import pandas as pd 
import os
import time
from termcolor import colored

def read_cache(_d, _verbose=False):
    def _print(msg, opt_dir=None):
        _col = 'green'
        _dir_col = 'blue'
        if _verbose and opt_dir is None:
            print(colored(msg, _col))
        elif _verbose:
            print(colored(msg, _col) + ' ' + colored(opt_dir, _dir_col))
    
    t0 = time.time()
    _print('* Read request for', _d)

    _filedir, _ext = os.path.splitext(_d)
    _folder, _filename = os.path.split(_filedir)
    assert _folder[:4] == 'data'
    _cache_folder = _folder[:4] + '_cache' + _folder[4:]
    _d_feather = os.path.join(_cache_folder, _filename+'.feather')
    if not os.path.isdir(_cache_folder):
        # Make cache folder
        _print('  * Cache folder created:', _cache_folder)
        os.mkdir(_cache_folder)
    if os.path.isfile(_d_feather):
        # Read cache
        _print('  * Reading cached file:', _d_feather)
        _result = pd.read_feather(_d_feather)

        t1 = time.time()
        _print(f'  * {(t1-t0)*1000:.3f} ms elapsed')
        return _result
    else:
        # Read csv, write cache, read cache
        if _verbose:
            print(colored('  * No cache found, reading csv file: ', 'red')+ colored(_d, 'blue'))
        if _ext == '.tsv':
            _result = pd.read_csv(_d, delimiter='\t')
        else:
            _result = pd.read_csv(_d)
        _shape = _result.shape
        _print('  * Saving to cache:', _d_feather)
        _result.to_feather(_d_feather)
        _print('  * Reading cached file:', _d_feather)
        _result = pd.read_feather(_d_feather)
        assert _shape == _result.shape

        t1 = time.time()
        _print(f'  * {(t1-t0)*1000:.3f} ms elapsed')
        return _result

def cache_files(*_files):
    for _f in _files:
        read_cache(_f)

def cache_folder(_folder, _extensions=('.tsv', '.csv'), _recursive=True):
    print(colored('Caching request for folder ', 'yellow')+colored(_folder, 'blue'))
    _t0 = time.time()
    _n_caches = 0
    for _f in os.listdir(_folder):
        _full_f = os.path.join(_folder, _f)
        if os.path.isfile(_full_f) and os.path.splitext(_full_f)[1] in _extensions:
            read_cache(_full_f, _verbose=True)
            _n_caches += 1
        elif os.path.isdir(_full_f) and _recursive:
            _n_caches += cache_folder(_full_f, _recursive=_recursive)
    _dt = time.time() - _t0
    print(colored(f'Cached {_n_caches} files in ', 'yellow')+colored(_folder, 'blue')+colored(f'. {_dt*1000:.0f} ms elapsed.', 'yellow'))
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