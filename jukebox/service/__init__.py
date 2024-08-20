""" Domain module
"""

from dataclasses import dataclass
from typing import List
from typing import Optional

from jukebox import queue
from jukebox.config import Config
from jukebox.credit import NotEnoughCredits
from .data import Album
from .protocol import Credits
from .protocol import CurrentTrack
from .protocol import Discography
from .protocol import Queue
from .data import Charge
from .data import Track
from .data import Page


@dataclass
class NoCreditsException(Exception):
    """ You tried to do something but you don't have enough credits
    """
    message: str


class Service:
    """ Service is main domain logic for the jukebox
    :param discography: Repository of album information
    :type discography: Discography
    :param queue: Playback queue
    :type queue: Queue
    :param current: Provides interface to get the currently playing track id
    """
    def __init__(self, disc: Discography, que: Queue, current: CurrentTrack, cred: Credits):
        self.discography: Discography = disc
        self.queue: Queue = que
        self.current: CurrentTrack = current
        self.credits: Credits = cred

    def current_track(self) -> Optional[Track]:
        """ Retrieves the currently playing track information
        :returns: The current track if one is playing
        :rtype: Track|None
        """
        track_id = self.current.current_track_id()
        track: Optional[Track] = None
        if track_id != "":
            track = self.discography.get_track(track_id)
        return track

    def next_track(self) -> Optional[Track]:
        """ Retrieves the next track in the queue.
        :returns: Next queued `Track` or `None`
        :rtype: Track|None
        """
        try:
            track_id = self.queue.peak()
        except queue.EmptyQueueException:
            return None
        return self.discography.get_track(track_id)

    def list_albums(self, page: Optional[Page] = None) -> List[Album]:
        """ Get the available albums
        :returns: List of `Album`s
        """
        return self.discography.get_albums(page)

    def list_album_tracks(self, album_id: str, page: Optional[Page] = None) -> List[Track]:
        """ Get the list of tracks in an album
        :param album_id: ID of the album to find tracks of
        :returns: list of `Track`s
        """
        return self.discography.get_album_tracks(album_id, page)

    def add_balance(self, amount: Charge):
        """ Add track credits
        :param amount: The amount of money that was deposited
        :type amount: Charge
        """
        # NOTE: we might want a currency conversion service here.
        # unless somewhere else is handling that.
        dollars: int = amount.amount
        high, dollars = divmod(dollars, 5)
        mid, dollars = divmod(dollars, 2)
        # NOTE: currently no thread safety.
        self.credits.add_credits((high * 18) + (mid * 7) + (3 * dollars))

    def get_balance(self) -> int:
        """ Returns the current credit balance
        """
        return self.credits.get_credits()

    def enqueue_track(self, track_id: str):
        """ Put the given track into the playback queue
        :param track_id: ID of the Track to play
        :raises NoCreditsException: If the user does not have enough funds available.
        :raises NotFoundException: If the given track id cannot be found
        """
        # validate the track exists
        self.discography.get_track(track_id)

        try:
            self.credits.remove_credits(1)
        except NotEnoughCredits as exc:
            raise NoCreditsException("not have enough funds available to queue track") from exc
        try:
            self.queue.enque(track_id)
        except:
            self.credits.add_credits(1)
            raise



def from_config(config: Config, disc: Discography, que: Queue, current: CurrentTrack,
                cred: Credits) -> Service:
    """ Constructs the service from the configuration options
    :param config: Configuration options
    :type config: Config
    :param disc: Discography repository
    :type disc: Discography
    :param queue: Playback queue
    :type queue: Queue
    :param current: Current track getter
    :type current: CurrentTrack
    """
    return Service(disc, que, current, cred)

__all__ = (
    "Album",
    "Track",
    "Page",
    "NoCreditsException",
)
