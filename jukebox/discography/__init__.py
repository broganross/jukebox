""" Repository of albums
"""

import json
import re
from token import OP
from typing import List
from typing import Optional
from typing import Protocol

from jukebox.service import Album
from jukebox.service import Page
from jukebox.service import Track
from jukebox.config import Config
from jukebox.config import ConfigurationException
from .exception import InvalidAlbumIdException
from .exception import InvalidTrackIdException
from .exception import NotFoundException


ALBUM_ID_REG = re.compile(r"^\d\d+$")
# NOTE: is it a safe assumption that an album won't have more than 99 tracks?
TRACK_ID_REG = re.compile(r"^\d\d+-\d\d$")


class Discography(Protocol):
    """ Interface contract for what a discography will provide
    """
    def get_albums(self, page: Optional[Page]) -> List[Album]:
        """ Retrieve a list of albums
        TODO: Needs a cursor for pagination
        :param page: pagination options
        :rtype page: Page
        :returns: List of `Album`s
        """

    def get_album_tracks(self, album_id: str, page: Optional[Page]) -> List[Track]:
        """ Get the tracks for a given album
        TODO: Maybe add cursor for pagination??
        :param album_id: Album id
        :type album_id: str
        :param page: Pagination options
        :rtype page: Page
        :returns: List of `Track`s
        :raises InvalidAlbumIdException: if the album_id is incorrectly formatted
        :raises NotFoundException: if the album was not found for the given album_id
        """

    def get_track(self, track_id: str) -> Track:
        """ Get a specific track by id
        :param track_id: Id of the track
        :type track_id: str
        :returns: The `Track`
        :raises InvalidTrackIdException: if the track_id is incorrectly formatted
        :raises NotFoundException: if the track was not found for the given id
        """


class JsonDiscography:
    """ Simple discography that reads from the sample JSON file
    :param url: Location of the discography
    :type url: str
    """
    def __init__(self, url: str):
        self.url = url
        file_path = self.url.replace("file://", "")
        self._albums: dict[str,Album] = {}
        # this all assumes a small json, obviously
        with open(file_path, "r", encoding="utf-8") as fo:
            albums = json.load(fo)["albums"]
        for index, data in enumerate(albums):
            album_id = f"{index+1:02d}"
            tracks: List[Track] = []
            for track_number, track_data in enumerate(data["songs"]):
                track = Track(
                    f"{album_id}-{track_number+1:02d}",
                    track_data["title"],
                    track_data["duration"],
                    f"file://{album_id}/{track_number+1:02d}.mp4"
                )
                tracks.append(track)

            self._albums[album_id] = Album(album_id, data["artist"], data["title"], tracks)

    def get_albums(self, page: Optional[Page] = None) -> List[Album]:
        """ Retrieve a list of albums
        TODO: Needs a cursor for pagination
        :returns: List of `Album`s
        """
        albums = sorted(self._albums.values(), key=lambda x: int(x.album_id))
        if page is not None:
            start = 0
            if page.cursor != "":
                start = int(page.cursor)
                if page.before:
                    start = max(start - (page.size + 1), 0)
            end = min(start + page.size, len(albums))
            albums = albums[start:end]
        return list(albums)

    def get_album_tracks(self, album_id: str, page: Optional[Page] = None) -> List[Track]:
        """ Returns the list of tracks contained in the album of 'album_id'
        :raises InvalidAlbumIdException: if the album_id is incorrectly formatted
        :raises NotFoundException: if the album was not found for the given album_id
        """
        if ALBUM_ID_REG.match(album_id) is None:
            raise InvalidAlbumIdException(f"{album_id} is an invalid album id")
        try:
            tracks = self._albums[album_id].tracks
        except KeyError as exc:
            raise NotFoundException(f"{album_id} album not found") from exc
        if page is not None:
            start = 0
            if page.cursor != "":
                start = int(page.cursor)
                if page.before:
                    start = max(start - (page.size + 1), 0)
            end = min(start + page.size, len(tracks))
            tracks = tracks[start:end]
        return tracks

    def get_track(self, track_id: str) -> Track:
        """ Get a specific track by its id
        :raises InvalidTrackIdException: if the track_id is incorrectly formatted
        :raises NotFoundException: if the track was not found for the given id
        """
        if TRACK_ID_REG.match(track_id) is None:
            raise InvalidTrackIdException(f"{track_id} is an invalid track id")
        spl = track_id.split("-")
        try:
            album = self._albums[spl[0]]
        except KeyError as exc:
            raise NotFoundException(f"{track_id} album not found") from exc
        index = int(spl[1]) - 1
        try:
            track = album.tracks[index]
        except IndexError as exc:
            raise NotFoundException(f"{track_id} track not found") from exc
        return track


def from_config(conf: Config) -> Discography:
    """ Constructs a Discography from the configuration options
    """
    url = conf.discography.url
    if url.startswith("file://"):
        if url.endswith(".json"):
            return JsonDiscography(url)
        # elif url.endswith(".sql"):
        #     return SqlDiscography(url)
    # elif src.startswith("postgres://"):
    #     return PostgresDiscography(
    #         url=url,
    #         username=conf.discography.user_name,
    #         passw=conf.discography.secret,
    #     )
    raise ConfigurationException("no discography defined")


__all__ = (
    "Discography",
    "ConfigurationException",
    "InvalidAlbumIdException",
    "InvalidTrackIdException",
    "NotFoundException"
)
