"""Cache csvs or pd.DataFrames."""
from __future__ import annotations

import datetime
import itertools
import os
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import pathvalidate
import pyarrow


class MutableModuleConstants:  # pylint: disable=too-few-public-methods
    """Internal class that exists only to make the cache root mutable module-wide."""

    # TODO there has to be a better way than this pylint: disable=fixme

    cache_root: str = os.getenv(
        "CACHE_ROOT",
        Path.home() / ".cache" / "data_cache" / "cache_root",
    )

    age_tol: datetime.timedelta = datetime.timedelta(days=7)


def set_cache_root(cache_root: Path) -> None:
    """Set the cache root.

    Args:
        cache_root (Path): New cache root
    """
    MutableModuleConstants.cache_root = cache_root


def get_cache_root() -> Path:
    """Get the cache root.

    Returns:
        Path: The cache root
    """
    return MutableModuleConstants.cache_root


def set_age_diff_tol(age_diff_tol: datetime.timedelta) -> None:
    """Set the max age of cached files that do not have a filesystem equivalent.

    If older cache files are encountered, they will be deleted.

    Args:
        age_diff_tol (datetime.timedelta): New max age.
    """
    MutableModuleConstants.age_diff_tol = age_diff_tol


def _get_cache_filepath(filename: Path) -> Path:
    """Get the cache location of a file.

    Args:
        filename (Path): File to get cache location for

    Returns:
        Path: Cache location of file
    """
    filename = Path(filename)
    if filename.is_absolute():
        common_root = Path(os.path.commonpath([get_cache_root(), filename]))
        filepath = os.path.relpath(filename, common_root)
    else:
        filepath = filename

    cache_path = get_cache_root() / filepath
    cache_path = cache_path.parent / f"{cache_path.stem}.feather"

    return pathvalidate.sanitize_filepath(cache_path, platform="auto")


def dir(path: Path) -> Path:  # pylint: disable=redefined-builtin
    """Get equivalent directory in cache.

    Args:
        path (Path): Path to find an equivalent directory for

    Returns:
        Path: Equivalent directory in cache
    """
    filepath = _get_cache_filepath(path)

    if path.is_file():
        return filepath.parent

    if path.is_dir():
        return filepath

    # Path does not exist

    if path.stem and path.suffix:
        return filepath.parent

    return filepath


def file(path: Path) -> Path:
    """Get equivalent directory in cache.

    Args:
        path (Path): Path to find an equivalent directory for

    Returns:
        Path: Equivalent directory in cache
    """
    return _get_cache_filepath(path)


def is_cached(filename: Path) -> bool:
    """Determine if a file is cached.

    Args:
        filename (Path): File to check

    Returns:
        bool: True if the file is cached
    """
    cache_filename = _get_cache_filepath(filename)
    return cache_filename.exists()


def _is_cache_outdated(filename: Path, cache_filename: Path) -> bool:
    """Determine if cache is outdated.

    If filename exists, then the cache is outdated if it has an earlier modification
    time than the filename.
    Otherwise, the cache is outdated if it is older than the age tolerance, which is
    7 days by default.

    Args:
        filename (Path): Filename as referenced by application
        cache_filename (Path): Cache filename

    Returns:
        bool: True if the cache is outdated
    """
    cache_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(cache_filename))
    if not filename.exists() and filename != cache_filename:
        return datetime.datetime.now() - cache_mtime > MutableModuleConstants.age_tol

    file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filename))

    return file_mtime > cache_mtime


def read(filename: Path, **kwargs) -> pd.DataFrame:
    """Read from cache if exists, otherwise read from csv and create cache.

    Args:
        filename (Path): Filename to read
        kwargs: Optional keyword arguments to pass to pd.read_csv(). Only used if not cached.

    Returns:
        pd.DataFrame: File contents
    """
    filename = Path(filename)

    cache_filename = _get_cache_filepath(filename)

    if cache_filename.exists():
        if _is_cache_outdated(filename, cache_filename):
            cache_filename.unlink()
        else:
            try:
                return pd.read_feather(cache_filename)
            except pyarrow.lib.ArrowInvalid:
                cache_filename.unlink()

    dataframe = pd.read_csv(filename, **kwargs)

    cache_filename.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_feather(cache_filename)

    return pd.read_feather(cache_filename)


def _hash_anything(arg: Any) -> int:
    try:
        return hash(arg)
    except TypeError:
        return hash(repr(arg))


def fingerprint(*args, **kwargs) -> int:
    """Create a unique fingerprint of some set of arguments.

    Returns:
        int: A unique fingerprint corresponding to the provided arguments
    """
    argument_iterator = itertools.chain(
        args,
        kwargs.keys(),
        kwargs.values(),
    )
    return hash(tuple(_hash_anything(argument) for argument in argument_iterator))


def cache_files(filenames: Iterable[str], **kwargs) -> int:
    """Cache a number of files.

    Args:
        filenames (Iterable[str]): Files to cache
        **kwargs: Optional keyword arguments to pass to pd.read_csv()

    Returns:
        int: The number of files that were cached
    """
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
    """Cache the contents of a folder.

    Args:
        folder (Path): Folder to cache contents of
        extensions (Iterable[str]): Extensions to cache. Defaults to (".tsv", ".csv").
        recursive (bool): If True (default), recursively traverses the folder.
        **kwargs: Optional keyword arguments to pass to pd.read_csv()

    Returns:
        int: The number of files that were cached
    """
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

    return cache_files(filenames, **kwargs)


def write(dataframe: pd.DataFrame, filename: str, **kwargs) -> None:
    """Write dataframe to cache.

    Args:
        dataframe (pd.DataFrame): DataFrame to cache
        filename (str): Filename to cache the dataframe under
        kwargs: Optional keyword arguments to pass to pd.to_feather()
    """
    cache_filename = _get_cache_filepath(filename)
    cache_filename.parent.mkdir(exist_ok=True, parents=True)

    dataframe.to_feather(cache_filename, **kwargs)
