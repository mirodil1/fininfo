# ruff: noqa
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView

from fininfo.core.views import TagAutocomplete
from fininfo.pages.sitemaps import NewsSitemap
from fininfo.pages.feeds import LatestNews
from fininfo.ads.views import ads_number_of_views
from django.contrib.sitemaps.views import sitemap

sitemaps = {"news": NewsSitemap}
urlpatterns = i18n_patterns(
    path("", RedirectView.as_view(url=settings.ADMIN_URL), name="home"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path("i18n/", include("django.conf.urls.i18n")),
    path(
        "ckeditor5/",
        include("django_ckeditor_5.urls"),
        name="ck_editor_5_upload_file",
    ),
    path(
        "tag-autocomplete/",
        TagAutocomplete.as_view(),
        name="tag-autocomplete",
    ),
    path(
        "ads/number-of-views/<str:ad_type>/",
        ads_number_of_views,
        name="number_of_views",
    ),
    path("feed/", LatestNews(), name="news_feed"),
    path("feed/<str:category_slug>/", LatestNews(), name="news_feed_by_category"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
)

# API URLS
urlpatterns += i18n_patterns(
    # API base url
    path("api/categories/", include("fininfo.categories.urls"), name="categories"),
    path("api/news/", include("fininfo.news.urls"), name="news"),
    path("api/users/", include("fininfo.users.urls"), name="users"),
    path("api/pages/", include("fininfo.pages.urls"), name="pages"),
    path("api/ads/", include("fininfo.ads.urls"), name="ads"),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
