__all__ = ('DumbSyntaxError',
           'DumbNameError',
           'DumbTypeError',
           'DumbValueError',
           'DumbEOFError')


class Error(Exception):

    def __init__(self, message, loc=None):
        super().__init__(message)
        self.message = message
        self.loc = loc


class DumbSyntaxError(Error):
    pass


class DumbNameError(Error):
    pass


class DumbTypeError(Error):
    pass


class DumbValueError(Error):
    pass


class DumbEOFError(Error):
    pass
