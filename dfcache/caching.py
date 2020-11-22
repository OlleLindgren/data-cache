import pandas as pd 
import os
import time
from termcolor import colored

def read_cache(filename, verbose=False):
    def _print(msg, opt_dir=None):
        _col = 'green'
        _dir_col = 'blue'
        if verbose and opt_dir is None:
            print(colored(msg, _col))
        elif verbose:
            print(colored(msg, _col) + ' ' + colored(opt_dir, _dir_col))
    
    t0 = time.time()
    _print('* Read request for', filename)

    _filedir, _ext = os.path.splitext(filename)

    # If file already in feather format, return file.
    if _ext == '.feather' and os.path.isfile(filename):
        result = pd.read_feather(_ext)
        t1 = time.time()
        _print(f'  * {(t1-t0)*1000:.3f} ms elapsed')
        return result

    _folder, _filename = os.path.split(_filedir)
    assert _folder[:4] == 'data'
    cache_folder = _folder[:4] + '_cache' + _folder[4:]
    feather_filename = os.path.join(cache_folder, _filename+'.feather')
    if not os.path.isdir(cache_folder):
        # Make cache folder
        _print('  * Cache folder created:', cache_folder)
        os.mkdir(cache_folder)
    if os.path.isfile(feather_filename):
        # Read cache
        _print('  * Reading cached file:', feather_filename)
        result = pd.read_feather(feather_filename)

        t1 = time.time()
        _print(f'  * {(t1-t0)*1000:.3f} ms elapsed')
        return result
    else:
        # Read csv, write cache, read cache
        if verbose:
            print(colored('  * No cache found, reading csv file: ', 'red')+ colored(filename, 'blue'))
        if _ext == '.tsv':
            result = pd.read_csv(filename, delimiter='\t')
        else:
            result = pd.read_csv(filename)
        expected_shape = result.shape
        _print('  * Saving to cache:', feather_filename)
        result.to_feather(feather_filename)
        _print('  * Reading cached file:', feather_filename)
        result = pd.read_feather(feather_filename)
        assert result.shape == expected_shape

        t1 = time.time()
        _print(f'  * {(t1-t0)*1000:.3f} ms elapsed')
        return result

def cache_files(*filenames):
    for filename in filenames:
        read_cache(filename)

def cache_folder(folder, extensions=('.tsv', '.csv'), recursive=True):
    print(colored('Caching request for folder ', 'yellow')+colored(folder, 'blue'))
    _t0 = time.time()
    _n_caches = 0
    for _f in os.listdir(folder):
        _full_f = os.path.join(folder, _f)
        if os.path.isfile(_full_f) and os.path.splitext(_full_f)[1] in extensions:
            read_cache(_full_f, verbose=True)
            _n_caches += 1
        elif os.path.isdir(_full_f) and recursive:
            _n_caches += cache_folder(_full_f, recursive=recursive)
    _dt = time.time() - _t0
    print(colored(f'Cached {_n_caches} files in ', 'yellow')+colored(folder, 'blue')+colored(f'. {_dt*1000:.0f} ms elapsed.', 'yellow'))
    return _n_caches

def read(filename):
    # Shorthand for read_cache(verbose=False)
    return read_cache(filename, False)

def write(file, filename):
    fn, fext = os.path.splitext(filename)
    if fext == '.feather':
        file.to_feather(os.path.join(fn, '.feather'))
    elif fext == '.csv':
        file.to_csv(filename)
        read_cache(filename)
    else:
        raise Exception(f'unknown extension: {fext}')
    pd.to_csv(filename)