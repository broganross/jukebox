
import pytest

from jukebox.config import Config
from jukebox import queue


class TestFromConfig:
    def test_unknown_config(self):
        conf = Config()
        conf.queue.url = "unknown://thing"
        with pytest.raises(queue.ConfigurationException):
            queue.from_config(conf)

    def test_list_queue(self):
        conf = Config()
        conf.queue.url = "mem://in-memory-queue"
        que = queue.from_config(conf)
        assert isinstance(que, queue.ListQueue)


class TestListQueue:
    @pytest.fixture
    def que(self):
        return queue.ListQueue()

    def test_enque(self, que):
        track_id = "01-01"
        que.enque(track_id)
        assert len(que.queue) == 1

    def test_deque(self, que):
        with pytest.raises(queue.EmptyQueueException):
            que.deque()

        que.enque("01-01")
        que.enque("01-02")
        que.enque("02-03")
        assert que.deque() == "01-01"
        assert que.deque() == "01-02"
        assert que.deque() == "02-03"

    def test_peak(self, que):
        with pytest.raises(queue.EmptyQueueException):
            que.peak()
        
        que.enque("01-01")
        que.enque("02-01")
        assert que.peak() == "01-01"
        assert que.peak() == "01-01"
