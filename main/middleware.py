import logging

logger = logging.getLogger('main')

class ExceptionLoggingMiddleware(object):
    """
    This middleware provides logging of exception in requests.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_exception(self, request, exception):
        """
        Processes exceptions during handling of a http request.
        Logs them with *ERROR* level.
        """
        logger.error(
            """Processing exception %s at %s.
            GET %s """,
            exception, request.path, request.GET if request.GET else request.POST)


