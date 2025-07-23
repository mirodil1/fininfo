from django.db.models.signals import post_save
from django.dispatch import receiver
from parler.utils.context import switch_language

from fininfo.news.models import News
from fininfo.utils.transliterate import to_cyrillic
from fininfo.utils.transliterate import to_latin


@receiver(post_save, sender=News)
def save_translated_news(sender, instance, created, **kwargs):
    """
    Transliteration from uzbek-cyrilic to uzbek-latin
    """
    if created:
        if instance.get_current_language() == "uz-cyril":
            title = to_latin(instance.title)
            short_content = to_latin(instance.short_content)
            content = to_latin(instance.content)
            image_source = to_latin(instance.image_source)
            image_name = to_latin(instance.image_name)
            slug = instance.slug

            # Saving latin news
            with switch_language(instance, "uz"):
                instance.title = title
                instance.short_content = short_content
                instance.content = content
                instance.slug = slug
                instance.image_source = image_source
                instance.image_name = image_name
                instance.save()

        elif instance.get_current_language() == "uz":
            title = to_cyrillic(instance.title)
            short_content = to_cyrillic(instance.short_content)
            content = to_cyrillic(instance.content)
            image_source = to_cyrillic(instance.image_source)
            image_name = to_cyrillic(instance.image_name)
            slug = instance.slug

            # Saving cyrillic news
            with switch_language(instance, "uz-cyril"):
                instance.title = title
                instance.short_content = short_content
                instance.content = content
                instance.slug = slug
                instance.image_source = image_source
                instance.image_name = image_name
                instance.save()
