import html
import re


def clean_text(text: str):
    striped_txt = text.strip()
    return html.unescape(
        re.sub(r"<\/?(p|span)[^>]*>", "", striped_txt)
        .replace("<br>", "\n")
        .replace("&lt;", "&amp;lt;")
        .replace("&gt;", "&amp;gt;"),
    )
