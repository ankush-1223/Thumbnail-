def clean_caption(caption):
    return caption.strip()

def get_footer():
    return "© Telegram Media — Sharing Limited to Telegram only."

def get_thumbnail():
    try:
        with open("thumbnail.txt") as f:
            return f.read().strip()
    except:
        return None
