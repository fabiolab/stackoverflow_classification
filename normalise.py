import unicodedata
import re

# Char to remove
REMOVABLE_CHARS = '!"#$%&*+,;<=>?@[\\]^`{|}~_'

# Don't remove, these characters make sense => .:/()-'
# . is used in IP
# : and / are used for setting transfer protocol


def _remove_html(raw_html):
    cleaner_regexp = re.compile("<.*?>")
    clean_text = re.sub(cleaner_regexp, "", raw_html)

    clean_text = clean_text.replace("&amp;", "&")
    clean_text = clean_text.replace("&nbsp;", " ")
    return clean_text


def _remove_accents(raw_text):
    # Replace accented characters by unaccented ones
    clean_text = "".join(
        (
            c
            for c in unicodedata.normalize("NFD", raw_text)
            if unicodedata.category(c) != "Mn"
        )
    )
    return clean_text


def _replace_digits(text):
    # replace all digits by the character ø
    new_text = re.sub("\d", "ø", text)
    return new_text


def normalise(raw_text):
    transform = _remove_html(raw_text)
    transform = transform.lower()
    # transform = _remove_accents(transform)
    transform = _replace_digits(transform)

    # Replace special characters with spaces
    transform = transform.translate(
        transform.maketrans(REMOVABLE_CHARS, " " * len(REMOVABLE_CHARS))
    )
    # To remove all characters rather than replace by spaces :
    # transform = transform.translate(transform.maketrans("", "", REMOVABLE_CHARS))

    # Remove leading and trailed spaces
    # Remove multiple spaces
    transform = " ".join(transform.split())

    return transform
