from re import sub

from unidecode import unidecode


def slugify_string(text: str, use_hyphen: bool = True) -> str:
    """Slugify a string.

    Args:
        text (str): The text to be slugified.
        use_hyphen (bool, optional): Use hyphen as a word separator if True. Use
            underscore otherwise. Defaults to True.

    Returns:
        str: The slugified text.
    """

    separator = "-" if use_hyphen is True else "_"

    return sub(r"[\W_]+", separator, unidecode(str(text)).lower())


def should_be_int(value: str) -> bool:
    """Check if a string value should be converter into a integer.

    Args:
        value (str): The string to be evaluated.

    Returns:
        bool: True if the coercion should occurs. False otherwise.
    """

    try:
        int(value)
        return True
    except ValueError:
        return False
