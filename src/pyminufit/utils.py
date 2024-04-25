"""
Some utility constructs.

"""

from __future__ import annotations

import collections
import logging
from typing import Any


class ClassLoggingMixin:
    """Mixin class that enables logging for instances of a specific class"""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialise the logger instance"""
        super().__init__(*args, **kwds)
        self.logger = logging.getLogger(self.__class__.__name__)

    def debug(self, msg: str) -> None:
        self.logger.debug(msg)

    def info(self, msg: str) -> None:
        self.logger.info(self, msg)

    def warn(self, msg: str) -> None:
        self.logger.warning(msg)

    def error(self, msg: str) -> None:
        self.logger.error(msg)

    def unknown_error(self) -> None:
        self.logger.error("Unknown Error occurred o_O")

    @staticmethod
    def setup_basic_config() -> None:
        """Setup basic logging configuration"""
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(name)-18s \t %(levelname)-8s %(message)s",
            datefmt="%m-%d %H:%M",
        )


class AttrDict(dict):  # type: ignore[type-arg]
    """Dictionary which items can also be addressed by attribute lookup in addition to item lookup"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__dict__ = self


def is_iterable(obj: Any) -> bool:
    """Check if an object is iterable

    Args:
        obj (object): Generic object

    Returns:
        True if is able to use python iterations

    """
    return isinstance(obj, collections.abc.Iterable)
