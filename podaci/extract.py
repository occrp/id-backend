import logging
import textract

log = logging.getLogger(__name__)


def get_file_text(pfile):
    """ Try to extract the actual text from a given file stored in podaci. """
    try:
        text = textract.process(pfile.local_path)
        if text is not None:
            log.info("Extracted %d bytes of text from %r", len(text), pfile)
        return text
    except Exception as ex:
        log.exception(ex)
