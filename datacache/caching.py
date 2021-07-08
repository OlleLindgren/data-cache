import os
import warnings
from typing import Iterable
import pandas as pd 
from pathlib import Path

class __setttings_handler:
    __cache_root: str = '.data-cache'
    @classmethod
    def get_cache_root(cls):
        return cls.__cache_root
    @classmethod
    def set_cache_root(cls, cache_root):
        cls.__cache_root=cache_root

set_cache_root = __setttings_handler.set_cache_root
get_cache_root = __setttings_handler.get_cache_root

try:
    # If pyarrow available, write as feather
    import pyarrow
    CACHE_FORMAT = '.feather'
except ImportError:
    CACHE_FORMAT = '.pickle'
    warnings.warn((
        'pyarrow does not seem to be available, falling back to caching with pickle. '
        'Installing pyarrow is strongly recommended, and will non-optional '
        'in future versions when it is supported on the M1 macs'
    ))

def __get_cache_filepath(filename: str) -> str:
    
    basename, extension = os.path.splitext(filename)
    if os.path.isabs(filename):
        common_root = os.path.commonpath([get_cache_root(), filename])
    else:
        common_root = get_cache_root()
    
    rel_filepath = os.path.relpath(basename+CACHE_FORMAT, start=common_root)

    return os.path.join(get_cache_root(), rel_filepath)

def is_cached(filename: str) -> bool:
    cache_filename = __get_cache_filepath(filename)
    return os.path.isfile(cache_filename)

def read(filename: str, **kwargs) -> pd.DataFrame:

    cache_filename = __get_cache_filepath(filename)
    cache_folder, _ = os.path.split(cache_filename)

    if not os.path.isdir(cache_folder):
        # Make cache folder
        Path(cache_folder).mkdir(parents=True, exist_ok=True)

    # If file already in feather format, return file.
    if os.path.isfile(cache_filename):
        if CACHE_FORMAT=='.feather':
            return pd.read_feather(cache_filename)
        else:
            return pd.read_pickle(cache_filename)
    else:
        # Read csv, write cache, read cache
        result = pd.read_csv(filename, **kwargs)
        expected_shape = result.shape
        if CACHE_FORMAT=='.feather':
            result.to_feather(cache_filename)
            result = pd.read_feather(cache_filename)
        else:
            result.to_pickle(cache_filename)
            result = pd.read_pickle(cache_filename)
        if result.shape != expected_shape:
            os.remove(expected_shape)
            assert result.shape == expected_shape, f"DataFrame shape from cache read is different to read_csv: {result.shape} != {expected_shape}. \nCaching of {filename} at {cache_filename} failed."

        return result

def cache_files(filenames: Iterable[str], **kwargs) -> int:
    n_caches = 0
    for filename in filenames:
        if not is_cached(filename):
            read(filename, **kwargs)
            n_caches += 1
    return n_caches
    
def cache_folder(folder: str, extensions: Iterable[str]=('.tsv', '.csv'), recursive: bool=True, **kwargs) -> int:
    filter = lambda filename: os.path.splitext(filename)[1] in extensions and not is_cached(filename)
    
    if recursive:
        def make_recursive_iterator():
            for root, _, files in os.walk(folder):
                for f in files:
                    yield os.path.join(root, f)
        file_iterator = make_recursive_iterator()
    else:
        file_iterator = (fn for fn in os.listdir(folder) if filter(fn))
        
    filenames = (
        fn
        for fn in file_iterator
        if filter(fn))
    
    n_caches = cache_files(filenames, **kwargs)

    return n_caches

def write(df: pd.DataFrame, filename: str, **kwargs) -> None:
    _cache_filename = __get_cache_filepath(filename)
    if CACHE_FORMAT=='.feather':
        df.to_feather(_cache_filename, **kwargs)
    else:
        df.to_pickle(_cache_filename, **kwargs)
