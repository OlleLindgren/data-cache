import hashlib
import os
from pathlib import Path
from typing import Iterable

from pyarrow.lib import ArrowInvalid
import pandas as pd
from pathvalidate import sanitize_filepath


class __setttings_handler:
    __cache_root: str = os.getenv('CACHE_ROOT', '.data-cache')
    __age_tol: int = 0

    @classmethod
    def get_cache_root(cls):
        return os.path.abspath(cls.__cache_root)

    @classmethod
    def set_cache_root(cls, cache_root):
        """Set the cache root"""
        cls.__cache_root = cache_root

    @classmethod
    def set_age_diff_tol(cls, seconds=0, days=0, hours=0, minutes=0) -> int:
        """Set max cache file age tolerance"""
        cls.age_tol = seconds + 60 * (minutes + 60 * (hours + 24 * days))
        return cls.age_tol


set_cache_root = __setttings_handler.set_cache_root
get_cache_root = __setttings_handler.get_cache_root
set_age_diff_tol = __setttings_handler.set_age_diff_tol


def __get_cache_filepath(filename: str) -> Path:
    """Get the cache location of a file"""

    basename, _ = os.path.splitext(filename)
    if os.path.isabs(filename):
        common_root = os.path.commonpath([get_cache_root(), filename])
    else:
        common_root = get_cache_root()

    rel_filepath = os.path.relpath(basename + '.feather', start=common_root)

    result = os.path.join(get_cache_root(), rel_filepath)

    return Path(sanitize_filepath(result, platform='auto'))


def dir(path: str) -> Path:
    """Get equivalent directory in cache"""
    _, filename = os.path.split(path)

    if filename:  # TODO fix; this won't work as intended
        # If file
        return __get_cache_filepath(path).parent

    # If directory
    return __get_cache_filepath(os.path.join(path, 'tmp')).parent


def file(path: str) -> Path:
    """Get equivalent file in cache"""
    return __get_cache_filepath(path)


def is_cached(filename: str) -> bool:
    """Is a filename cached"""
    cache_filename = __get_cache_filepath(filename)
    return os.path.isfile(cache_filename)


def read(filename: str, **kwargs) -> pd.DataFrame:
    """Read from cache if exists, otherwise read from csv and create cache"""

    cache_filename = __get_cache_filepath(filename)

    # Ensure filename or cache_filename exists
    if not Path(filename).exists() and not cache_filename.exists():
        raise FileNotFoundError(
            f"Filename '{filename}' does not exist, nothing to read")

    cache_filename.parent.mkdir(parents=True, exist_ok=True)

    # If file already in feather format, and modification time of underlying file not too old return file.
    if cache_filename.exists():
        if not Path(filename).exists() or os.path.getmtime(
                cache_filename) >= os.path.getmtime(filename):
            try:
                return pd.read_feather(cache_filename)
            except ArrowInvalid:
                print(
                    "WARNING: Found unusable cache file, discarding and re-creating."
                )
                cache_filename.unlink()

    # Read csv, write cache, read cache
    result = pd.read_csv(filename, **kwargs)
    expected_shape = result.shape

    result.to_feather(cache_filename)
    result = pd.read_feather(cache_filename)

    if result.shape != expected_shape:
        cache_filename.unlink()
        assert result.shape == expected_shape, \
            "DataFrame shape from cache read is different to read_csv: " \
            f"{result.shape} != {expected_shape}. \n " \
            f"Caching of {filename} at failed."

    return result


def fingerprint(*args, **kwargs) -> int:
    """Return an integer fingerprint of arguments"""
    import json
    import dataclasses

    def jsonify(arg):
        try:
            return dataclasses.asdict(arg)
        except TypeError:
            return str(arg)

    return hashlib.md5(
        json.dumps({
            "args": list(map(jsonify, args)),
            "kwargs": {
                "keys": list(map(jsonify, kwargs.keys())),
                "values": list(map(jsonify, kwargs.values()))
            }
        }).encode('utf-8')).hexdigest()


def cache_files(filenames: Iterable[str], **kwargs) -> int:
    """Cache a number of files"""
    n_caches = 0
    for filename in filenames:
        if not is_cached(filename):
            read(filename, **kwargs)
            n_caches += 1
    return n_caches


def cache_folder(folder: str,
                 extensions: Iterable[str] = ('.tsv', '.csv'),
                 recursive: bool = True,
                 **kwargs) -> int:
    """Cache the contents of a folder"""
    filter = lambda filename: os.path.splitext(filename)[
        1] in extensions and not is_cached(filename)

    if recursive:

        def make_recursive_iterator():
            for root, _, files in os.walk(folder):
                for f in files:
                    yield os.path.join(root, f)

        file_iterator = make_recursive_iterator()
    else:
        file_iterator = (fn for fn in os.listdir(folder) if filter(fn))

    filenames = (fn for fn in file_iterator if filter(fn))

    n_caches = cache_files(filenames, **kwargs)

    return n_caches


def write(df: pd.DataFrame, filename: str, **kwargs) -> None:
    """Write dataframe to cache."""
    # Figure out filename
    _cache_filename = __get_cache_filepath(filename)
    _cache_folder = Path(_cache_filename).parent
    # If filename parent directory doesn't exist, create it
    if not os.path.isdir(_cache_folder):
        os.makedirs(_cache_folder)
    # Write cache
    df.to_feather(_cache_filename, **kwargs)
