
import pytest

from jukebox import discography
from jukebox.config import Config
from jukebox.discography import JsonDiscography

class TestFromConfig:
    def test_config_error(self):
        conf = Config()
        conf.discography.url = "nothing"
        with pytest.raises(discography.ConfigurationException):
            discography.from_config(conf)

    def test_json_file(self, tmp_path):
        conf = Config()
        conf.discography.url = "file://some.json"
        with pytest.raises(FileNotFoundError):
            discography.from_config(conf)

        data_path = tmp_path / "test.json"
        data_path.write_text("""{"albums":[]}""")
        conf.discography.url = f"file://{data_path}"
        disc = discography.from_config(conf)
        assert disc.url == f"file://{data_path}"
        assert len(disc.get_albums()) == 0

class TestJsonDiscography:
    @pytest.fixture
    def repo(self, tmp_path):
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
]}"""
        json_path = tmp_path / "test.json"
        json_path.write_text(content)
        return JsonDiscography(f"file://{json_path}")
    
    def test_get_albums(self, repo):
        albums = repo.get_albums()
        assert len(albums) == 3

    def test_get_album_tracks(self, repo):
        bad = ["a", "1"]
        for b in bad:
            with pytest.raises(discography.InvalidAlbumIdException):
                repo.get_album_tracks(b)
        with pytest.raises(discography.NotFoundException):
            repo.get_album_tracks("55")
        tracks = repo.get_album_tracks("01")
        assert len(tracks) == 6

    def test_get_track(self, repo):
        bad = ["a", "10", "1-", "1-01", "1-1"]
        for b in bad:
            with pytest.raises(discography.InvalidTrackIdException):
                repo.get_track(b)
        with pytest.raises(discography.NotFoundException, match="10-01 album not found"):
            repo.get_track("10-01")

        with pytest.raises(discography.NotFoundException, match="01-50 track not found"):
            repo.get_track("01-50")
        repo.get_track("01-03")
