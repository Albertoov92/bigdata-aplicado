from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType


appName = "Visor de pedidos Golbal A ficheiro" 
master = "local"
KAFKA_SERVERS = "kafkaserver:9092"
TOPIC = "pedidos"

spark = SparkSession.builder \
    .master(master) \
    .appName(appName) \
    .getOrCreate()

# Fixar o nivel de rexistro/log a ERROR
spark.sparkContext.setLogLevel("ERROR")

# Stream de lectura
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_SERVERS) \
    .option("subscribe", TOPIC) \
    .load()

#procesado

df = df.selectExpr("CAST(value AS STRING)")

#Stream de escritura

schema= StructType(
	[
		StructField("tenda", StringType(), True),
		StructField("marca", StringType(), True),
		StructField("color", StringType(), True),
		StructField("cantidade", StringType(), True)
	]
)

df2= df.withColumn("value", from_json("value", schema)).select(col("value.*"))

df2.createOrReplaceTempView("pedidos")
df_sql = spark.sql("SELECT tenda, marca, color, cantidade FROM pedidos  ")

query = df_sql \
        .writeStream \
        .outputMode("append") \
        .format("csv") \
        .option("truncate", False) \
	.option("checkpointLocation", "/home/hduser/Descargas/") \
	.option("path", "/home/hduser/Descargas/Output/") \
	.trigger(processingTime="15 seconds") \
        .start()

query.awaitTermination()

