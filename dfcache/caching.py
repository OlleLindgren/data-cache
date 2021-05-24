from typing import Iterable
import pandas as pd 
import os
from pathlib import Path

def __get_cache_filename(filename: str) -> str:
    
    _filedir, extension = os.path.splitext(filename)

    if extension == '.feather':
        return filename

    _folder, _filename = os.path.split(_filedir)

    cache_folder = _folder[:4] + '_cache' + _folder[4:]
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
    _n_caches = 0
    for filename in filenames:
        if not is_cached(filename):
            read(filename, **kwargs)
            _n_caches += 1
    return _n_caches
    
def cache_folder(folder: str, extensions: Iterable[str]=('.tsv', '.csv'), recursive: bool=True, **kwargs) -> int:
    filenames = (
        fn for fn in (os.walk if recursive else os.listdir)(folder) 
        if (
            os.path.splitext(fn)[1] in extensions
            and not is_cached(fn)))
    _n_caches = cache_files(filenames, **kwargs)
    return _n_caches

def write(df: pd.DataFrame, filename: str, **kwargs) -> None:
    _, extension = os.path.splitext(filename)
    assert extension == '.feather'
    df.to_feather(filename, **kwargs)
