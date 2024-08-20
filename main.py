
import logging
import sys
import time

from jukebox import config
from jukebox import credit
from jukebox import discography
from jukebox import log
from jukebox import queue
from jukebox import player
from jukebox import service
from jukebox.service.data import Charge

LOGGER = logging.getLogger(__name__)

def main():
    conf = config.Config()
    conf.parse_env()
    log.setup_logger(conf)
    LOGGER.info("starting test service")

    # create the components
    repo = discography.from_config(conf)
    que = queue.from_config(conf)
    play = player.from_config(conf, repo, que)
    cred = credit.from_config(conf)
    domain = service.from_config(conf, repo, que, play, cred)

    # testing interfaces, and playback queuing
    albums = domain.list_albums()
    tracks = domain.list_album_tracks(albums[0].album_id)
    domain.add_balance(Charge(8, "usd"))
    for i in range(9):
        tracks[i].duration = "0:03"
        domain.enqueue_track(tracks[i].track_id)

    for i in range(60):
        time.sleep(1)
        match i:
            case 20:
                LOGGER.info(domain.current_track())
                LOGGER.info(domain.next_track())

    play.stop()
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)