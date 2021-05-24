from typing import Iterable
import pandas as pd 
import os
from pathlib import Path

CACHE_ROOT = '.data-cache'

def __get_cache_filename(filename: str) -> str:
    
    basename, extension = os.path.splitext(filename)

    if extension == '.feather':
        return os.path.join(CACHE_ROOT, filename)

    return os.path.join(CACHE_ROOT, basename+'.feather')

def is_cached(filename: str) -> bool:
    feather_filename = __get_cache_filename(filename)
    return os.path.isfile(feather_filename)

def read(filename: str, **kwargs) -> pd.DataFrame:

    feather_filename = __get_cache_filename(filename)
    cache_folder, _ = os.path.split(feather_filename)

    if not os.path.isdir(cache_folder):
        # Make cache folder
        Path(cache_folder).mkdir(parents=True, exist_ok=True)

    # If file already in feather format, return file.
    if os.path.isfile(feather_filename):
        return pd.read_feather(feather_filename)
    else:
        # Read csv, write cache, read cache
        result = pd.read_csv(filename, **kwargs)
        expected_shape = result.shape
        result.to_feather(feather_filename)
        result = pd.read_feather(feather_filename)
        if result.shape != expected_shape:
            os.remove(expected_shape)
            assert result.shape == expected_shape, f"DataFrame shape from read_feather is different to read_csv: {result.shape} != {expected_shape}. \nCaching of {filename} at {feather_filename} failed."

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
    _, extension = os.path.splitext(filename)
    assert extension == '.feather', "File extension must be .feather"
    df.to_feather(os.path.join(CACHE_ROOT, filename), **kwargs)
