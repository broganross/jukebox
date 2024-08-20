""" Interfaces for the service module
"""

from typing import List
from typing import Optional
from typing import Protocol
from .data import Album
from .data import Page
from .data import Track


class Credits(Protocol):
    """ Interface for keeping track of the number of credits available for playback
    """
    def add_credits(self, credit: int):
        """ Add some number of credits to storage
        :param credit: the number of credits to add
        :type credit: int
        """

    def remove_credits(self, credit: int):
        """ Remove some number of credits from storage
        :param credit: Number of credits to remove
        :type credit: int
        """

    def get_credits(self) -> int:
        """ Return the number of available credits
        :returns: The number of credits
        :rtype: int
        """


class CurrentTrack(Protocol):
    """ Interface for retrieving the currently playing track id
    """
    def current_track_id(self) -> str:
        """ Return the currently playing track id
        """


class Discography(Protocol):
    """ Interface for getting information about available discography
    """
    def get_albums(self, page: Optional[Page] = None) -> List[Album]:
        """ Get the list of available albums
        :param page: pagination options
        :rtype page: Page
        """

    def get_album_tracks(self, album_id: str, page: Optional[Page] = None) -> List[Track]:
        """ Get the list of tracks for the given album
        :param album_id: Id of the album to get tracks from
        :type album_id: str
        :param page: Pagination options
        :rtype page: Page
        :raises InvalidAlbumIdException: if the album_id is incorrectly formatted
        :raises NotFoundException: if the album was not found for the given album_id
        """

    def get_track(self, track_id: str) -> Track:
        """ Get the information about a specific track
        :raises InvalidTrackIdException: if the track_id is incorrectly formatted
        :raises NotFoundException: if the track was not found for the given id
        """



class Queue(Protocol):
    """ Interface for adding to and looking at a queue
    """
    def enque(self, track_url: str):
        """ Returns the next track id in the queue and removes it
        """

    def peak(self) -> str:
        """ Returns the next track id in the queue without removing it
        """
