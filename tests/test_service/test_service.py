
import pytest

from typing import List

from jukebox import discography
from jukebox import service
from jukebox.config import Config
from jukebox.credit import InMemory
from jukebox.discography import JsonDiscography
from jukebox.queue import ListQueue
from jukebox.service import Charge
from jukebox.service import Page
from jukebox.service import Service
from jukebox.service import Track


@pytest.fixture
def mock_disc(tmp_path):
    content = """{
"albums": [
  {
    "title": "The Joshua Tree",
    "artist": "U2",
    "songs": [
      {
        "title": "Where The Streets Have No Name",
        "duration": "5:37"
      },
      {
        "title": "I Still Haven't Found What I'm Looking For",
        "duration": "4:37"
      },
      {
        "title": "With Or Without You",
        "duration": "4:56"
      },
      {
        "title": "Bullet The Blue Sky",
        "duration": "4:32"
      },
      {
        "title": "Running To Stand Still",
        "duration": "4:17"
      },
      {
        "title": "Red Hill Mining Town",
        "duration": "4:53"
      }
    ]
  },
  {
    "title": "Lateralus",
    "artist": "Tool",
    "songs": [
      {
        "title": "The grudge",
        "duration": "8:36"
      },
      {
        "title": "Eon Blue Apocalypse",
        "duration": "1:07"
      },
      {
        "title": "The patient",
        "duration": "7:13"
      }
    ]
  },
  {
    "title": "Animals",
    "artist": "Pink Floyd",
    "songs": [
      {
        "title": "Pigs on the Wing, Part 1",
        "duration": "1.25"
      },
      {
        "title": "Dogs",
        "duration": "17:05"
      }
    ]
  }
]
}"""
    json_path = tmp_path / "test.json"
    json_path.write_text(content)
    return JsonDiscography(f"file://{json_path}")

class MockCurrent:
    """ testing current track getter
    """
    def __init__(self, que: List[str]):
        self.queue = que

    def current_track_id(self) -> str:
        try:
            return self.queue[0]
        except IndexError:
            return ""


def test_from_config(mock_disc):
    conf = Config()
    que = ListQueue()
    cur = MockCurrent(que.queue)
    cred = InMemory()
    service.from_config(conf, mock_disc, que, cur, cred)


class TestService:
    @pytest.fixture(autouse=True)
    def setup_method(self, request, mock_disc):
        que = ListQueue()
        cur = MockCurrent(que.queue)
        cred = InMemory()
        self.serv = Service(mock_disc, que, cur, cred)

    def test_current_track(self):
        assert self.serv.current_track() is None
        self.serv.add_balance(Charge(1.0, "usd"))
        self.serv.enqueue_track("01-02")

        got = self.serv.current_track()
        expect = Track(
            "01-02",
            "I Still Haven't Found What I'm Looking For",
            "4:37",
            "file://01/02.mp4"
        )
        assert expect == got

    def test_next_track(self):
        assert self.serv.next_track() is None
        self.serv.add_balance(Charge(1.0, "usd"))
        self.serv.enqueue_track("01-02")

        got = self.serv.next_track()
        expect = Track(
            "01-02",
            "I Still Haven't Found What I'm Looking For",
            "4:37",
            "file://01/02.mp4"
        )
        assert expect == got

    def test_list_albums(self):
        assert len(self.serv.list_albums()) == 3
        page = Page("02", 1, False)
        albums = self.serv.list_albums(page)
        assert len(albums) == 1
        assert albums[0].album_id == "03"

        page.before = True
        albums = self.serv.list_albums(page)
        assert len(albums) == 1
        assert albums[0].album_id == "01"

    def test_list_album_tracks(self):
        assert len(self.serv.list_album_tracks("02")) == 3

    def test_add_balance(self):
        assert self.serv.get_balance() == 0
        self.serv.add_balance(Charge(8.0, "usd"))
        assert self.serv.get_balance() == 28
    
    def test_enqueue_track(self):
        with pytest.raises(discography.NotFoundException):
            self.serv.enqueue_track("05-20")

        with pytest.raises(service.NoCreditsException):
            self.serv.enqueue_track("02-01")
        self.serv.add_balance(Charge(1.0, "usd"))

        self.serv.enqueue_track("02-01")
        assert self.serv.queue.peak() == "02-01"
