# file-caching
Repository for caching .csv files as .feather, making load times much faster (usually around 10x compared to .csv) on subsequent runs.

Not stable between versions. Dependent on pyarrow, which is also not stable between versions.

## Install
`pip install git+https://github.com/OlleLindgren/file-caching@v0.1.2`

## Usage 

```
import dfcache as cch

# Recursively cache all csv/tsv files in folder
cch.cache_folder(directory, recursive=True)

# Read from cache if cache exists, otherwise read csv/tsv and create cache
df = cch.read(filename)

# Write to cache
cch.write(df, filename)
```
