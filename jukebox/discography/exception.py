""" Exceptions
"""

from dataclasses import dataclass


@dataclass
class InvalidAlbumIdException(Exception):
    """ The album id is incorrectly formatted
    """
    message: str


@dataclass
class InvalidTrackIdException(Exception):
    """ The album id is incorrectly formatted
    """
    message: str


@dataclass
class NotFoundException(Exception):
    """ The item was not found in the repository
    """
    message: str
