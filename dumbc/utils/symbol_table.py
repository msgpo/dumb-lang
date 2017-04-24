import contextlib

from collections import deque


class SymbolTable:
    """Scope stack.

    Examples
        >>> t = SymbolTable()
        >>> t.push()
        >>> t.set('foo', 'bar')
        >>> t.push()
        >>> t.set('cheese', 'pizza')
        >>> t.has('foo')
        True
        >>> t.has('cheese')
        True
        >>> t.pop()
        {'cheese': 'pizza'}
        >>> t.has('cheese') # now 'cheese' is out of scope
        False
        >>> t.get('foo')
        'bar'
        >>> t.pop()
        {'foo': 'bar'}
        >>> with t.scope(): # you can use context manager too
        ...    t.set('cheese', 'foobar')
    """

    def __init__(self):
        self.scopes = deque()

    def push(self):
        """Enter a new scope."""
        self.scopes.append(dict())

    def pop(self):
        """Leave current scope."""
        return self.scopes.pop()

    def has(self, key):
        """Check whether given key is reachable.

        Arguments:
            key: Given key.

        Returns:
            bool: True if given key is reachable, otherwise False.

        """
        for scope in reversed(self.scopes):
            if key in scope:
                return True
        return False

    def get(self, key):
        """Get associated value with a key."""
        for scope in reversed(self.scopes):
            if key in scope:
                return scope[key]
        return None

    def set(self, key, value):
        """Set associated value with a key."""
        scope = self.scopes[-1]
        scope[key] = value

    @contextlib.contextmanager
    def scope(self):
        self.push()
        try:
            yield
        finally:
            self.pop()
