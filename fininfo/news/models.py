from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django_ckeditor_5.fields import CKEditor5Field
from imagekit.models import ImageSpecField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from parler.models import TranslatableModel
from parler.models import TranslatedFields
from taggit.managers import TaggableManager

from fininfo.categories.models import Category
from fininfo.core.models import TimeStampedModel
from fininfo.utils.validators import validate_telegram_link

User = get_user_model()


class News(TimeStampedModel, TranslatableModel):
    class NewsStatus(models.TextChoices):
        PUBLISHED = "published", _("Chop etildi")
        DRAFT = "draft", _("Qoralama")

    translations = TranslatedFields(
        title=models.CharField(
            max_length=255,
            db_index=True,
            verbose_name=_("Sarlavha"),
        ),
        short_content=CKEditor5Field(verbose_name=_("Qisqa matn (Lid)")),
        content=CKEditor5Field(
            config_name="extends",
            verbose_name=_("Kontent"),
        ),
        image_source=models.CharField(
            max_length=255,
            verbose_name=_("Asosiy rasm ostidagi yozuv"),
            blank=True,
        ),
        image_name=models.CharField(
            max_length=255,
            verbose_name=_("Rasm nomi"),
            help_text=_(
                "Google'da izlaganda joylangan asosiy rasmni topish oson \
                bo'lishi uchun kalit so'zlar",
            ),
            blank=True,
        ),
        tags=TaggableManager(
            verbose_name=_("Teg"),
            help_text=_(
                "Vergul bilan kiritilsin: (Misol: ekologiya, Aziz Abduhakimov)",
            ),
        ),
        slug=models.SlugField(max_length=255, db_index=True),
        meta={"unique_together": [("slug", "language_code")]},
    )
    category = models.ForeignKey(
        to=Category,
        on_delete=models.SET_NULL,
        db_index=True,
        null=True,
        verbose_name=_("Bo'lim"),
    )
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Muallif"),
        null=True,
        blank=True,
    )
    news_status = models.CharField(
        max_length=20,
        choices=NewsStatus.choices,
        default=NewsStatus.PUBLISHED,
        verbose_name=_("Holati"),
    )
    publish = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name=_("Sana"),
    )
    number_of_views = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Ko'rishlar soni"),
    )
    is_pinned = models.BooleanField(default=False, verbose_name=_("Muhim yangilik"))
    author_choice = models.BooleanField(
        default=False,
        verbose_name=_("Muharrir tanlovi"),
    )
    youtube_link = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Youtube video"),
    )
    tizer_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Tizer"),
        help_text=_(
            "Telegram kanalga video xabar joylash uchun maxsus kanalga \
                joylangan video havolasini kiriting",
        ),
        validators=[validate_telegram_link],
    )
    image = models.ImageField(
        max_length=500,
        upload_to="images/",
        verbose_name=_("Asosiy rasm"),
    )
    image_large = ImageSpecField(
        source="image",
        processors=[ResizeToFill(820, 546)],
        format="webp",
        options={"quality": 90},
    )
    image_medium = ImageSpecField(
        source="image",
        processors=[ResizeToFill(402, 268)],
        format="webp",
        options={"quality": 90},
    )
    image_small = ImageSpecField(
        source="image",
        processors=[ResizeToFill(303, 202)],
        format="webp",
        options={"quality": 90},
    )
    short_slug = models.SlugField(
        max_length=10,
        unique=True,
    )
    expired_at = models.DateTimeField(
        null=True,
        verbose_name=_("Amal qilish muddati"),
    )
    send_tg = models.BooleanField(
        default=True,
        verbose_name=_("Telegramdan yuborish"),
    )
    is_sent_tg = models.BooleanField(
        default=False,
        verbose_name=_("Telegramdan yuborildi"),
    )

    class Meta:
        verbose_name = _("Yangilik")
        verbose_name_plural = _("Yangiliklar")

    def __str__(self) -> str:
        return self.title

    def increment_number_of_views(self):
        self.number_of_views += 1
        self.save()


class NewsGallery(TimeStampedModel):
    image = ProcessedImageField(
        upload_to="gallery/",
        format="webp",
        processors=[ResizeToFill(820, 546)],
        options={"quality": 90},
        verbose_name=_("Rasm"),
    )
    post = models.ForeignKey(to=News, on_delete=models.CASCADE, related_name="gallery")

    class Meta:
        verbose_name = _("Foto galereya")
        verbose_name_plural = _("Foto galereya")

    def __str__(self):
        return str(self.post)


class Comment(TimeStampedModel):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ("created_at",)
    
    def __str__(self):
        return f"Comment by {self.user.first_name} on {self.news}"
