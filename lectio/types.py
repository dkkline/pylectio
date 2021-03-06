"""
Contains the base types used by pylectio.
"""

from enum import Enum
import hashlib


class LectioType(object):
    """
    Abstract Base Class for Lectio Types.
    """
    ATTRIBUTES = []

    def get_hash(self):
        """
        Returns a hash of the object.
        """
        hasher = hashlib.sha512()

        for attribute in self.ATTRIBUTES:
            attr = getattr(self, attribute)

            if attr is not None:
                hasher.update(str(attr).encode("utf-8"))
            else:
                hasher.update("NONE".encode("utf-8"))

        return hasher.hexdigest()

    def __repr__(self):
        indent = "\t"

        x = "<{}>".format(self.__class__.__name__)

        for attribute in self.ATTRIBUTES:
            attr_line = "{}: {}".format(attribute, getattr(self, attribute))
            x += "\n{}{}".format(indent, attr_line)

        return x


class PeriodStatuses(Enum):
    """
    Enumerates the statuses that a ``Period`` can have.
    """
    NOTHING = 0
    CANCELLED = 1
    CHANGED = 2


class AssignmentWaitingFor(Enum):
    """
    Enumerates the people that an ``Assignment`` can be waiting for.
    """
    STUDENT = 0
    TEACHER = 1


class AssignmentStatuses(Enum):
    """
    Enumerates the statuses that an ``Assignment`` can have.
    """
    HANDED_IN = 0
    WAITING = 1
    MISSING = 2
