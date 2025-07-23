import html

from django.contrib.syndication.views import Feed
from django.db.models.base import Model
from django.template.defaultfilters import truncatewords
from django.utils import timezone
from django.utils.feedgenerator import Enclosure
from django.utils.html import strip_tags
from django.utils.translation import get_language

from fininfo.categories.models import Category
from fininfo.news.models import News


class LatestNews(Feed):
    title = "fininfo"
    description = "fininfo"
    link = "https://fininfo.uz"

    def __call__(self, request, *args, **kwargs):
        self.host = request.get_host()
        self.language = get_language()
        return super().__call__(request, *args, **kwargs)

    def get_object(self, request, category_slug=None):
        if category_slug:
            return Category.objects.get(
                translations__slug=category_slug,
                translations__language_code=self.language,
            )
        return None

    def feed_url(self):
        return f"https://{self.host}/feed/"

    def items(self, obj):
        qs = (
            News.objects.filter(
                translations__language_code=self.language,
                news_status=News.NewsStatus.PUBLISHED,
                publish__lte=timezone.now(),
            )
            .select_related("category")
            .prefetch_related("translations")
        )
        if obj:
            qs = qs.filter(category=obj)

        return qs.order_by("-publish")[:10]

    def item_title(self, item: Model) -> str:
        return item.title

    def item_description(self, item: Model) -> str:
        return truncatewords(html.unescape(strip_tags(item.short_content)), 20)

    def item_link(self, item):
        languages = {
            "uz-cyril": "",
            "uz": "uz/",
            "en": "en/",
            "ru": "ru/",
        }
        language = languages.get(self.language, "")
        return f"https://fininfo.uz/{language}news/{item.slug}/"

    def item_pubdate(self, item):
        return item.publish

    def item_enclosures(self, item):
        host = self.host
        return [
            Enclosure(
                f"https://{host}/{item.image_large.url}",
                str(item.image_large.size),
                "image/{}".format(item.image_large.name.split(".")[-1]),
            ),
        ]
