# ruff: noqa

from django.conf import settings
from django.utils.translation import get_language
from rest_framework import serializers


class TranslatedSerializerMixin:
    """
    Mixin for selecting only requested translation with django-parler-rest
    """

    def to_representation(self, instance):
        inst_rep = super().to_representation(instance)
        lang_code = get_language()
        result = {}

        for field_name in self.get_fields():
            # add normal field to resulting representation
            if field_name != "translations":
                field_value = inst_rep.pop(field_name, None)
                result.update({field_name: field_value})
            if field_name == "translations":
                translations = inst_rep.pop(field_name, None)
                if translations:
                    if lang_code not in translations:
                        # use fallback setting in PARLER_LANGUAGES
                        parler_default_settings = settings.PARLER_LANGUAGES["default"]
                        if "fallback" in parler_default_settings:
                            lang_code = parler_default_settings.get("fallback")
                        if "fallbacks" in parler_default_settings:
                            lang_code = parler_default_settings.get("fallbacks")[0]

                    for lang, translation_fields in translations.items():
                        if lang == lang_code:
                            trans_rep = (
                                translation_fields.copy()
                            )  # make copy to use pop() from
                            for (
                                trans_field_name,
                                trans_field,
                            ) in translation_fields.items():
                                field_value = trans_rep.pop(trans_field_name)
                                result.update({trans_field_name: field_value})

        return result


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)
        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
