from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType
from pyspark.sql.window import Window

SOURCE_TABLE = "workspace.default.tmb"
SUMMARY_TABLE = "workspace.default.tmb_gear_summary"
TOP_TABLE = "workspace.default.tmb_gear_top_per_category"


def prepare(df: DataFrame) -> DataFrame:
    return (df
        .withColumn("weight", F.col("weight").cast(IntegerType()))
        .withColumn("weight_kg", F.round(F.col("weight") / 1000.0, 3))
        .withColumnRenamed("Item Name", "item_name")
    )


def build_summary(df: DataFrame) -> DataFrame:
    return (df
        .groupBy("Category")
        .agg(
            F.count("item_name").alias("items"),
            F.round(F.sum("weight") / 1000.0, 2).alias("total_weight_kg"),
            F.round(F.avg("weight"), 0).alias("avg_weight_g")
        )
        .orderBy(F.desc("total_weight_kg"))
    )


def build_top_per_category(df: DataFrame) -> DataFrame:
    window = Window.partitionBy("Category").orderBy(F.desc("weight"))
    return (df
        .withColumn("rank", F.rank().over(window))
        .filter(F.col("rank") == 1)
        .select("Category", "item_name", "weight")
    )


def main():
    spark = SparkSession.builder.appName("tmb-analysis").getOrCreate()

    df = prepare(spark.table(SOURCE_TABLE))
    summary = build_summary(df)
    df_ranked = build_top_per_category(df)

    (summary.write.format("delta")
        .mode("overwrite")
        .saveAsTable(SUMMARY_TABLE))

    (df_ranked.write.format("delta")
        .mode("overwrite")
        .saveAsTable(TOP_TABLE))

    print("Done. Wrote tmb_gear_summary and tmb_gear_top_per_category.")


if __name__ == "__main__":
    main()
