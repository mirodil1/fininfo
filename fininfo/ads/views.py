import random

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from fininfo.ads.models import Ad
from fininfo.ads.models import AdStat
from fininfo.ads.serializers import AdSerializer


class AdViewSet(ListModelMixin, GenericViewSet):
    queryset = Ad.objects.filter(is_active=True)
    serializer_class = AdSerializer

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        ad_type = self.kwargs.get("type")
        if ad_type:
            qs = qs.filter(ad_type__slug=ad_type)
        qs_list = list(qs)
        if qs_list:
            # Fetch random obj from qs
            random_items = random.sample(qs_list, 1)
            self.add_number_of_views(random_items[0])
            return random_items
        return []

    def add_number_of_views(self, ad: Ad):
        AdStat.objects.create(ad=ad, stat_type=AdStat.StatType.VIEWS)


@api_view(["POST"])
def clicked_ad(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    AdStat.objects.create(ad=ad, stat_type=AdStat.StatType.CLICKS)
    return Response(status=status.HTTP_204_NO_CONTENT)


@staff_member_required
def ads_number_of_views(request, ad_type):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    stat_type = request.GET.get("stat_type")

    qs = AdStat.objects.filter(stat_type=stat_type)

    ads = (
        qs.filter(ad__is_active=True, ad__ad_type__slug=ad_type)
        .select_related("ad")
        .values("ad__name", "created_at__date")
        .annotate(view_count=Count("id"))
        .order_by("created_at__date")
    )

    if start_date and end_date:
        ads = ads.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
        )
    elif start_date:
        ads = ads.filter(created_at__date__gte=start_date)
    elif end_date:
        ads = ads.filter(created_at__date__lte=end_date)

    ads_data = []
    for item in ads:
        ad_name = item["ad__name"]
        date_str = str(item["created_at__date"])
        count = item["view_count"]
        found = False
        for entry in ads_data:
            if entry["name"] == ad_name:
                entry["number_of_views"].append(
                    {"created_at": date_str, "count": count},
                )
                found = True
                break

        if not found:
            ads_data.append(
                {
                    "name": ad_name,
                    "number_of_views": [{"created_at": date_str, "count": count}],
                },
            )
    return JsonResponse(ads_data, safe=False)
