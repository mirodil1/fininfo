from django.contrib.sitemaps import Sitemap
from django.utils import timezone
from django.utils.translation import get_language

from fininfo.news.models import News


class NewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    language = get_language()

    def items(self):
        return News.objects.filter(
            translations__language_code=self.language,
            news_status=News.NewsStatus.PUBLISHED,
            publish__lte=timezone.now(),
        )

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f"/news/{obj.slug}/"
