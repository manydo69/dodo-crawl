
import re
import unicodedata

def slugify(text: str) -> str:
    # Normalize to ASCII
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    # Replace non-alphanumeric characters with hyphens
    text = re.sub(r'[^a-zA-Z0-9]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    # Lowercase
    return text.lower()