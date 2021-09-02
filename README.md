# data-cache

Repository with a few small helper functions for caching .csv files in the binary .feather format, making load times much faster (usually around 10x compared to .csv) on subsequent runs.  

Not guaranteed to be stable between versions, and hence not intended for long-term storage.

There is an internal cache root, where cached files are stored (.data-cache by default). View the code example below for how to change that.

It is also possible to cache functions in ram, with the `mem_cache` function/decorator.

## Dependencies

```
python>=3.8
pandas
pyarrow
```

## Install

`pip install git+https://github.com/OlleLindgren/data-cache@v0.7`

## Usage: As a stand-in for pd.read_csv

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

## Usage: Caching to RAM

This is useful if the same function will be re-called multiple times with the same arguments.

```python
# Same as cache.read, but caches the result in RAM.
# If the underlying .feather object updates (gets a different modification time),
# this will reload.
df = cache.mem_read(filename)

# Cache any function in RAM
df = cache.mem_cache(pd.read_csv)(filename)

import random
@cache.mem_cache
def get_random_number(x: float):
    return random.random() * x

# The same as long as the arguments are the same
print(get_random_number(1.0))  # x
print(get_random_number(1.0))  # x
print(get_random_number(-1.0))  # y
print(get_random_number(-1.0))  # y
print(get_random_number(1.0))  # x
```

`pandas.to_feather` is used under the hood, which introduces certain requirements on what files may be cached. Non-default (range) indexes will not work, and column datatypes are restricted to the native C datatypes. For these reasons, it is recommended to fully replace `pd.read_csv()` with `cache.read()`.