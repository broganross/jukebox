""" Playback queue
"""

from threading import Lock
from dataclasses import dataclass
from typing import List
from typing import Protocol

from jukebox.config import Config
from jukebox.config import ConfigurationException


@dataclass
class EmptyQueueException(Exception):
    """ When the queue is empty but you tried to get something from it
    """
    message: str


class Queue(Protocol):
    """ Contract interface for what a constructed queue will provide
    """
    def enque(self, track_id: str):
        """ Adds a track_id to the queue
        """

    def deque(self) -> str:
        """ Remove the next track_id from the queue and return it
        :raises EmptyQueueException: if the queue is empty
        """

    def peak(self) -> str:
        """Returns the next track_id in the queue with removing it from the queue.
        :raises EmptyQueueException: if the queue is empty
        """


class ListQueue:
    """ Stores the track id queue in a list in memory

    :param lock: threading Lock
    :type lock: Lock
    :param queue:
    :type queue: List[str]
    """
    def __init__(self) -> None:
        self.lock = Lock()
        self.queue: List[str] = []

    def enque(self, track_id: str) -> None:
        """ Adds a track_id to the queue
        """
        with self.lock:
            self.queue.append(track_id)

    def deque(self) -> str:
        """ Remove the next track_id from the queue and return it
        :raises EmptyQueueException: if the queue is empty
        """
        with self.lock:
            try:
                track_id = self.queue.pop(0)
            except IndexError as exc:
                raise EmptyQueueException("queue is empty") from exc
        return track_id

    def peak(self) -> str:
        """Returns the next track_id in the queue with removing it from the queue.
        :raises EmptyQueueException: if the queue is empty
        """
        with self.lock:
            try:
                track_id = self.queue[0]
            except IndexError as exc:
                raise EmptyQueueException("queue is empty") from exc
        return track_id


def from_config(conf: Config) -> Queue:
    """ Constructs the appropriate Queue based on the configuration
    """
    if conf.queue.url == "mem://in-memory-queue":
        return ListQueue()
    raise ConfigurationException("unknown queue configuration")


__all__ = (
    "from_config",
    "ConfigurationException",
    "Queue"
)
