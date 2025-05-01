def clean_caption(caption):
    return caption.strip() if caption else ""

def get_footer():
    return "🔒 Shared via @UltimateClonerBot"

def remove_thumbnail():
    return None  # Force no thumbnail

def get_thumbnail():
    if Config.USE_THUMBNAIL.startswith("url:"):
        return Config.USE_THUMBNAIL.split(":")[1]
    elif Config.USE_THUMBNAIL == "default":
        return "https://example.com/default.jpg"
    return None
