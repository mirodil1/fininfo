import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_telegram_link(link):
    link_pattern = re.compile(r"https://t\.me/c/(\d+)/(\d+)")
    if not link_pattern.match(link):
        msg = _("Tizer havola noto'g'ri kiritildi")
        raise ValidationError(msg)
    return link
