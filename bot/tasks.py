from __future__ import absolute_import, unicode_literals


# log = get_task_logger(__name__)
import json
import logging

import os
import re
import urllib

import feedparser
import redis
from datetime import timedelta, datetime

from PIL import Image
from confusable_homoglyphs import confusables
from django.core.cache import cache
from django.db.models import F
from django.utils import timezone
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest

from bot.utils import loadAdmins
from celery import shared_task
from django.conf import settings
from django.db import IntegrityError

import telegram
from bot.models import Member, NewsSource, News, Setup

log = logging.getLogger("tmessage.*")
log.setLevel(False)


@shared_task(name='bot.createMember')
def createMember(mid, username, first_name, last_name=None, type=Member.MEMBER):
    try:
        Member.objects.get_or_create(member_id=mid, first_name=first_name, last_name=last_name, username=username, type=type)
    except IntegrityError as err:
        log.error(err)
        log.error("Error saving.... Member_id: {}, Username: {}, First Name: {}, Last Name: {}".format(mid, username, first_name, last_name))


@shared_task(name='bot.newsFeedCheck')
def news_feed_check(is_test=False):
    sources = NewsSource.objects.filter(enabled=True)
    url_reg = r'[a-z]*[:.]+\S+'

    # log.warning("Sources: {}".format(len(sources)))
    for s in sources:
        try:

            d = feedparser.parse(s.source)
            # log.warning("Sources: {}".format(len(s.source)))

            src_time = datetime.strptime(d.updated, "%a, %d %b %Y %H:%M:%S %Z")
            if src_time == s.latest and not is_test:
                log.warning("Skipping: {} == {} == {}".format(src_time, s.latest, src_time == s.latest))
                continue

            x = 0
            s.latest = src_time
            s.save()
            for u in d.entries:
                x += 1
                if x > 3:
                    break
                # time = datetime.strptime('Thu, 17 May 2018 13:58:46 +0200', "%a, %d %b %Y %H:%M:%S %z")
                news, created = News.objects.get_or_create(title=u.title, description=u.summary, source=s, url=u.id,
                                                           src_time=datetime.strptime(u.published, "%a, %d %b %Y %H:%M:%S %z"))

                if created or is_test:
                    editors = Member.objects.filter(subscribed=True, type=Member.EDITOR)
                    bot = telegram.Bot(token=settings.DJANGO_TELEGRAMBOT['BOTS'][0]['TOKEN'])
                    for ed in editors:
                        url = "{}/news/{}/{}/".format(settings.THIS_URL, ed.member_id, news.id)
                        log.warning(url)
                        keyboard = [[InlineKeyboardButton("💫 News Update", url=url)],
                                    [InlineKeyboardButton("👍 Like", callback_data="n-{}-1".format(news.id)),
                                     InlineKeyboardButton("👎 Dislike", callback_data="n-{}-0".format(news.id)), ]]

                        bot.sendMessage(chat_id=ed.member_id, text="{}\n{}\n".format(news.title, news.description),
                                        disable_web_page_preview=False, reply_markup=InlineKeyboardMarkup(keyboard))
                else:
                    break
        except Exception as err:
            log.error(err)


@shared_task(name='bot.processNewsVote')
def process_news(news=[]):
    if len(news) == 0:
        setup = Setup.loadSetup()
        news = News.objects.filter(status__in=[News.PENDING, News.ACCEPTED, News.SENT], ).order_by('created')

    for n in news:

        try:
            if setup:
                if n.status in [News.ACCEPTED, News.PENDING]:
                    log.warning("Status ---- Accepted/Pending")
                    if n.created + timedelta(minutes=setup.max_review_time_editor) <= timezone.now():
                        log.warning("Running from Task -----")
                        all_editors = Member.objects.filter(type=Member.EDITOR, subscribed=True).count()
                        results = n.result_set.all().filter(member__type=Member.EDITOR, late=False)
                        all_votes = len(results)

                        if (all_votes * 100/all_editors) < setup.participation_threshold_editor:
                            n.status = News.DISCARDED
                            n.save()
                            continue

                        for_votes = results.filter(accepted=True).count()
                        percent = for_votes * 100/all_votes
                        if percent >= setup.review_threshold_editor:
                            subscribers = Member.objects.filter(type=Member.MEMBER, subscribed=True)
                            bot = telegram.Bot(token=settings.DJANGO_TELEGRAMBOT['BOTS'][0]['TOKEN'])
                            n.status = News.ACCEPTED
                            n.save()
                            try:
                                for subs in subscribers:
                                    url = "{}/news/{}/{}/".format(settings.THIS_URL, subs.member_id, n.id)
                                    keyboard = [[InlineKeyboardButton("💫 News Update", url=url)],
                                                [InlineKeyboardButton("👍 Like", callback_data="n-{}-1".format(n.id)),
                                                 InlineKeyboardButton("👎 Dislike", callback_data="n-{}-0".format(n.id))]]

                                    bot.sendMessage(chat_id=subs.member_id, text="{}\n{}\n".format(n.title, n.description),
                                                    disable_web_page_preview=False, reply_markup=InlineKeyboardMarkup(keyboard))

                            except Exception as err:
                                log.error(err)
                            n.status = News.SENT
                            n.sent_time = timezone.now()
                            n.save()

                        else:
                            n.status = News.REJECTED
                            n.save()
                elif n.status in [News.SENT]:
                    log.warning("Status ---- SENT")
                    if n.sent_time + timedelta(minutes=setup.max_review_time_user) <= timezone.now():
                        subscribers = Member.objects.filter(type=Member.MEMBER, subscribed=True).count()
                        results = n.result_set.all().filter(member__type=Member.MEMBER, late=False)
                        all_votes = len(results)

                        if (all_votes * 100/subscribers) < setup.participation_threshold_user:
                            n.status = News.NOT_SCORED
                            n.save()
                            continue

                        for_votes = results.filter(accepted=True).count()
                        percent = for_votes * 100 / all_votes

                        win = percent >= setup.review_threshold_user
                        if win:
                            Member.objects.filter(id__in=n.result_set.all().filter(type=Member.EDITOR, accepted=True).values_list('member__id', flat=True)).update(point=F('point')+setup.positive_reward_point)
                            Member.objects.filter(id__in=n.result_set.all().filter(type=Member.EDITOR, accepted=False).values_list('member__id', flat=True)).update(point=F('point')-setup.negative_reward_point)
                        else:
                            Member.objects.filter(id__in=n.result_set.all().filter(type=Member.EDITOR, accepted=True).values_list('member__id', flat=True)).update(point=F('point')-setup.negative_reward_point)
                            Member.objects.filter(id__in=n.result_set.all().filter(type=Member.EDITOR, accepted=False).values_list('member__id', flat=True)).update(point=F('point')+setup.positive_reward_point)

                        n.status = News.SCORED
                        n.score_time = timezone.now()
                        n.save()
                        bot = telegram.Bot(token=settings.DJANGO_TELEGRAMBOT['BOTS'][0]['TOKEN'])

                        for r in n.result_set.all().filter(type=Member.EDITOR, accepted=win):
                            bot.sendMessage(chat_id=r.member.member_id, disable_web_page_preview=False, reply_markup=None,
                                            text="Congratulations {}, you've earned {} points\n\nRef: {}".format(r.member.first_name, setup.positive_reward_point, n.url))
            else:
                log.warning("SET-UP NONE......")
        except Exception as err:
            log.error(err)

