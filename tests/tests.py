import shutil
from pathlib import Path
import pandas as pd

import datacache as cache

# Define temporary cache folder, and set CACHE_ROOT to it
__TMP_CACHE = Path(__file__).parent / "tmp-cache"


def test_stuff():
    cache.set_cache_root(__TMP_CACHE)

    # Assert CACHE_ROOT is now the temporary cache folder
    assert not __TMP_CACHE.exists(), "Cache exists"
    assert cache.get_cache_root() == __TMP_CACHE, "Cache root not set successfully"
    print("[X] Set cache root")

    # Filename of test data
    test_filename = Path(__file__).parent / "test-data.csv"

    # Result of reading csv
    df_read_csv: pd.DataFrame = pd.read_csv(test_filename)

    # Result of cache.read
    read_1 = cache.read(test_filename)

    # Assert cache now exists
    assert __TMP_CACHE.exists(), "Cache root not created"
    print("[X] Cache root created")

    assert df_read_csv.equals(
        read_1
    ), "Result of cache.read not equal to initial dataframe"
    print("[X] Result of cache read equal to write")

    # Result of second cache.read
    read_2 = cache.read(test_filename)
    assert df_read_csv.equals(
        read_2
    ), "Second result of cache.read not equal to initial dataframe"
    assert read_1.equals(
        read_2
    ), "Second result of cache.read not equal to first result"
    print("[X] Result of subsequent read equal to initial dataframe")
    print("[X] Result of subsequent read equal to first read")

    # Test write
    write_filename = "qwerty.asdf"
    cache.write(df_read_csv, write_filename)
    write_read_df = cache.read(write_filename)
    assert df_read_csv.equals(
        write_read_df
    ), "Read result from file created by cache.write not equal to initial dataframe"
    print("[X] Read result from file created by cache.write equal to initial dataframe")

    # Delete cache folder if it did not exist before
    shutil.rmtree(__TMP_CACHE)

    print()
    print("[X] All tests passed.")


try:
    test_stuff()
finally:
    if __TMP_CACHE.exists():
        shutil.rmtree(__TMP_CACHE)
