"""Cache csvs or pd.DataFrames"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable
import json
import dataclasses


import pyarrow.lib
import pandas as pd
from pathvalidate import sanitize_filepath


class _SettingsHandler:  # pylint: disable=too-few-public-methods
    """Internal class that exists only to make the cache root mutable module-wide."""

    # TODO there has to be a better way than this pylint: disable=fixme

    __cache_root: str = os.getenv(
        "CACHE_ROOT",
        Path.home() / ".cache" / "data_cache" / "cache_root",
    )

    @classmethod
    def _get_cache_root(cls):
        return cls.__cache_root

    @classmethod
    def _set_cache_root(cls, cache_root):
        """Set the cache root"""
        cls.__cache_root = Path(cache_root).absolute()

    @classmethod
    def _set_age_diff_tol(cls, seconds=0, days=0, hours=0, minutes=0) -> int:
        """Set max cache file age tolerance"""
        cls.age_tol = seconds + 60 * (minutes + 60 * (hours + 24 * days))
        return cls.age_tol


# pylint: disable=protected-access
set_cache_root = _SettingsHandler._set_cache_root
get_cache_root = _SettingsHandler._get_cache_root
set_age_diff_tol = _SettingsHandler._set_age_diff_tol
# pylint: enable=protected-access


def __get_cache_filepath(filename: Path) -> Path:
    """Get the cache location of a file"""

    if Path(filename).is_absolute():
        common_root = Path(os.path.commonpath([get_cache_root(), filename]))
        filepath = os.path.relpath(filename, common_root)
    else:
        filepath = filename

    cache_path = get_cache_root() / filepath
    cache_path = cache_path.parent / (cache_path.stem + ".feather")

    return Path(sanitize_filepath(cache_path, platform="auto"))


def dir(path: Path) -> Path:  # pylint: disable=redefined-builtin
    """Get equivalent directory in cache"""

    filepath = __get_cache_filepath(path)

    if path.is_file():
        return filepath.parent

    if path.is_dir():
        return filepath

    # Path does not exist

    if path.stem and path.suffix:
        return filepath.parent

    return filepath


def file(path: str) -> Path:
    """Get equivalent file in cache"""
    return __get_cache_filepath(path)


def is_cached(filename: Path) -> bool:
    """Is a filename cached"""
    cache_filename = __get_cache_filepath(filename)
    return cache_filename.exists()


def _is_cache_outdated(filename: Path, cache_filename: Path) -> bool:
    return os.path.getmtime(filename) > os.path.getmtime(cache_filename)


def read(filename: Path, **kwargs) -> pd.DataFrame:
    """Read from cache if exists, otherwise read from csv and create cache"""

    filename = Path(filename)

    cache_filename = __get_cache_filepath(filename)

    # Ensure filename or cache_filename exists
    if not filename.exists() and not cache_filename.exists():
        raise FileNotFoundError(
            f"Filename {filename!r} does not exist, nothing to read"
        )

    if cache_filename.exists():
        if filename.exists() and _is_cache_outdated(filename, cache_filename):
            cache_filename.unlink()
        else:
            try:
                return pd.read_feather(cache_filename)
            except pyarrow.lib.ArrowInvalid:
                print("WARNING: Found unusable cache file, discarding and re-creating.")
                cache_filename.unlink()

    cache_filename.parent.mkdir(parents=True, exist_ok=True)

    # Read csv, write cache, read cache
    result = pd.read_csv(filename, **kwargs)
    expected_shape = result.shape

    result.to_feather(cache_filename)
    result = pd.read_feather(cache_filename)

    if result.shape != expected_shape:
        cache_filename.unlink()
        if result.shape != expected_shape:
            raise RuntimeError(
                "DataFrame shape from cache read is different to read_csv: "
                f"{result.shape} != {expected_shape}. \n "
                f"Caching of {filename} at failed."
            )

    return result


def fingerprint(*args, **kwargs) -> int:
    """Return an integer fingerprint of arguments"""

    def jsonify(arg):
        try:
            return dataclasses.asdict(arg)
        except TypeError:
            return str(arg)

    return hash(
        json.dumps(
            {
                "args": [jsonify(arg) for arg in args],
                "kwargs": {
                    "keys": [jsonify(arg) for arg in kwargs],
                    "values": [jsonify(arg) for arg in kwargs.values()],
                },
            }
        ).encode("utf-8")
    )


def cache_files(filenames: Iterable[str], **kwargs) -> int:
    """Cache a number of files"""
    n_caches = 0
    for filename in filenames:
        if not is_cached(filename):
            read(filename, **kwargs)
            n_caches += 1
    return n_caches


def cache_folder(
    folder: Path,
    extensions: Iterable[str] = (".tsv", ".csv"),
    recursive: bool = True,
    **kwargs,
) -> int:
    """Cache the contents of a folder"""

    folder = Path(folder)

    if recursive:
        file_iterator = folder.rglob("*")
    else:
        file_iterator = folder.iterdir()

    filenames = (
        filename
        for filename in file_iterator
        if filename.is_file()
        and filename.suffix in extensions
        and not is_cached(filename)
    )

    n_caches = cache_files(filenames, **kwargs)

    return n_caches


def write(dataframe: pd.DataFrame, filename: str, **kwargs) -> None:
    """Write dataframe to cache."""
    # Figure out filename
    _cache_filename = __get_cache_filepath(filename)
    # If filename parent directory doesn't exist, create it
    _cache_filename.parent.mkdir(exist_ok=True, parents=True)
    # Write cache
    dataframe.to_feather(_cache_filename, **kwargs)
