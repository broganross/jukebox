
from http.client import HTTP_PORT
import os

from jukebox.config import Config


class TestConfig:
    def setup_method(self, _):
        self.env = dict(os.environ)

    def teardown_method(self, _):
        os.environ = self.env

    def test_defaults(self):
        conf = Config()
        assert conf.discography.url == ""
        assert conf.discography.user_name == ""
        assert conf.discography.secret == ""
        assert conf.queue.url == "mem://in-memory-queue"
        assert conf.queue.max_size == 200
        assert conf.player.url == "local://test-player"
        assert conf.http.port == 80
        assert conf.http.host == "127.0.0.1"

    def test_parse_env(self,):
        env = dict(os.environ)
        os.environ["JUKEBOX_DISCOGRAPHY_URL"] = "disc-url"
        os.environ["JUKEBOX_DISCOGRAPHY_USERNAME"] = "disc-user"
        os.environ["JUKEBOX_DISCOGRAPHY_SECRET"] = "disc-secret"
        os.environ["JUKEBOX_QUEUE_URL"] = "queue-url"
        os.environ["JUKEBOX_QUEUE_SIZE"] = "41"
        os.environ["JUKEBOX_PLAYER_URL"] = "player-url"
        os.environ["JUKEBOX_HTTP_PORT"] = "118"
        os.environ["JUKEBOX_HTTP_HOST"] = "http-host"

        conf = Config()
        conf.parse_env()

        assert conf.discography.url == "disc-url"
        assert conf.discography.user_name == "disc-user"
        assert conf.discography.secret == "disc-secret"
        assert conf.queue.url == "queue-url"
        assert conf.queue.max_size == 41
        assert conf.player.url == "player-url"
        assert conf.http.port == 118
        assert conf.http.host == "http-host"
