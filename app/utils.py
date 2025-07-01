import re

def clean_html(text: str) -> str:
    allowed_tags = ["b", "i", "u", "s", "code", "pre", "a"]
    return re.sub(r"</?(?!(" + "|".join(allowed_tags) + r"))[^>]+>", "", text)

def markdown_to_html(markdown_text: str) -> str:
    markdown_text = re.sub(r"</?think>", "", markdown_text).strip()
    return markdown_text.replace("\n", "<br>")
