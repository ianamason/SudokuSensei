""" A StringBuilder class for string buffer addicts.
"""
import io

class StringBuilder:
    """StringBuilder mimics Javas StringBuilder class."""
    def __init__(self):
        self.empty = True
        self._stringio = io.StringIO()

    def __str__(self):
        val = self._stringio.getvalue()
        self._stringio.close()
        return val

    # this one returns the string buffer (and so could be closed by a print)
    def append(self, obj):
        """appends the string representation of the given object to the string buffer.

        This routine returns the string builder, and so can be chained.
        """
        data = str(obj)
        if self.empty and len(data) > 0:
            self.empty = False
        self._stringio.write(data)
        return self

    # this one returns None
    def add(self, obj):
        """appends the string representation of the given object to the string buffer.

        This routine returns None.
        """
        data = str(obj)
        if self.empty and len(data) > 0:
            self.empty = False
        self._stringio.write(data)

    def isempty(self):
        """deterimes in the string builder is empty."""
        return self.empty
