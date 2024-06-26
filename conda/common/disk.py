# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
"""Common disk utilities."""

from contextlib import contextmanager
from os import unlink

from ..auxlib.compat import Utf8NamedTemporaryFile
from ..deprecations import deprecated


@deprecated("24.3", "24.9", addendum="Use `tempfile` instead.")
@contextmanager
def temporary_content_in_file(content, suffix=""):
    # content returns temporary file path with contents
    fh = None
    path = None
    try:
        with Utf8NamedTemporaryFile(mode="w", delete=False, suffix=suffix) as fh:
            path = fh.name
            fh.write(content)
            fh.flush()
            fh.close()
            yield path
    finally:
        if fh is not None:
            fh.close()
        if path is not None:
            unlink(path)
