from __future__ import annotations

import importlib.metadata

import pyminufit as m


def test_version():
    assert importlib.metadata.version("pyminufit") == m.__version__
