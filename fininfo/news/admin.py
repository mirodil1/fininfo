import re
import uuid
from typing import Any

from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.widgets import AdminFileWidget
from django.core.cache import cache
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin
from parler.utils.context import switch_language
from taggit.models import Tag
from telebot.apihelper import ApiTelegramException

from fininfo.news.forms import NewsAdminForm
from fininfo.news.models import News
from fininfo.news.models import NewsGallery
from fininfo.utils.bot import send_news
from fininfo.utils.helper import clean_text
from fininfo.utils.transliterate import to_latin


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)
            output.append(
                f' <a href="{image_url}" target="_blank"><img src="{image_url}" \
                    alt="{file_name}"width="50" height="50" \
                    style="object-fit: cover;"/></a>',
            )
        output.append(super().render(name, value, attrs, renderer))
        return mark_safe("".join(output))  # noqa: S308


class NewsGalleryInline(admin.TabularInline):
    model = NewsGallery
    formfield_overrides = {models.ImageField: {"widget": AdminImageWidget}}
    extra = 2


@admin.register(News)
class NewsAdmin(TranslatableAdmin):
    form = NewsAdminForm
    fieldsets = (
        (
            _("Yangilik"),
            {
                "fields": (
                    "title",
                    "short_content",
                    "content",
                    "tags",
                    "image",
                    "image_source",
                    "category",
                    "author",
                    "is_pinned",
                    "tizer_id",
                    "publish",
                    "news_status",
                    "send_tg",
                ),
            },
        ),
    )
    list_display = [
        "display_image",
        "title",
        "category",
        "translated",
        "publish",
        "number_of_views",
        "news_status",
        "is_sent_tg",
        "author",
    ]
    list_filter = ["news_status", "publish", "author"]
    readonly_fields = ["slug", "number_of_views"]
    exclude = ["slug"]
    list_display_links = [
        "display_image",
        "title",
    ]
    search_fields = [
        "translations__title",
        "translations__short_content",
        "translations__content",
    ]
    ordering = ["-publish"]
    inlines = [NewsGalleryInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("category", "author").prefetch_related(
            "translations",
            "category__translations",
        )

    def save_model(self, request: Any, obj: News, form: Any, change: Any) -> None:
        if not obj.id:
            if not obj.author:
                obj.author = request.user
            obj.short_content = re.sub(r"<p>(?:\s|&nbsp;)*</p>", "", obj.short_content)

            # generate unique short slug
            short_slug = uuid.uuid4().hex[:6]
            while News.objects.filter(short_slug=short_slug).exists():
                short_slug = uuid.uuid4().hex[:6]
            obj.short_slug = short_slug

            slug = slugify(f"{to_latin(obj.title)}")
            if News.objects.filter(translations__slug=slug).exists():
                slug = f"{slug}-{short_slug}"
            obj.slug = slug
        try:
            with transaction.atomic():
                super().save_model(request, obj, form, change)

                if change:
                    self.transliterate_edited(obj)

                if not change:
                    self.send_telegram_news(obj)
            self.set_translatable_tags(obj)
            cache.clear()
        except ApiTelegramException as e:
            err_msg = f"Telegramga jo'natishda xatolik: <<{e!s}>>"
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, err_msg)

    @admin.display(description=_("Asosiy rasm"))
    def display_image(self, obj: News):
        if obj.image.storage.exists(obj.image.name):
            return (
                mark_safe(  # noqa: S308
                    f'<img src="{obj.image_small.url}" width={72} height={48} />',
                )
                if obj.image_small
                else None
            )
        return None

    @admin.display(description=_("Tarjima"))
    def translated(self, obj: News):
        """
        Get list of translated langs of object
        """
        lang = set()
        languages = obj.get_available_languages()
        for language in languages:
            if language in ("uz", "uz-cyril"):
                lang.add("uz")
            else:
                lang.add(language)
        return ", ".join(lang)

    def set_translatable_tags(self, obj: News):
        """
        Set tags after obj being saved.
        """
        current_obj_language = obj.get_current_language()

        if current_obj_language in ("uz", "uz-cyril"):
            translations = obj.translations.filter(
                Q(language_code="uz") | Q(language_code="uz-cyril"),
            )
            for translation in translations:
                tags = []
                for _tag_name in obj.tags:
                    if translation.language_code == "uz":
                        tag_name = to_latin(_tag_name)
                    elif translation.language_code == "uz-cyril":
                        tag_name = _tag_name
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    tags.append(tag)
                translation.tags.set(tags)
        else:
            tags = []
            translation = obj.translations.get(language_code=current_obj_language)
            for tag_name in obj.tags:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            translation.tags.set(tags)

    def send_telegram_news(self, obj: News):
        if (
            obj.send_tg
            and not obj.is_sent_tg
            and obj.get_current_language() == "uz-cyril"
            and obj.news_status == News.NewsStatus.PUBLISHED
            and obj.publish <= timezone.now()
        ):
            from_chat_id = message_id = None
            if obj.tizer_id:
                from_chat_id = "-100" + obj.tizer_id.split("/")[-2]
                message_id = obj.tizer_id.split("/")[-1]

            title = clean_text(obj.title)
            short_content = clean_text(obj.short_content)
            short_url = obj.short_slug
            youtube_link = obj.youtube_link
            image = obj.image

            send_news(
                title=title,
                image=image,
                short_content=short_content,
                short_url=short_url,
                youtube_link=youtube_link,
                from_chat_id=from_chat_id,
                message_id=message_id,
            )
            obj.is_sent_tg = True
            obj.save()

    def transliterate_edited(self, obj):
        if obj.get_current_language() == "uz-cyril":
            title = to_latin(obj.title)
            short_content = to_latin(obj.short_content)
            content = to_latin(obj.content)
            image_source = to_latin(obj.image_source)
            image_name = to_latin(obj.image_name)

            # Saving latin news
            with switch_language(obj, "uz"):
                obj.title = title
                obj.short_content = short_content
                obj.content = content
                obj.image_source = image_source
                obj.image_name = image_name
                obj.save()
