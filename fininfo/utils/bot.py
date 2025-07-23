import environ
import telebot
from django.conf import settings

env = environ.Env()

BOT_TOKEN = settings.BOT_TOKEN
CHAT_ID = settings.CHAT_ID

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


def send_news(  # noqa: PLR0913
    image,
    title: str,
    short_content: str,
    short_url: str,
    youtube_link: str | None = None,
    from_chat_id: str | None = None,
    message_id: str | None = None,
):
    text = f"<b>{title}</b>\n\n"
    text += f"{short_content}\n\n"
    text += f"<b>Батафсил:</b> https://fininfo.uz/{short_url}\n\n"

    if youtube_link:
        text += f"<a href='{youtube_link}'>📹 ВИДЕОНИ ТОМОША ҚИЛИНГ</a>\n\n"
    text += "👉 @fininfouzb"

    if from_chat_id and message_id:
        bot.copy_message(
            chat_id=CHAT_ID,
            from_chat_id=from_chat_id,
            message_id=message_id,
            caption=text,
        )
    else:
        bot.send_photo(CHAT_ID, image, caption=text)
