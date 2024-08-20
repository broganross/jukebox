""" Credit repository
"""

from dataclasses import dataclass
from threading import Lock
from typing import Protocol

from jukebox.config import Config
from jukebox.config import ConfigurationException

@dataclass
class NotEnoughCredits(Exception):
    """ When there's not enough credits to be removed
    """
    message: str


class CreditRepo(Protocol):
    """ Interface contract for what a credit repository will provide
    """
    def add_credits(self, credit: int):
        """ Add some number of credits to storage
        :param credits: the number of credits to add
        :type credits: int
        """

    def remove_credits(self, credit: int):
        """ Remove some number of credits from storage
        :param credits: Number of credits to remove
        :type credits: int
        """

    def get_credits(self) -> int:
        """ Return the number of available credits
        :returns: The number of credits
        :rtype: int
        """


class InMemory:
    """ Just stores the credit count in memory
    """
    def __init__(self) -> None:
        self.lock: Lock = Lock()
        self._credits: int = 0

    def add_credits(self, credit: int):
        """ Add some number of credits to storage
        :param credit: the number of credits to add
        :type credit: int
        """
        with self.lock:
            self._credits += credit

    def get_credits(self) -> int:
        """ Return the number of available credits
        :returns: The number of credits
        :rtype: int
        """
        with self.lock:
            return self._credits

    def remove_credits(self, credit: int):
        """ Remove some number of credits from storage
        :param credit: Number of credits to remove
        :type credit: int
        """
        with self.lock:
            if self._credits - credit < 0:
                raise NotEnoughCredits("no enough credits are available")
            self._credits -= credit


def from_config(config: Config) -> CreditRepo:
    """ Construct a credit repository from the configuration options
    :param conf: Configuration options
    :type conf: Config
    :rtype: CreditRepo
    """
    if config.credits.url == "mem://in-memory-store":
        return InMemory()
    raise ConfigurationException("unknown credit repository configuration")

__all__ = (
    "CreditRepo",
    "from_config",
    "NotEnoughCredits"
)
