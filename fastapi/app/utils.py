def simple_paragraph_split(text: str) -> list[str]:
    """
    Splits text into paragraphs based on double newlines.
    You can tweak logic to use regex, sentence boundaries, etc.
    """
    return [p.strip() for p in text.split("\n\n") if p.strip()]
