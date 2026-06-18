import sys
from pathlib import Path

import pytest
from pyspark.sql import SparkSession

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.fixture(scope="session")
def spark():
    spark = (SparkSession.builder
        .master("local[1]")
        .appName("tmb-analysis-tests")
        .config("spark.sql.shuffle.partitions", "1")
        .getOrCreate())
    yield spark
    spark.stop()


@pytest.fixture
def gear_df(spark):
    rows = [
        ("Tent", "Shelter", 1200),
        ("Footprint", "Shelter", 300),
        ("Sleeping Bag", "Sleep", 900),
        ("Pad", "Sleep", 450),
        ("Stove", "Cooking", 150),
    ]
    return spark.createDataFrame(rows, ["Item Name", "Category", "weight"])
