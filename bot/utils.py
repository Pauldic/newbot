import logging

import unicodedata
import urllib
from datetime import timedelta, datetime, time

from decimal import Decimal

import os
from time import sleep

import pytz
import subprocess

import re

import redis

import telegram, json
from django.conf import settings
from django.core import mail
from django.db import IntegrityError
from django.db.models.base import ModelState
from django.utils import timezone
from telethon import TelegramClient
from telethon.errors import ChatAdminRequiredError
from telethon.tl.functions.channels import InviteToChannelRequest, EditBannedRequest, GetParticipantsRequest, \
    JoinChannelRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import UpdateShortMessage, UpdateNewChannelMessage, PeerChannel, PeerUser, ChannelBannedRights, \
    ChannelParticipantsSearch, Channel, ChannelParticipantAdmin, ChannelParticipantCreator, InputPeerEmpty, \
    InputPeerChannel

from bot.custom_exception import MissingConnectionException, InvalidClient

log = logging.getLogger("tmessage.*")
log.setLevel(False)


G_TEXT = "Text"
G_CONTACT = "Text"
G_LOCATION = "Text"
G_VENUE = "Text"
G_URL = "Text"

G_STICKER = "Photo"
G_PHOTO = "Photo"
G_ANIMATION = "Photo"

G_AUDIO = "Audio"
G_AUDIO_NOTE = "Audio"

G_VIDEO = "Video"
G_VIDEO_NOTE = "Video"

G_DOCUMENT = "Others"
G_GAME = "Others"


TEXT = "Text"
CONTACT = "Contact"
LOCATION = "Location"
VENUE = "Venue"
URL = "Url"

STICKER = "Sticker"
PHOTO = "Photo"
ANIMATION = "Animation"

AUDIO = "Audio"
AUDIO_NOTE = "Audio Note"

VIDEO = "Video"
VIDEO_NOTE = "Video Note"

DOCUMENT = "Document"
GAME = "Game"
OTHERS = "Others"

TEXT_GROUP = [TEXT, CONTACT, LOCATION, VENUE, URL]
PHOTO_GROUP = [STICKER, PHOTO, ANIMATION]
AUDIO_GROUP = [AUDIO, AUDIO_NOTE]
VIDEO_GROUP = [VIDEO, VIDEO_NOTE]
OTHER_GROUP = [DOCUMENT, GAME]

MEDIA_CATEGORY = [(G_TEXT, G_TEXT), (G_PHOTO, G_PHOTO), (G_AUDIO, G_AUDIO), (G_VIDEO, G_VIDEO), (G_DOCUMENT, G_DOCUMENT)]

MEDIAS = [TEXT, CONTACT, LOCATION, VENUE, URL, STICKER, PHOTO, ANIMATION, AUDIO, AUDIO_NOTE, VIDEO, VIDEO_NOTE, DOCUMENT, GAME]



def get_connection(label='default', **kwargs):

    try:
        connections = getattr(settings, 'EMAIL_CONNECTIONS')
        options = connections[label]
    except (KeyError, AttributeError) as e:
        options = []
        raise MissingConnectionException('Settings for connection "%s" were not found' % label)

    options.update(kwargs)
    return mail.get_connection(**options)


def get_receivers():
    recipients = [('Paul Okeke', 'pauldiconline@gmail.com'), ('Benfdela', 'Prowebmedia2@gmail.com')]
    return recipients


def callback(update):
    log.warning('I received:  ', update)


# for client in TeleClient.clients:
    # client.add_update_handler(callback)
    # client.add_update_handler(callback)


def ser(obj, model_instance):
    for k, v in vars(obj).items():
        print(k)
        model_instance

    klass = globals()["class_name"]
    instance = klass()


def get_seconds(n, time):
    n = int(n)
    if time in ['sec', 'secs']:
        return n
    elif time in ['min', 'mins']:
        return n * 60
    elif time in ['hour', 'hours']:
        return n * 60 * 60
    elif time in ['day', 'days']:
        return n * 24 * 60 * 60


def serialize(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    if isinstance(obj, time):
        serial = obj.isoformat()
        return serial
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, ModelState):
        return "---"



# tt ="#CRYPTOLIONSOFFICIALLS [ðŸ”24] (+344%) Win/Loses/Open: 78/63/2 WinRate: 55% Average signal ~6hours 29minðŸ”µ #ZEN ðŸ”µSell 0.00400000 11.11% Buy  0.00360000 Now  0.00361196 0.33% (@ Bittrex)Stop 0.00330000 8.33% ðŸ’¬ Original signal quote: Buy Some #ZEN now at 0.00360000. Sell : 0.00400000-0.00430000-0.00460000 Take stoploss at 0.00330000"
# tt="âœ… #TEST [ðŸ”27] #BLOCK âœ… Target +12.41%  in ~1hours 45min"
#
# "#CRYPTOLIONSOFFICIALLS [ðŸ”24] (+344%)
# Win/Loses/Open: 78/63/2
# WinRate: 55% Average signal ~6hours 29min
#
# ðŸ”µ #ZEN ðŸ”µ
# Sell 0.00400000 11.11%
# Buy  0.00360000
# Now  0.00361196 0.33% (@ Bittrex)
# Stop 0.00330000 8.33%
#
# ðŸ’¬ Original signal quote:
# Buy Some #ZEN now at 0.00360000.
# Sell :
# 0.00400000-0.00430000-0.00460000
#
# Take stoploss at 0.00330000



def getMember(bot_user, group_id=None):
    from bot.models import Member
    try:
        member_id = bot_user.id
    except (KeyError, AttributeError):
        return getMemberByDict(bot_user, group_id=group_id)
    first_name = bot_user.first_name
    is_bot = bot_user.is_bot

    try:
        last_name = bot_user.last_name
    except (KeyError, AttributeError):
        last_name = None
    try:
        username = bot_user.username
    except (KeyError, AttributeError):
        username = None
    try:
        language_code = bot_user.language_code
    except (KeyError, AttributeError):
        language_code = None

    defaults = {'first_name': first_name, 'last_name': last_name, 'username': username, 'language_code': language_code, 'is_bot': is_bot, 'group_id': group_id}
    # log.warning(defaults)
    if group_id:
        try:
            member = Member.objects.get(member_id=member_id,  group_id=group_id)
        except Exception as err:
            member = Member.objects.filter(member_id=member_id).first()
    else:
        member = Member.objects.filter(member_id=member_id).first()

    log.warning("----Got here 1 *****::: Member Id: {} || {}, Group: {} ".format(member.member_id, member_id, group_id))
    return Member.objects.get_or_create(member_id=member_id,  defaults=defaults)


def getMemberByDict(bot_user, group_id=None):
    from bot.models import Member
    member_id = bot_user['id']
    first_name = bot_user['first_name']
    is_bot = bot_user['is_bot']
    try:
        last_name = bot_user['last_name']
    except (KeyError, AttributeError):
        last_name = None
    try:
        username = bot_user['username']
    except (KeyError, AttributeError):
        username = None
    try:
        language_code = bot_user['language_code']
    except (KeyError, AttributeError):
        language_code = None

    # log.warning(defaults)
    if group_id:
        try:
            member = Member.objects.get(member_id=member_id,  group_id=group_id)
        except Exception as err:
            member = Member.objects.filter(member_id=member_id).first()
    else:
        member = Member.objects.filter(member_id=member_id).first()
    defaults = {'first_name': first_name, 'last_name': last_name, 'username': username, 'language_code': language_code,
                'is_bot': is_bot, 'group_id': member.group.id if member and member.group else group_id}

    log.warning("----Got here 2")
    return Member.objects.get_or_create(member_id=member_id,  defaults=defaults)
    # return Member.objects.update_or_create(member_id=member_id, first_name=first_name, last_name=last_name, username=username, language_code=language_code, is_bot=is_bot, group_id=group_id)


def getIMember(i_user):
    from bot.models import Member
    try:
        member_id = i_user.pk
    except (KeyError, AttributeError):
        return getIMemberByDict(i_user)

    if len(i_user.full_name) > 0:
        full = i_user.full_name.split(" ")
        first_name = full.pop(0)
        last_name = " ".join(full)
    try:
        username = i_user.username
    except (KeyError, AttributeError):
        username = None

    return Member.objects.update_or_create(member_id=member_id, first_name=first_name, last_name=last_name, username=username, is_bot=False, type=Member.INSTAGRAM)


def getIMemberByDict(i_user):
    from bot.models import Member

    member_id = i_user['pk']

    if len(i_user['full_name']) > 0:
        full = i_user['full_name'].split(" ")
        first_name = full.pop(0)
        last_name = " ".join(full)
    else:
        first_name = last_name = ""
    try:
        username = i_user['username']
    except (KeyError, AttributeError):
        username = None

    try:
        return Member.objects.update_or_create(member_id=member_id, first_name=first_name, last_name=last_name, username=username, is_bot=False, type=Member.INSTAGRAM)
    except Exception as err:
        log.error(err)


def getGroup(chat):
    from bot.models import Group
    return Group.objects.update_or_create(id=chat.id, title=chat.title, username=chat.username, type=chat.type)


DEFAULT_CHANNEL = 1153647546
# DEFAULT_CHANNEL = 1188959006    #My Test


def loadAdmins(admins):
    users = []
    for au in admins:
        users.append(au.user)
    return users


def decimal_normalise(f):
    d = Decimal(str(f));
    return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()


def all_dialog(client):
    dialogs = []
    users = []
    chats = []
    last_date = None
    chunk_size = 200
    block = 1
    sleep_counter = 0
    while True:
        result = client(GetDialogsRequest(offset_date=last_date, offset_id=0, offset_peer=InputPeerEmpty(), limit=chunk_size))
        dialogs.extend(result.dialogs)
        users.extend(result.users)
        chats.extend(result.chats)
        log.warning("Block: {},    Count: {},   Users: {},  Dialog: {},  Chat: {}".format(block, len(result.messages), len(result.users), len(result.dialogs), len(result.chats)))
        block += 1
        sleep_counter += 1
        if not result.messages:
            break
        last_date = min(msg.date for msg in result.messages)
        if sleep_counter > 4:
            sleep(1)
            sleep_counter = 0
    return {"dialogs": dialogs, "users": users, "chats": chats}


# def get_all_channel_members(client, channels, batch_id=None):
#     all_participants = []
#     all_admins = []
#
#     offset = 0
#     limit = 100
#     block = 1
#     print("\n\n********Preparing Group {} ({}) for Scraping".format(channel.title, channel.id))
#     while True:
#         try:
#             participants = client(GetParticipantsRequest(channel, ChannelParticipantsSearch(''), offset, limit, 0))
#             print("Block: {},  Capacity: {},   Count: {},   All: {}, Offset: {}".format(block, participants.count, len(participants.users), len(all_participants), offset))
#             block += 1
#             if not participants.users:
#                 break
#             all_participants.extend(participants.users)
#             for p in participants.participants:
#                 if isinstance(p, ChannelParticipantAdmin):
#                     all_admins.append(p)
#             offset += len(participants.users)
#         except ChatAdminRequiredError as err:
#             offset += 1
#             print(err)
#             print(channel.stringify())
#             print("\n")
#         sleep(1)
#     return all_participants, all_admins


def get_all_channel_members(client, channels, batch_id=None, skip_admins=False, aggressive=False):
    q = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '`', '~',
         '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '[', '{', '}', ']', '|', ':', ';', '"', ',', '<', '.', '>', '/', '?']

    from bot.models import Group, Member
    all_participants_by_group = []
    log.warning(len(channels))
    for channel in channels:
        all_participants = []
        all_admins = []
        if not isinstance(channel, Channel):
            continue
        count = client.get_participants(channel, 0).total
        log.warning("\n\n********Preparing Group '{} ({})' with {} members for Scraping {}".format(channel.title, channel.id, count, ("Aggressively" if count > 10000 and aggressive else "")))

        if count > 10000 and aggressive:
            usernames = set()
            for x in q:
                offset = 0
                limit = 100
                block = 1
                while True:
                    try:
                        participants = client(GetParticipantsRequest(channel, ChannelParticipantsSearch(x), offset, limit, 0))
                        log.warning("{}:  Block: {},  Capacity: {},   Count: {},   All: {}, Offset: {}".format(x, block, count, len(usernames), len(all_participants), offset))
                        block += 1
                        if not participants.users:
                            break
                        all_participants.extend(participants.users)
                        for user in participants.users:
                            usernames.add(user.username)
                        for p in participants.participants:
                            if isinstance(p, ChannelParticipantAdmin) or isinstance(p, ChannelParticipantCreator):
                                all_admins.append(p)

                        if len(usernames) >= count:
                            break
                        offset += len(participants.users)
                    except ChatAdminRequiredError as err:
                        offset += 1
                        log.warning(err)
                        log.warning(channel.stringify())
                    sleep(1)
                if len(usernames) >= count:
                    break

                admins = set()
                for admin in all_admins:
                    admins.add(TAdminMember(admin.__dict__, group=channel))

                members = set()
                for user in all_participants:
                    members.add(TMember(user.__dict__, admins=admins, group=channel))
                all_participants_by_group.append({'group': channel, 'members': members, 'admins': admins})
        else:
            offset = 0
            limit = 100
            block = 1
            while True:
                try:
                    participants = client(GetParticipantsRequest(channel, ChannelParticipantsSearch(''), offset, limit, 0))
                    log.warning("Block: {},  Capacity: {},   Count: {},   All: {}, Offset: {}".format(block, count, len(participants.users), len(all_participants), offset))

                    block += 1
                    if not participants.users:
                        break
                    all_participants.extend(participants.users)
                    for p in participants.participants:
                        if isinstance(p, ChannelParticipantAdmin) or isinstance(p, ChannelParticipantCreator):
                            all_admins.append(p)

                    offset += len(participants.users)
                except (TypeError, ChatAdminRequiredError) as err:
                    offset += 1
                    log.error(err)
                    log.error(channel.stringify())
                sleep(1)

            admins = set()
            for admin in all_admins:
                admins.add(TAdminMember(admin.__dict__, group=channel))

            members = set()
            for user in all_participants:
                members.add(TMember(user.__dict__, admins=admins, group=channel))
            all_participants_by_group.append({'group': channel, 'members': members, 'admins': admins})

    for a in all_participants_by_group:
        g = a['group']
        type = "Group"
        group = Group.objects.filter(id=g.id).first()
        if group is None:
            group = Group.objects.create(id=g.id, title=g.title, username=g.username, type=type, )
        for m in a['members']:
            try:
                Member.objects.create(member_id=m.id, first_name=m.first_name or "", last_name=m.last_name, username=m.username, type=Member.TELEGRAM, group=group, is_bot=m.bot, is_admin=m.is_admin, batch_id=batch_id)
            except IntegrityError as err:
                pass
    return all_participants_by_group


def filter_duplicate(client, link, tid):
    from bot.models import Member
    return Member.objects.filter(taskadddetail__task__id=tid, username__in=scrap_usernames(client=client, link=link)).delete()


def scrap_usernames(client, link, aggressive=True):
    q = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '`', '~',
         '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '[', '{', '}', ']', '|', ':', ';', '"', ',', '<', '.', '>', '/', '?']

    channel = client.get_entity(link)

    all_usernames = set()
    if not isinstance(channel, Channel):
        raise Exception("Invalid Channel link/username provided")

    count = client.get_participants(channel, 0).total
    log.warning("\n\n********Preparing Group '{} ({})' with {} members for Scraping {}".format(channel.title, channel.id, count, ("Aggressively" if count > 10000 and aggressive else "")))

    if count > 10000 and aggressive:
        for x in q:
            offset = 0
            limit = 100
            block = 1
            while True:
                try:
                    participants = client(GetParticipantsRequest(channel, ChannelParticipantsSearch(x), offset, limit, 0))
                    log.warning("{}:  Block: {},  Capacity: {},   Count: {},   All: {}, Offset: {}".format(x, block, participants.count, len(participants.users), len(all_usernames), offset))
                    block += 1
                    if not participants.users:
                        break
                    for u in participants.users:
                        all_usernames.add(u.username)

                    offset += len(participants.users)
                except ChatAdminRequiredError as err:
                    offset += 1
                    log.warning(err)
                    log.warning(channel.stringify())
                sleep(1)
    else:
        offset = 0
        limit = 100
        block = 1
        while True:
            try:
                participants = client(GetParticipantsRequest(channel, ChannelParticipantsSearch(''), offset, limit, 0))
                log.warning("Block: {},  Capacity: {},   Count: {},   All: {}, Offset: {}".format(block, count, len(participants.users), len(all_usernames), offset))

                block += 1
                if not participants.users:
                    break
                for u in participants.users:
                    all_usernames.add(u.username)

                offset += len(participants.users)
            except (TypeError, ChatAdminRequiredError) as err:
                offset += 1
                log.error(err)
                log.error(channel.stringify())
            sleep(1)

    return all_usernames

def enter_groups(client, c_usernames):
    for c in c_usernames:
        input_channel = client.get_input_entity(c)
        print(input_channel)
        if isinstance(input_channel, InputPeerChannel):
            result = client(JoinChannelRequest(input_channel))
            print(result)


def leave_group(client, channel_id=None):
    dialog = all_dialog(client)
    chats = dialog['chats']


def removeUser(client, username, channel_id=DEFAULT_CHANNEL):
    try:
        msg = removeUser_by_user(client, user=client(ResolveUsernameRequest(username)).users[0], channel_id=channel_id)
    except Exception as err:
        msg = "Attempt to kicked user @{}  from channel ({}) failed. Confirm the username is valid".format(username, channel_id)
        log.error(msg)
        log.error(err)
    return msg


def removeUser_by_user(client, user, channel_id=DEFAULT_CHANNEL):
    msg = ""
    try:
        until = datetime(2040, 12, 25)
        rights = ChannelBannedRights(until, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, embed_links=True)

        channel_entity = client.get_input_entity(PeerChannel(channel_id=int(channel_id)))
        client(EditBannedRequest(channel_entity, client.get_input_entity(PeerUser(user_id=user.id)), banned_rights=rights))
        msg = 'Kicked User: {} from Channel ({})'.format(user.first_name, channel_id)
        log.warning(msg)
    except Exception as err:
        reason = err.args[1] if len(err.args) > 1 else err.message
        msg = "Attempt to kick User: {} from Channle ({}) failed [{}]".format(user.first_name, channel_id, reason)
        log.error(msg)
        log.error(err)
    return msg


def sendMsg(client, msg, channel_id=DEFAULT_CHANNEL):
    channel_entity = client.get_entity(PeerChannel(channel_id=int(channel_id)))
    client.send_message(entity=channel_entity, message=msg, reply_to=None, parse_mode=None, link_preview=True)


def addUser(client, username, channel_id=DEFAULT_CHANNEL):
    try:
        user = client(ResolveUsernameRequest(username))
        return add_user_by_id(client, user_id=user.users[0].id, channel_id=channel_id)
    except Exception as err:
        msg = "Add User @{} attempt to channel ({}) failed. Confirm the username is valid".format(username, channel_id)
        log.error(msg)
        log.error(err)
        return msg


def add_user_by_id(client, user_id, channel_id=DEFAULT_CHANNEL):
    try:

        # client.invoke(InviteToChannelRequest(get_input_peer(channel), [get_input_peer(user)]))

        # client.invoke(InviteToChannelRequest(
        #     # InputChannel(get_input_peer(user.chats[0]).channel_id, get_input_peer(user.chats[0]).access_hash),
        #     InputChannel(channel.id, channel.access_hash),
        #     [InputUser(get_input_peer(user.users[0]).user_id, get_input_peer(user.users[0]).access_hash)]
        # ))
        # client.invoke(InviteToChannelRequest(InputChannel(channel.id, channel.access_hash), [InputUser(get_input_peer(user.users[0]).user_id, get_input_peer(user.users[0]).access_hash)]))
        # client.invoke(InviteToChannelRequest(client.get_entity(PeerChannel(1188959006)), [user]))
        # client.invoke(InviteToChannelRequest(client.get_input_entity(PeerChannel(channel_id)), [client.get_input_entity(PeerUser(user_id=user.users[0].id))]))

        user_entity = client.get_input_entity(PeerUser(user_id))
        channel_entity = client.get_entity(PeerChannel(channel_id=int(channel_id)))
        client.invoke(InviteToChannelRequest(channel_entity, [user_entity]))

        log.warning("Added User: {} to Channel: {}".format(user_id, channel_id))
        return "User added successfully"
    except Exception as err:
        reason = err.args[1] if len(err.args) > 1 else err.message
        msg = "Add User {} attempt to channel ({}) failed [{}]".format(user_id, channel_id, reason)
        log.error(msg)
        log.error(err)
    return msg


class TeleClient():
    id = 0
    allowedGroups = []
    clients = []
    client_objs = []
    default_api_id = 0

    # TARGET_CHANNELS = [1131704561, 1350457716, 1124723913, 1228129346, ]
    # TARGET_CHANNELS = [1158028079]
    TARGET_CHANNELS = []
    TARGET_GROUPS = []
    TARGET_PRIVATE = []

    ALLOWED_GROUP_IDS = []
    TARGET_CHANNELS_IDS = []
    TARGET_GROUPS_IDS = []
    TARGET_PRIVATE_IDS = []

    # FORWARD_TO = [1375066736]
    FORWARD_TO = []

    PUSH_2_MAIL = False
    PUSH_2_DB = False
    ANALYSE = False

    # If you already have a previous 'session_name.session' file, skip this.
    # client.sign_in(phone=None, code=None, password=None, bot_token=None, phone_code_hash=None)
    # client.send_code_request(phone, force_sms=False)
    # client.sign_in(phone=settings.CLIENT[0].PHONE)

    @classmethod
    def get_config(cls, type_, ids_only=False):
        from bot.models import Config
        if type_ == Config.TARGET_GROUPS:
            if len(cls.TARGET_GROUPS) == 0:
                cls.TARGET_GROUPS = Config.objects.filter(type=type_)
                cls.TARGET_GROUPS_IDS = cls.TARGET_GROUPS.values_list("entity_id", flat=True)
            return cls.TARGET_GROUPS_IDS if ids_only else cls.TARGET_GROUPS

        elif type_ == Config.TARGET_PRIVATE:
            if len(cls.TARGET_PRIVATE) == 0:
                cls.TARGET_PRIVATE = Config.objects.filter(type=type_)
                cls.TARGET_PRIVATE_IDS = cls.TARGET_PRIVATE.values_list("entity_id", flat=True)
            return cls.TARGET_PRIVATE_IDS if ids_only else cls.TARGET_PRIVATE

        elif type_ == Config.TARGET_CHANNELS:
            if len(cls.TARGET_CHANNELS) == 0:
                cls.TARGET_CHANNELS = Config.objects.filter(type=type_)
                cls.TARGET_CHANNELS_IDS = cls.TARGET_CHANNELS.values_list("entity_id", flat=True)

            return cls.TARGET_CHANNELS_IDS if ids_only else cls.TARGET_CHANNELS

        elif type_ == Config.FORWARD_TO:
            if len(cls.FORWARD_TO) == 0:
                cls.FORWARD_TO = Config.objects.filter(type=type_)
                cls.FORWARD_TO_IDS = cls.FORWARD_TO.values_list("entity_id", flat=True)
            return cls.FORWARD_TO_IDS if ids_only else cls.FORWARD_TO
        else:
            return []

    @classmethod
    def clear_clients(cls):
        for c in cls.clients:
            pass
        cls.clients = cls.client_objs = []

    @classmethod
    def get_clients(cls, is_tele_client=True):
        from bot.models import Client
        if is_tele_client:
            if len(cls.clients) == 0:
                cls.client_objs = Client.objects.filter(enabled=True)
                log.warning("******** - Initializing Telegram Clients - ***************")
                for c in cls.client_objs:
                    cc = TelegramClient(session=c.phone, api_id=c.api_id, api_hash=c.access_hash, update_workers=1, spawn_read_thread=False)
                    # cc.for_id = c
                    if cc.connect():
                        cls.clients.append(cc)
                        log.warning("Adding Telegram client list..... {}".format(c.phone))

                # try:
                #     for cc in cls.clients:
                #         if cc.connect():
                #             if cc.is_user_authorized():
                #                 me = cc.get_me()
                #                 Client.objects.filter(api_id=cc.api_id, phone=cc.session.filename.split('.session', 1)[0]).update(
                #                     **{'first_name': me.first_name, 'last_name': me.last_name, 'username': me.username})
                #
                # except Exception as err:
                #     log.error(err)
                # updateClients.apply_async()
            return cls.clients
        else:
            if len(cls.client_objs) == 0:
                cls.client_objs = Client.objects.filter(enabled=True)
            return cls.client_objs

    def get_client_(self, id):
        for client in TeleClient.get_clients():
            if client.api_id == id:
                return client
        return None

    def set_id(self, id):
        self.id = id

    # @classmethod
    # def get_phone(cls, api_id):
    #     api_id = str(api_id)
    #     for c in cls.get_clients(is_tele_client=False):
    #         if api_id == c.id:
    #             return c.phone
    #     return None

    @classmethod
    def get_api_id(cls, phone):
        for c in cls.get_clients(is_tele_client=False):
            if phone == c.phone:
                return c.id
        return None

    @classmethod
    def get_title(cls, phone=None):
        for c in cls.get_clients(is_tele_client=False):
            if phone == c.phone:
                return "{} {}".format(c.first_name, ("" if c.last_name is None else c.last_name))
        return None

    @classmethod
    def get_client(cls, phone=None):
        # log.warning(phone)
        if phone:
            log.warning("Getting '{}' client from '{}' clients".format(phone, len(cls.get_clients())))
            for c in cls.get_clients():
                if c.session.filename.split('.session')[0] == str(phone).strip():
                    return c
            log.warning("{}: NOT Found ****************".format(phone))
        else:
            for c in cls.get_clients():
                if c:
                    status = c.connect()
                    if status:
                        status = c.is_user_authorized()
                        if status:
                            return c
        return None

    @classmethod
    def get_client_obj(cls, client):
        from bot.models import  Client
        return Client.objects.filter(phone=client.session.filename.split('.session')[0]).first()


    @classmethod
    def logout(cls, phone):
        client = cls.get_client(phone)

        if client:
            for handler in client.list_update_handlers():
                client.remove_update_handler(handler)
            client.disconnect()
            return client.log_out()
            # try:
            #     BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            #     os.remove(os.path.join(BASE_DIR, "{}.session".format(phone)))
            # except:
            #     return False
            # return True
        else:
            return False

    @classmethod
    def login(cls, phone, code):
        from bot.models import TelegramUser, Client
        client = cls.get_client(phone)
        if not client or not client.connect():
            raise InvalidClient()
        me = client.sign_in(code=code)
        Client.objects.filter(phone=client.session.filename.split('.session', 1)[0]).update(**{'first_name': me.first_name, 'last_name': me.last_name, 'username': me.username})
        log.error("Sign Successful......")
        # except ValueError as err:
        #     log.error(err)
        #     return False
        # except PhoneCodeInvalidError as err:
        #     log.error(err)
        #     PhoneCodeInvalidError
        #     raise PhoneCodeInvalidError()
        # except PhoneNumberUnoccupiedError as err:
        #     log.error(err)
        #     raise PhoneNumberUnoccupiedError()
        if me and cls.is_accessible(phone):
            tu = TelegramUser()
            tu = tu.tele_2_app(me)
            # tu.save()
            return True
        return False

    @classmethod
    def login_request(cls, phone):
        client = cls.get_client(phone)
        if client and client.connect() and client.is_user_authorized():
            return True
        # elif client is None:
        #     cls.client_objs
        # try:
        #     sent_code = client.send_code_request("+{}".format(phone))
        # except ApiIdInvalidError as err:
        #     log.error(err)
        #     return False
        sent_code = client.send_code_request(phone, force_sms=True)
        return sent_code.phone_registered

    @classmethod
    def is_accessible(cls, phone):
        client = cls.get_client(phone)
        status = False
        if client:
            try:
                if client.connect():
                    status = client.is_user_authorized()
            except:
                status = False
        return status

    @classmethod
    def getAllowedGroups(cls):
        from bot.models import Group
        if len(cls.allowedGroups) == 0:
            cls.allowedGroups = Group.objects.filter(enabled=True)
        return cls.allowedGroups

    @classmethod
    def setAllowedGroups(cls, groups):
        cls.allowedGroups = groups

    @classmethod
    def getAllowedGroupIDs(cls):
        from bot.models import Group
        if len(cls.ALLOWED_GROUP_IDS) == 0:
            cls.ALLOWED_GROUP_IDS = Group.objects.filter(enabled=True).values_list('id', flat=True)
        return cls.ALLOWED_GROUP_IDS

    @classmethod
    def setAllowedGroupIDS(cls, ids):
        cls.ALLOWED_GROUP_IDS = ids


    def callback(self, update):
        print(".............")


class TinClient():
    api_id = 109317
    api_hash = '71e0a46537592c6d2f2a56cfbfeba33a'
    phone = '+2348077737774'

    # api_id = 187136
    # api_hash = 'aa09410fbbccf046acf7ef14fb60efb6'
    # phone = '+00212661422956'

    # api_id = 160077
    # api_hash = '28bcfee96563fd4f3769fe45683388cb'
    # phone = '+447743770917'
    t_client = None

    TELEGRAM = "Telegram"
    INSTAGRAM = "Instagram"

    i_client = None

    @classmethod
    def getConnection(cls, type=TELEGRAM):
        if type == cls.TELEGRAM:
            if not cls.t_client:
                cls.t_client = TelegramClient(cls.phone[1:], cls.api_id, cls.api_hash, update_workers=1)
                cls.t_client.connect()
            return cls.t_client
        elif type == cls.INSTAGRAM:
            if not cls.i_client:
                cls.i_client = InstagramAPI(settings.INSTAGRAM_USER, settings.INSTAGRAM_PASS)
                cls.i_client.login()  # login
            elif not cls.i_client.isLoggedIn:
                    cls.i_client.login()
            return cls.i_client

    def getConnectionInstance(self, type=TELEGRAM):
        if type == self.TELEGRAM:
            client = TelegramClient(self.phone[1:], self.api_id, self.api_hash, update_workers=1)
            client.connect()
            return client
        elif type == self.INSTAGRAM:
            client = InstagramAPI(settings.INSTAGRAM_USER, settings.INSTAGRAM_PASS)
            client.login()  # login
            return client
class TMember():
    id = None
    username = None
    phone = None
    access_hash = None
    first_name = None
    last_name = None
    title = None
    type = None
    bot = False
    last_seen = None
    last_update = datetime.now()

    group = None
    is_admin = False


    def __init__(self, dictionary=None, type="User", admins=[], group=None, *args, **kwargs):
        if dictionary:
            self.__dict__.update(dictionary)
            try:
                self.last_seen = dictionary['status'].was_online
            except (AttributeError, KeyError) as err:
                try:
                    self.last_seen = dictionary['status'].expires
                except (AttributeError, KeyError) as err:
                    self.last_seen = None
            self.type = "Bot" if dictionary['bot'] else type
            self.group = group
            for ad in admins:
                if ad.user_id == dictionary['id']:
                    self.is_admin = True
        else:
            super(TMember, self).__init__(*args, **kwargs)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __str__(self):
        return "{}, {}".format(self.id, self.access_hash)



class TAdminMember():
    user_id = None
    inviter_id = None
    promoted_by = None
    username = None
    type = None
    can_edit = True
    # can_edit = False
    # can_edit = False
    # can_edit = False
    # can_edit = False
    # can_edit = False
    last_update = datetime.now()

    group = None
    is_admin = False

    def __init__(self, dictionary=None, type="User", group=None, *args, **kwargs):
        if dictionary:
            self.__dict__.update(dictionary)
            log.warning(dictionary)
            try:
                self.type = "Bot" if dictionary['bot'] else type
            except KeyError as err:
                self.type = type
            self.group = group
        else:
            super(TAdminMember, self).__init__(*args, **kwargs)

    def __hash__(self):
        return hash(self.user_id)

    def __eq__(self, other):
        return self.user_id == other.user_id

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __str__(self):
        return "{}".format(self.user_id)
