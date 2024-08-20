""" This gets us JSON formatted structured logging.  However, it's not easily
extendable.  It would be good to have a simple interface for adding any fields
to the JSON.  I found some examples of making message JSON encodable, but
I wasn't a fan of the interface.  I would want to make this better.  Or
investigate third party libs.
"""
import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Union

from jukebox.config import Config

JsonType = Union[None, int, float, str, bool, List["JsonType"], Dict[str, "JsonType"]]

_org_factory = logging.getLogRecordFactory()


class JsonEncoder(json.JSONEncoder):
    """ Custom encoder knows how to handle datetimes
    """
    def default(self, o: Any) -> JsonType:
        if isinstance(o, datetime):
            return o.timestamp()
        try:
            return super().default(o)
        except TypeError as exc:
            if "not JSON serializable" in str(exc):
                return str(o)
            raise


def record_factory(*args, **kwargs) -> logging.LogRecord:
    """ Extends the standard log record factory by adding a JSON encoded string 
    attribute to the record.
    """
    record = _org_factory(*args, **kwargs)
    data = {
        "level": record.levelname,
        "unixtime": record.created,
        "thread": record.thread,
        "process": record.process,
        "func_name": record.funcName,
        "lineno": record.lineno,
        "message": record.getMessage(),
    }
    if record.pathname:
        data["pathname"] = record.pathname
    if record.filename:
        data["filename"] = record.filename
    if record.exc_info:
        data["exception"] = record.exc_info
        data["traceback"] = traceback.format_exception(*record.exc_info)

    record.json_formatted = json.dumps(data, cls=JsonEncoder)
    record.exc_info = None
    record.exc_text = None
    return record

def setup_logger(conf: Config):
    """ Setup the logger based on the configuration options
    """
    logging.basicConfig(
        format="%(json_formatted)s",
        level=conf.logger.level,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logging.setLogRecordFactory(record_factory)

__all__ = ("setup_logger",)
