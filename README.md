# data-cache

Repository with a few small helper functions for caching .csv files in the binary .feather format, making load times much faster (usually around 10x compared to .csv) on subsequent runs.  

Not guaranteed to be stable between versions, and hence not intended for long-term storage.

Cache files are stored in the CACHE_ROOT directory (.data-cache by default).

## Dependencies

```
python>=3.6
pandas
pyarrow
termcolor
```

## Install

`pip install git+https://github.com/OlleLindgren/data-cache@v0.3`

## Usage: Caching .csv files

```python
import datacache as cache

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
