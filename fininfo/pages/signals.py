from django.db.models.signals import post_save
from django.dispatch import receiver
from parler.utils.context import switch_language

from fininfo.pages.models import Page
from fininfo.utils.transliterate import to_cyrillic
from fininfo.utils.transliterate import to_latin


@receiver(post_save, sender=Page)
def save_translated_page(sender, instance, created, **kwargs):
    """
    Transliteration from uzbek-cyrilic to uzbek-latin vice versa
    """
    if created:
        if instance.get_current_language() == "uz-cyril":
            name = to_latin(instance.name)
            short_content = to_latin(instance.short_content)
            content = to_latin(instance.content)

            # Saving latin news
            with switch_language(instance, "uz"):
                instance.name = name
                instance.short_content = short_content
                instance.content = content
                instance.save()

        elif instance.get_current_language() == "uz":
            name = to_cyrillic(instance.name)
            short_content = to_cyrillic(instance.short_content)
            content = to_cyrillic(instance.content)

            # Saving cyrillic news
            with switch_language(instance, "uz-cyril"):
                instance.name = name
                instance.short_content = short_content
                instance.content = content
                instance.save()
