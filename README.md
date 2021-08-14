# data-cache

Repository with a few small helper functions for caching .csv files in the binary .feather format, making load times much faster (usually around 10x compared to .csv) on subsequent runs.  

Not guaranteed to be stable between versions, and hence not intended for long-term storage.

There is an internal cache root, where cached files are stored (.data-cache by default). View the code example below for how to change that.

## Dependencies

```
python>=3.6
pandas
pyarrow
```

The package will work without `pyarrow`, but installing it is strongly recommended. In future versions, when `pyarrow` is supported for the arm64 Apple Silicon Macs, this dependency will become non-optional.

## Install

`pip install git+https://github.com/OlleLindgren/data-cache@v0.5.1`

## Usage: Caching .csv files

```python
import datacache as cache

# Manually set directory for caches (not necessary)
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

`pandas.to_feather` is used under the hood, which introduces certain requirements on what files may be cached. Non-default (range) indexes will not work, and column datatypes are restricted to the native C datatypes. This is normally not a problem for numeric data.
