import re
from html import unescape


def html_to_text(html: str) -> str:
    """Convertit du HTML en texte propre"""
    if not html:
        return ""
    
    # Décoder les entités HTML
    text = unescape(html)
    
    # Supprimer les scripts et styles
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remplacer les sauts de ligne HTML
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</div>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</li>", "\n", text, flags=re.IGNORECASE)
    
    # Supprimer tous les tags HTML restants
    text = re.sub(r"<[^>]+>", "", text)
    
    # Nettoyer les espaces multiples
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    
    # Supprimer les espaces en début/fin de ligne
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)
    
    return text.strip()
