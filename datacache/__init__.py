"""Reduce read times by caching .csv files and other pd.DataFrame data."""

# pylint: disable=redefined-builtin
from .caching import (
    cache_files,
    cache_folder,
    dir,
    file,
    fingerprint,
    get_cache_root,
    is_cached,
    read,
    set_age_diff_tol,
    set_cache_root,
    write,
)

version = "0.9.1"
