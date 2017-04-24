class Colors:
    RED = '\033[91;1m'
    MAGENTA = '\033[95;1m'
    CYAN = '\033[36;1m'
    NORMAL = '\033[0m'


class DiagnosticsEngine:
    """Diagnostics engine.

    It prints pretty warning messages, etc.

    Attributes:
        filename (str): Filename of a file to be compiled.
        lines (list): Lines of the file.
    """

    def __init__(self, filename, text):
        self.filename = filename
        self.lines = text.split('\n')

    def _print_full(self, color, kind, message, loc, window=3):
        msg = '{filename}:{line}:{col}:{color}{kind}{normal_color}: {message}'
        msg = msg.format(filename=self.filename,
                         line=loc.line,
                         col=loc.column,
                         color=color,
                         kind=kind,
                         normal_color=Colors.NORMAL,
                         message=message)
        print(msg + '\n')
        for i in range(-window, window):
            curr_line = loc.line + i
            if curr_line < 0 or curr_line > len(self.lines):
                continue
            print('\t' + self.lines[curr_line - 1])
            if i == 0:
                print('\t{space}{color}^{tildas}{normal_color}'.format(
                    space=' ' * (loc.column - 1),
                    color=color,
                    tildas='~' * (loc.extent - 1),
                    normal_color=Colors.NORMAL))
        print('\n')

    def _print_header(self, color, kind, message):
        msg = '{filename}:{color}{kind}{normal_color}: {message}'
        msg = msg.format(filename=self.filename,
                         color=color,
                         kind=kind,
                         normal_color=Colors.NORMAL,
                         message=message)
        print(msg + '\n')

    def _print(self, color, kind, message, loc):
        if loc is None:
            self._print_header(color, kind, message)
        else:
            self._print_full(color, kind, message, loc)

    def info(self, message, loc=None):
        """Print info message.

        Args:
            loc (Location): Part of a text to be marked.
            message (str): Message which will be displayed.
        """
        self._print(Colors.CYAN, 'info', message, loc)

    def warning(self, message, loc=None):
        """Print warning message.

        Args:
            loc (Location): Part of a text to be marked.
            message (str): Message which will be displayed.
        """
        self._print(Colors.MAGENTA, 'warning', message, loc)

    def error(self, message, loc=None):
        """Print error message.

        Args:
            loc (Location): Part of a text to be marked.
            message (str): Message which will be displayed.
        """
        self._print(Colors.RED, 'error', message, loc)
