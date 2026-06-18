from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType
from pyspark.sql.window import Window


def main():
    spark = SparkSession.builder.appName("tmb-analysis").getOrCreate()

    df = (spark.table("workspace.default.tmb")
        .withColumn("weight", F.col("weight").cast(IntegerType()))
        .withColumn("weight_kg", F.round(F.col("weight") / 1000.0, 3))
        .withColumnRenamed("Item Name", "item_name")
    )

    summary = (df
        .groupBy("Category")
        .agg(
            F.count("item_name").alias("items"),
            F.round(F.sum("weight") / 1000.0, 2).alias("total_weight_kg"),
            F.round(F.avg("weight"), 0).alias("avg_weight_g")
        )
        .orderBy(F.desc("total_weight_kg"))
    )

    window = Window.partitionBy("Category").orderBy(F.desc("weight"))
    df_ranked = (df
        .withColumn("rank", F.rank().over(window))
        .filter(F.col("rank") == 1)
        .select("Category", "item_name", "weight")
    )

    (summary.write.format("delta")
        .mode("overwrite")
        .saveAsTable("workspace.default.tmb_gear_summary"))

    (df_ranked.write.format("delta")
        .mode("overwrite")
        .saveAsTable("workspace.default.tmb_gear_top_per_category"))

    print("Done. Wrote tmb_gear_summary and tmb_gear_top_per_category.")


if __name__ == "__main__":
    main()
