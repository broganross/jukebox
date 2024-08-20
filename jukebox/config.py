""" Configuration options
"""

import logging
from dataclasses import dataclass
import os

LOGGER = logging.getLogger(__name__)


@dataclass
class ConfigurationException(Exception):
    """ Something went wrong when constructing a Queue from the Config
    """
    message: str


@dataclass
class Queue:
    """ Playback queue configuration options
    """
    # this can be used to define an internal or external queue
    url: str
    # maximum_size of the queue.
    max_size: int


@dataclass
class Player:
    """ Playback service configuration options
    """
    # Identifies which service to use in order to play the audio
    url: str


@dataclass
class Discography:
    """ Discorgraphy repository configuration options
    """
    url: str
    # these two could be turned into a more generic Authentication object
    user_name: str
    secret: str


@dataclass
class Credit:
    """ Credit repository configuration options
    """
    url: str


@dataclass
class HTTP:
    """ HTTP server configuration options
    """
    port: int
    host: str


@dataclass
class Logger:
    """ Logger configuration options
    """
    level: int
    # if you want to write logs somewhere specific
    # url: str


class Config:
    """ Configuration options for the jukebox

    :param discography: Repository of albums
    :type discography: Discography
    :param queue: Queue for tracks
    :type queue: Queue
    :param player: Playback service
    :type player: Player
    :param http: HTTP service options
    :type http: HTTP
    :param logger: Logging options
    :type logger: Logger
    """
    def __init__(self) -> None:
        self.discography: Discography = Discography("", "", "")
        self.queue: Queue = Queue("mem://in-memory-queue", 200)
        # NOTE: This would definitely not be the default player
        self.player: Player = Player(url="local://test-player")
        self.http: HTTP = HTTP(port=80, host="127.0.0.1")
        self.logger: Logger = Logger(level=logging.INFO)
        self.credits: Credit = Credit("mem://in-memory-store")

    def parse_env(self):
        """ Populate the configuration options by parsing the environment variables
        """
        for key, value in os.environ.items():
            if key.startswith("JUKEBOX") is False:
                continue
            spl = key.split("_")
            if len(spl) < 2:
                LOGGER.error(f"env var %s invalid format", key)
                continue
            match spl[1]:
                case "DISCOGRAPHY":
                    match spl[2]:
                        case "URL":
                            self.discography.url = value
                            # TODO: add parsing the URL for a username
                            # and password, if not alread set
                        case "USERNAME":
                            self.discography.user_name = value
                        case "SECRET":
                            self.discography.secret = value
                        case _:
                            LOGGER.error("unsupported configuration environment variable: %s", key)
                case "QUEUE":
                    match spl[2]:
                        case "URL":
                            self.queue.url = value
                        case "SIZE":
                            self.queue.max_size = float(value)
                        case _:
                            LOGGER.error("unsupported configuration environment variable: %s", key)

                case "PLAYER":
                    match spl[2]:
                        case "URL":
                            self.player.url = value
                        case _:
                            LOGGER.error("unsupported configuration environment variable: %s", key)
                # service level config
                case "HTTP":
                    match spl[2]:
                        case "PORT":
                            self.http.port = int(value)
                        case "HOST":
                            self.http.host = value
                        case _:
                            LOGGER.error("unsupported configuration environment variable: %s", key)
                case "CREDIT":
                    match spl[2]:
                        case "URL":
                            self.credits.url = value
                        case _:
                            LOGGER.error("unsupported configuration environment variable: %s", key)
                case _:
                    LOGGER.error("unsupported configuration environment variable: %s", key)


__all__ = (
    "Config",
    "ConfigurationException"
)
