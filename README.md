# data-cache

Repository with a few small helper functions for caching .csv files in the binary .feather format, making load times much faster (usually around 10x compared to .csv) on subsequent runs.  

Not guaranteed to be stable between versions, and hence not intended for long-term storage. Dependent on pyarrow, which is also not guaranteed to be stable between versions.

## Dependencies

```
python>=3.6
pandas
pyarrow
termcolor
```

## Install

`pip install git+https://github.com/OlleLindgren/data-cache@v0.3`

## Usage: Caching .csv and .tsv-files

```python
import dfcache as cch

# Recursively cache all csv/tsv files in directory and sub-directories
cch.cache_folder(directory)

# Cache all csv/tsv files in directory, but not sub-directories
cch.cache_folder(directory, recursive=False)

# Read from cache if cache exists, otherwise read csv/tsv and create cache
df = cch.read(filename)

# Write df (pandas.DataFrame instance) to cache
cch.write(df, filename)
```

`pandas.to_feather` is used under the hood, which introduces certain requirements on what files may be cached. Non-default (range) indexes will not work, and column datatypes are restricted to the native C datatypes.
