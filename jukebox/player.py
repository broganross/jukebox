""" Audio player
"""


import logging
import threading
import time
from datetime import datetime
from typing import Optional
from typing import Protocol

from jukebox import queue
from jukebox.config import Config
from jukebox.config import ConfigurationException
from jukebox.service import Track

LOGGER = logging.getLogger(__name__)


class Player(Protocol):
    """ Contract interface for what a constructed player will provide
    """
    def stop(self):
        """Tells the player to stop playback
        """

    def start(self):
        """Tells the player to start playback
        """

    def current_track_id(self) -> str:
        """Returns the track id of the song that is currently being played.
        """


class TrackFinder(Protocol):
    """ Interface for something that can get a Track from its id
    """
    def get_track(self, track_id: str) -> Track:
        """ Retrieve the track info by its id
        :raises InvalidTrackIdException: if the track_id is incorrectly formatted
        :raises NotFoundException: if the track was not found for the given id
        """


class Queue(Protocol):
    """ Interface for getting a track id from a queue
    """
    def deque(self) -> str:
        """ Get the next track id and remove it from the queue
        :raises EmptyQueueException: If the queue is empty
        """


class TestPlayer:
    """ Example player which just writes the track url to stdout

    :param queue: Queue storing the track ids to play
    :type queue: Queue
    :param finder: Interface to find track info from an id
    :type finder: TrackFinder
    :param current_id: The id of the currently playing track
    :type current_id: str
    :param task: thread which runs the "playback"
    :type task: threading.Thread

    """
    def __init__(self, que: Queue, finder: TrackFinder) -> None:
        self.queue: Queue = que
        self.finder: TrackFinder = finder
        self.current_id: str = ""
        self.task: Optional[threading.Thread] = None
        self._stopping: bool = False

    def stop(self):
        """ Tells playback to cease
        """
        self._stopping = True
        if self.task is not None:
            while self.task.is_alive():
                LOGGER.debug("waiting for thread to stop")
                time.sleep(1)
        self.task = None

    def start(self):
        """ Tells playback to start
        """
        self.task = threading.Thread(target=self._loop, daemon=True)
        self.task.start()

    def _loop(self) -> None:
        LOGGER.debug("starting loop")
        start: float = 0.0
        seconds: float = 0.0
        while self._stopping is False:
            if self.current_id != "":
                if datetime.now().timestamp() - start < seconds:
                    LOGGER.info("playing: %s", self.current_id)
                    time.sleep(1)
                    continue
                LOGGER.debug("playback complete")
                start = 0.0
                self.current_id = ""
                seconds = 0.0
            LOGGER.info("getting next track")
            try:
                track_id = self.queue.deque()
            except queue.EmptyQueueException:
                LOGGER.info("empty queue, wait")
                time.sleep(2)
            except Exception as e:
                LOGGER.error("deque exception %s", e)
            else:
                track = self.finder.get_track(track_id)
                for part in track.duration.split(":"):
                    seconds = seconds * 60.0 + float(part)

                start = datetime.now().timestamp()
                self.current_id = track_id

    def current_track_id(self) -> str:
        """ Returns the currently playing track id
        """
        return self.current_id


def from_config(conf: Config, finder: Optional[TrackFinder] = None,
                que: Optional[Queue] = None) -> Player:
    """ Constructs the appropriate Player based on the given Config
    :param conf: Configuration object
    :type conf: Config
    :param finder: A track finder
    :type finder: TrackFinder
    :param que: Track id que
    :rtype: Player
    """
    if conf.player.url == "local://test-player":
        # TODO: how do we resolve the optional, mypy
        player = TestPlayer(que, finder)
        player.start()
        return player
    raise ConfigurationException("no player defined")


__all__ = (
    "from_config",
    "ConfigurationException",
    "Player"
)
