
import pytest

from jukebox import credit
from jukebox.config import Config, ConfigurationException
from jukebox.credit import InMemory
from jukebox.credit import NotEnoughCredits


class TestInMemory:
    @pytest.fixture
    def in_mem(self):
        return InMemory()
    
    def test_get_credits(self, in_mem):
        assert in_mem.get_credits() == 0
        in_mem.add_credits(10)
        assert in_mem.get_credits() == 10

    def test_add_credits(self, in_mem):
        assert in_mem.get_credits() == 0
        in_mem.add_credits(5)
        assert in_mem.get_credits() == 5

    def test_remove_credits(self, in_mem):
        with pytest.raises(NotEnoughCredits):
            in_mem.remove_credits(1)
        in_mem.add_credits(1000)
        with pytest.raises(NotEnoughCredits):
            in_mem.remove_credits(1001)
        in_mem.remove_credits(1000)
        assert in_mem.get_credits() == 0

def test_from_config():
    conf = Config()
    cred = credit.from_config(conf)
    assert isinstance(cred, InMemory)

    conf.credits.url = ""
    with pytest.raises(ConfigurationException):
        credit.from_config(conf)
