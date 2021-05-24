from typing import Iterable
import pandas as pd 
import os
from pathlib import Path

def __get_cache_filename(filename: str) -> str:
    
    filedir, extension = os.path.splitext(filename)

    if extension == '.feather':
        return filename

    folder, _filename = os.path.split(filedir)

    cache_folder = folder[:4] + '_cache' + folder[4:]
    return os.path.join(cache_folder, _filename+'.feather')

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
        assert result.shape == expected_shape

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
    assert extension == '.feather'
    df.to_feather(filename, **kwargs)
