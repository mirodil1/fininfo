from dal import autocomplete
from parler.forms import TranslatableModelForm
from django.contrib.auth import get_user_model

from fininfo.news.models import News


User = get_user_model()


class NewsAdminForm(TranslatableModelForm, autocomplete.FutureModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter the author field to show only superusers or staff
        self.fields["author"].queryset = User.objects.filter(is_staff=True)
    
    class Meta:
        model = News
        fields = "__all__"
        widgets = {"tags": autocomplete.TaggitSelect2("tag-autocomplete")}
