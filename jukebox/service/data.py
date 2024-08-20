""" Data types
"""


from dataclasses import dataclass
from typing import List


@dataclass
class Track:
    """ Song, audio track, etc
    """
    "01-01"
    track_id: str
    name: str
    duration: str
    url: str


@dataclass
class Album:
    """ Album data
    """
    "01"
    album_id: str
    artist: str
    title: str
    tracks: List[Track]


@dataclass
class Charge:
    """ A charge to be converted into credits
    """
    amount: int
    # TODO: make it an enum
    currency: str


@dataclass
class Page:
    """ Represents pagination options for retrieving list of items
    :param cursor: Identifier for the cursor location
    :param size: The number of items to return
    :param before: Whether to return items before the cursor
    """
    # NOTE: this should probably be more extendable, as an interface.
    cursor: str
    size: int
    before: bool
