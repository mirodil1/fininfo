from dal import autocomplete
from parler.forms import TranslatableModelForm

from fininfo.news.models import News


class NewsAdminForm(TranslatableModelForm, autocomplete.FutureModelForm):
    class Meta:
        model = News
        fields = "__all__"
        widgets = {"tags": autocomplete.TaggitSelect2("tag-autocomplete")}
