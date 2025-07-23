from django.urls import path

from fininfo.ads.views import AdViewSet
from fininfo.ads.views import clicked_ad

app_name = "ads"


urlpatterns = [
    path("<str:type>/", AdViewSet.as_view({"get": "list"}), name="list"),
    path("click/<int:ad_id>", clicked_ad, name="clicks"),
]
