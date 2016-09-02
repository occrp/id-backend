from django.utils.text import Truncator


def truncate_summary(text):
    """Truncate a ticket summary."""
    tronc = Truncator(text)
    return tronc.chars(140)
