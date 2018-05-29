from django.contrib import admin

# Register your models here.
from bot.models import Message, Member, MessageTemplate, News, Level, NewsSource, Result

MAX_SHOW_ALL = 2000
PER_PAGE = 500


# @admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('from_id', 'message_id', 'source_id', 'created', 'treated', 'text')
    search_fields = ['from_id', 'message_id', 'source_id', 'text', 'for_id']
    date_hierarchy = 'created'
    list_filter = ('treated',)
    list_max_show_all = MAX_SHOW_ALL
    list_per_page = PER_PAGE


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    # list_display = ('member_id', 'first_name', 'last_name', 'username', 'type', 'is_bot', 'user', 'is_blacklisted', 'created')
    list_display = ('member_id', 'first_name', 'last_name', 'username', 'type', 'is_bot', 'user', 'subscribed', 'created')
    search_fields = ['member_id', 'first_name', 'last_name', 'username']
    date_hierarchy = 'created'
    list_filter = ('is_bot', 'subscribed')
    list_max_show_all = MAX_SHOW_ALL
    list_per_page = PER_PAGE


# @admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ('type', 'text')
    search_fields = ['text']
    date_hierarchy = 'created'
    list_filter = ('type', )
    list_max_show_all = MAX_SHOW_ALL
    list_per_page = PER_PAGE
    readonly_fields = ('group',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'source', 'status', 'sent_time', 'score_time', 'update', 'created', 'url', 'src_time')
    search_fields = ['title', 'source', 'url', 'status']
    date_hierarchy = 'created'
    list_filter = ('status', )
    list_max_show_all = MAX_SHOW_ALL
    list_per_page = PER_PAGE
    readonly_fields = ('src_time',)


@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ('label', 'source', 'enabled', 'latest', 'update', 'created')
    search_fields = ['label', 'source']
    date_hierarchy = 'created'
    list_filter = ('enabled', )
    list_max_show_all = MAX_SHOW_ALL
    list_per_page = PER_PAGE


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('label', 'point', 'enabled')
    search_fields = ['label', 'point']
    # date_hierarchy = 'created'
    list_filter = ('enabled', )
    list_max_show_all = MAX_SHOW_ALL
    list_per_page = PER_PAGE


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('news', 'member', 'type', 'read', 'accepted', 'late', 'created')
    search_fields = ['news', 'member', 'type', ]
    date_hierarchy = 'created'
    list_filter = ('type', 'read', 'accepted', 'late', )
    list_max_show_all = MAX_SHOW_ALL
    list_per_page = PER_PAGE

