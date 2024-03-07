class HDRezkaError(Exception):
    """Any HDRezka exception"""


class EmptyPage(HDRezkaError):
    """The requested page is empty"""


class AJAXFail(HDRezkaError):
    """The success field in the response is false"""


class PageNotFound(HDRezkaError):
    """The requested page was not found"""


class ServiceUnavailable(HDRezkaError):
    """Service is temporarily unavailable"""


class LoadingError(HDRezkaError):
    """The server response status code is not within the range of 200"""
