from celery import shared_task
from django.utils import timezone
from telebot.apihelper import ApiTelegramException

from fininfo.news.models import News
from fininfo.utils.bot import send_news
from fininfo.utils.helper import clean_text


@shared_task
def send_telegram_news_task():
    news = News.objects.language("uz-cyril").filter(
        translations__language_code="uz-cyril",
        news_status=News.NewsStatus.PUBLISHED,
        send_tg=True,
        is_sent_tg=False,
        publish__lte=timezone.now(),
    )
    from_chat_id = message_id = None
    for i in news:
        if i.tizer_id:
            from_chat_id = "-100" + i.tizer_id.split("/")[-2]
            message_id = i.tizer_id.split("/")[-1]

        title = clean_text(i.title)
        short_content = clean_text(i.short_content)
        short_url = i.short_slug
        youtube_link = i.youtube_link
        image = i.image
        try:
            send_news(
                title=title,
                image=image,
                short_content=short_content,
                short_url=short_url,
                youtube_link=youtube_link,
                from_chat_id=from_chat_id,
                message_id=message_id,
            )
            i.is_sent_tg = True
            i.save()
        except ApiTelegramException as e:
            print(f"NEWS: {i.title}, ERROR: {e}")  # noqa: T201
