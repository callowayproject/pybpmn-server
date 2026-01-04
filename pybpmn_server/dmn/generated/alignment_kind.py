from enum import Enum

__NAMESPACE__ = "http://www.omg.org/spec/DMN/20180521/DC/"


class AlignmentKind(Enum):
    """
    AlignmentKind enumerates the possible options for alignment for layout
    purposes.
    """

    START = "start"
    END = "end"
    CENTER = "center"
