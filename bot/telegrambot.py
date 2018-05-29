# Example code for telegrambot.py module
import json

import redis
from django.core.files import images
from django.utils import timezone

from datetime import timedelta

from shortuuid import ShortUUID
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove

from bot.apps import BotClient
from bot.forms import EngagementRuleForm
from bot.models import Message, Setup, News, Result
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler, \
    RegexHandler

from bot.utils import getIMember, MEDIA_CATEGORY
from django_telegrambot.apps import DjangoTelegramBot
from bot.lib import *
import logging
from django.utils.translation import ugettext_lazy as _

log = logging.getLogger(settings.PROJECT_NAME+".*")
log.setLevel(settings.DEBUG)

from bot.models import Member, Group, Message


CENTER_LINK = "https://t.me/joinchat/IcsVE0pDxquaijPb--338w"
CENTER_BOT = "https://telegram.me/{}?start".format(telegram.Bot(token=settings.DJANGO_TELEGRAMBOT['BOTS'][0]['TOKEN']).username)

BACK_KEY = 'back'

HOME_KEY = 'home'
HOME_VALUE = 'Home'

LINK_KEY, WALLET_KEY, RULES_KEY, GROUP_KEY, VERIFICATION_KEY, STATS_KEY = range(6)

LINK_VALUE = 'Link'
WALLET_VALUE = 'Wallet'
RULES_VALUE = 'Rules'
GROUP_VALUE = 'Group'
VERIFICATION_VALUE = 'Verification'
STATS_VALUE = 'Stats'

SUBSCRIBE = "Subscribe"
UNSUBSCRIBE = "Unsubscribe"


def help(bot, update):
    text = "The follow commands are available:\n"
    text += "/start (Establish Communication with the bot) \n"
    text += "/status (Check your subscription status ) \n"
    text += "/subscribe (Subscribe for news ) \n"
    text += "/unsubscribe (Unsubscribe for news ) \n"
    bot.sendMessage(update.message.chat_id, text=text)


def staff(bot, update):
    log.warning("Start.....")
    # from confusable_homoglyphs import categories, confusables
    # categories
    # confusables
    admins = bot.getChatAdministrators(chat_id=update.message.chat.id)
    for a in admins:
        u = a.user
        log.warning("{} {} @({}) - {}".format(u.first_name, u.last_name, u.username, a.status))
    # bot.sendMessage(update.message.chat_id, text="")


def status(bot, update):
    log.warning("-----------")
    member = Member.objects.filter(member_id=update.message.from_user.id).first()

    mark_up = telegram.ReplyKeyboardRemove()
    if member:
        if member.subscribed:
            msg = "Good News!!! Your subscription Status is Active. 😁😁😁 ".format(update.message.from_user.first_name)
            msg = "Hello {},\n\n{}\n\nType: {}{}\nStatus: Subscribed\n".format(update.message.from_user.first_name, msg, member.type, ("\nProgress: {}".format(member.level) if member.type==Member.EDITOR else ""))

        else:
            mark_up = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
            msg = "Hello {},\n\nUnfortunately!!! Your subscription Status is inactive.\nPlease use the button below to activate\n".format(update.message.from_user.first_name)
    else:
        msg = "Hello {}, \n\nI am not sure we have meet.\n\nPlease use /start to get started. \n\n".format(update.message.from_user.first_name)

    update.message.reply_text(msg, reply_markup=mark_up)
    return 0


def error(bot, update, error):
    pass
    try:
        bot.deleteMessage(chat_id=update.message.chat_id, message_id=update.message.message_id)
    except Exception as err:
        log.warning('Update "%s" caused error "%s"' % (update, error))


keyboard = [[SUBSCRIBE]]
unkeyboard = [[UNSUBSCRIBE]]


def start(bot, update, args=None):
    log.warning("-------Start------")
    setup = Setup.loadSetup(timeout=60*60*24)
    if setup is None:
        update.message.reply_text("Welcome to {} {}\n\n⚠️⚠️⚠️I am not yet setup please again later!!!".format(bot.first_name, bot.last_name),)
        return
    user = update.message.from_user

    log.warning(args)
    member = Member.objects.filter(member_id=user.id).first()
    if member and member.subscribed:
        msg = "Hello {}, you are most welcome!!!\n\n" \
              "I am excited to see you again, I trust you are enjoying our service. 😁😁😁 \n\n" \
              "To help us in serving you better, please always like/unlike our News".format(user.first_name)
    elif member:
        msg = "Hello {}, you are most welcome!!!\n\n" \
              "I am excited to see you again, unfortunately 😭😭😭 you are not currently Subscribed. \n\n" \
              "To help us in serving you better, please always like/unlike our News".format(user.first_name)
    else:
        member, created = Member.objects.get_or_create(member_id=user.id, defaults={'first_name': user.first_name,
                                                                                    'last_name': user.last_name,
                                                                                    'username': user.username,
                                                                                    'is_bot': user.is_bot,
                                                                                    'group_id': None,
                                                                                    'status': Member.ACTIVE})
        if created:
            msg = "Hello {}, you are most welcome!!!\n\n" \
                  "I am excited to meet you and will be happy to update you with most current and exciting news update\n\n" \
                  "Please click the button below to Subscribe 👇👇👇".format(user.first_name)
    mark_up = telegram.ReplyKeyboardRemove()
    if not member.subscribed:
        mark_up = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
    update.message.reply_text("{}\n/help (for more...)".format(msg), reply_markup=mark_up)
    return 0


def button(bot, update):
    log.warning("------IT IS HERE---:{}:---".format(update.callback_query.data))

    query = update.callback_query
    log.warning(query.data)
    member, crea = getMember(query.from_user)
    parts = query.data.split("-")
    if len(parts) == 3 and parts[0] == "n":
        news = News.objects.filter(id=parts[1]).first()
        if news:
            if parts[2] in ["0", "1"]:  # 0 = Unlike, 1 = Like
                result = Result.objects.filter(news=news, member=member).first()
                if result is None:
                    bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text="Please read the News 📄 first!!!")
                    return
                if member.type == Member.EDITOR:
                    if news.status != News.PENDING:
                        result.late = True
                elif member.type == Member.MEMBER:
                    log.warning("-------- {} ".format(news.status))
                    if news.status not in [News.ACCEPTED, News.SENT]:
                        result.late = True

                result.accepted = False if parts[2] == "0" else True
                result.save()
                url = "{}/news/{}/{}/".format(settings.THIS_URL, member.member_id, news.id)
                keyboard = [[InlineKeyboardButton("💫 News Update", url=url)]]
                bot.editMessageText(
                    message_id=update.callback_query.message.message_id,
                    chat_id=update.callback_query.message.chat.id,
                    text="Thanks for your feedback ({})\n\n{}\n{}".format(("👍" if result.accepted else "👎"), news.title, news.description),
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

                if member.type == Member.EDITOR:
                    results = Result.objects.filter(news=news, late=False, type=Member.EDITOR)
                    all_editors = Member.objects.filter(subscribed=True, type=Member.EDITOR).count()
                    all_votes = len(results)

                    if all_votes >= all_editors and news.status == News.PENDING:
                        setup = Setup.loadSetup()

                        if (all_votes * 100 / all_editors) < setup.participation_threshold_editor:
                            log.warning("{}--------- All Votes (E): {}, All Editor: {}, Participation Threshold: {}".format(News.DISCARDED, all_votes, all_editors, setup.participation_threshold_editor))
                            news.status = News.DISCARDED
                            news.save()
                        else:

                            for_votes = results.filter(accepted=True).count()
                            percent = for_votes * 100 / all_votes
                            if percent >= setup.review_threshold_editor:
                                subscribers = Member.objects.filter(type=Member.MEMBER, subscribed=True)
                                news.status = News.ACCEPTED
                                news.save()
                                try:
                                    for subs in subscribers:
                                        url = "{}/news/{}/{}/".format(settings.THIS_URL, subs.member_id, news.id)
                                        keyboard = [[InlineKeyboardButton("💫 News Update", url=url)],
                                                    [InlineKeyboardButton("👍 Like", callback_data="n-{}-1".format(news.id)),
                                                     InlineKeyboardButton("👎 Dislike", callback_data="n-{}-0".format(news.id)), ]]

                                        bot.sendMessage(chat_id=subs.member_id, text="{}\n{}".format(news.title, news.description),
                                                        disable_web_page_preview=False, reply_markup=InlineKeyboardMarkup(keyboard))

                                except Exception as err:
                                    log.error(err)
                                news.status = News.SENT
                                news.sent_time = timezone.now()

                            else:
                                news.status = News.REJECTED
                            news.save()

                            log.warning("{}-----2---- All Votes (E): {}, All Editor: {}, Participation Threshold: {}"
                                    .format(news.status, all_votes, all_editors,  setup.participation_threshold_editor))
                elif member.type == Member.MEMBER:
                    pass
                    # TODO: It might be too expensive to check if voting is completed for every vote

            elif parts[2] == "2":   #2 = Read
                log.warning("Creating Result: {}".format(member.type))
                result, created = Result.objects.get_or_create(news=news, member=member, type=member.type).first()
                if created:
                    if member.type == Member.EDITOR:
                        if news.status != News.PENDING:
                            result.late = True
                            result.save()
                    elif member.type == Member.MEMBER:
                        if news.status not in [News.ACCEPTED, News.SENT]:
                            result.late = True
                            result.save()
                    bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text="Please make sure to like/unlike")


def subscription(bot, update):
    log.warning("Subscription: {}".format(update.message.text))
    member, created = getMember(update.message.from_user)
    if update.message.text in ["Subscribe", "/subscribe"]:
        if member.subscribed:
            msg = "Hello {}, you are already subscribed, please stay turned as we feed you with the lastest updates".format(member.first_name)
        else:
            msg = "Hello {}, you have been successfully subscribed, please stay turned as we feed you with the lastest updates".format(member.first_name)
            member.subscribed = True
            member.save()
    elif update.message.text in ["Unsubscribe", "/unsubscribe"]:
        if member.subscribed:
            member.subscribed = False
            member.save()
            msg = "Hello {}, you have been successfully unsubscribed".format(member.first_name)
        else:
            msg = "Hello {}, you are not currently subscribed".format(member.first_name)

    reply_markup = ReplyKeyboardRemove()
    if not member.subscribed:
        reply_markup =ReplyKeyboardMarkup(keyboard=[["Subscribe"]])
    bot.sendMessage(chat_id=update.message.chat.id, text=msg, reply_markup=reply_markup, )


def editMessage(bot, query, text, keyboard):
        bot.editMessageText(
            text=text,
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


def cancel(bot, update):
    log.info("User %s canceled the conversation.", update.message.from_user.first_name)
    # update.message.reply_text('Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END



button_handler = RegexHandler('^(Subscribe|Unsubscribe)$', subscription)


def main():
    log.warning("......Loading handlers for telegram bot")

    # Default dispatcher (this is related to the first bot in settings.DJANGO_TELEGRAMBOT['BOTS'])
    # dp = DjangoTelegramBot.dispatcher
    # To get Dispatcher related to a specific bot
    # dp = DjangoTelegramBot.getDispatcher('BOT_n_token')     #get by bot token
    dp = DjangoTelegramBot.getDispatcher('NewPublisherBot')  #get by bot username

    # on different commands - answer in Telegram
    # dp.add_handler(CommandHandler("wallet", wallet, pass_args=True))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("subscribe", subscription))
    dp.add_handler(CommandHandler("unsubscribe", subscription))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(button_handler)

    dp.add_handler(CallbackQueryHandler(button))

    # From libs
    # dp.add_handler(CommandHandler(GROUP[1:], group, pass_args=True))

    # dp.add_handler(CommandHandler(RESTRICT[1:], restrictUser, pass_args=True))
    # dp.add_handler(CommandHandler(BAN[1:], banUser, pass_args=True))
    # dp.add_handler(CommandHandler(UNBAN[1:], unbanUser, pass_args=True))

    # dp.add_handler(CommandHandler(TEST_COMMAND[1:], test_command, pass_args=True))

    # ConversationHandler()
    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler([Filters.text], echo))
    # dp.add_handler(MessageHandler([], in_out))

    # Filters.successful_payment
    # dp.add_handler(MessageHandler([], create_member))
    # dp.add_handler(MessageHandler([], test_msg))

    # log all errors
    dp.add_error_handler(error)