import logging

from .types import OutputType
from .registry import conversion
from ..model.http import make_outlinks

logger = logging.getLogger(__name__)

@conversion(OutputType.Links, "text/html")
def links_processor(r, **kwargs):
    """return a list of links found on the given resource"""
    with r.make_stream() as fp:
        try:
            content = fp.read().decode()
            return list(make_outlinks(content, r._make_url()))
        except Exception as e:
            logger.error("Conversion error", exc_info=True)
            return None
