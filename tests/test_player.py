
from dataclasses import dataclass
from typing import List

import pytest

from jukebox import player
from jukebox.config import Config
from jukebox.service import Track


@dataclass
class Finder:
    tracks: List[Track]

    def get_track(self, track_id: str) -> Track:
        return [t for t in self.tracks if t.track_id == track_id][0]


class TestFromConfig:
    def test_from_config(self):
        conf = Config()
        conf.player.url = "something://"
        with pytest.raises(player.ConfigurationException):
            player.from_config(conf, Finder(tracks=[]))


class TestTestPlayer:
    # I'm skipping some tests for this player because of dealing with the threading

    @pytest.fixture
    def test_current_track_id(self):
        player = player.TestPlayer()
        assert player.current_track_id is None
    