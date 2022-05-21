# data-cache

Repository with a few small helper functions for caching .csv files in the binary .feather format, making load times much faster (typically an order of magnitude) on subsequent runs. 

Not guaranteed to be stable between versions, and hence not intended for long-term storage.

There is an internal cache root, where cached files are stored (~/.cache/data_cache/cache_root by default). View the code example below for how to change that.

## Dependencies

```
python>=3.8
pandas
pyarrow
```

## Install

`pip install git+https://github.com/OlleLindgren/data-cache@main`

## Usage

This is useful when the same .csv file will be loaded multiple times, across different Python sessions.

```python
import datacache as cache

# Manually set directory for caches (not necessary)
# The cache root may also be set using the CACHE_ROOT environment variable.
cache.set_cache_root('/tmp/some-caching-directory')

# Recursively cache all csv files in directory and sub-directories
cache.cache_folder(directory)

# Cache all csv files in directory, but not sub-directories
cache.cache_folder(directory, recursive=False)

# Read from cache. If cache does not exist, read from csv, create cache, then read from cache. 
# This way, the result from cache.read is guaranteed to be exactly the same regardless of which method is used.
# cache.read is intended as a direct replacement for pd.read_csv, and supports the same keyword arguments.
df = cache.read(filename)

# Write df (pd.DataFrame) to cache
cache.write(df, filename)
```

`pandas.to_feather` is used under the hood, which introduces certain requirements on what files may be cached. Non-default (non-range) indexes will not work, and column datatypes are restricted to the native C datatypes. For these reasons, it works very well to replace `pd.read_csv()` with `cache.read()`, while replacing intermediary pd.DataFrame objects may be trickier.
