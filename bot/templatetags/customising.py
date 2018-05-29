from decimal import Decimal

from django import template
from django.utils.safestring import mark_safe

from bot.models import Member, Setup

register = template.Library()


def decimal_normalise(f):
    d = Decimal(str(f));
    return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()


@register.filter
def due_amount(obj):
    members = Member.objects.filter(referee=obj, status=Member.JOINED)
    setup = Setup.loadSetup(timeout=60*60*24)

    total = members.count() * decimal_normalise(setup.per_referral)

    total = setup.maxi_user_referral_bonus if total >= setup.maxi_user_referral_bonus else total
    # html = ""
    # for o in obj:
    #     html += "<li>"+o+"</li>"
    diff = total - obj.reward
    return decimal_normalise(mark_safe(diff if diff >= 0 else 0) )


@register.filter
def member_count(obj):
    return Member.objects.filter(referee=obj, status=Member.JOINED).count()
