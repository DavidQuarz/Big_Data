from pyspark.sql import SparkSession
from hdfs import InsecureClient
from pyspark.sql.functions import *
from py4j.java_gateway import java_import

#Construction du contexte spark
spark = SparkSession.builder \
  .appName("Embedding Spark Thrift Server") \
  .config("spark.sql.hive.thriftServer.singleSession", "True") \
  .config("hive.server2.thrift.port", "10001") \
  .config("javax.jdo.option.ConnectionURL", \
  "jdbc:derby:;databaseName=metastore_db2;create=true") \
  .enableHiveSupport() \
  .getOrCreate()

#construction d'un schema template
schema=spark.read.json("hdfs:///tmp/ttempJson.json",multiLine=True).schema



#enregistrement au topic Kafka 
s1= spark.readStream.format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("subscribe","RealTime-Transilien-Topic").load()

jsondf=s1.selectExpr("CAST(value as STRING)","CAST(timestamp as TIMESTAMP)")

jsondf=jsondf.select(from_json(col("value"),schema),"timestamp")

#Parsing et Mise en forme du Json Stream
jsondf=jsondf.select("jsontostructs(value).data","timestamp")
jsondf=jsondf.select(explode("data"),"timestamp")
jsondf=jsondf.select("col.Siri.ServiceDelivery.StopMonitoringDelivery.MonitoredStopVisit","timestamp")
jsondf=jsondf.select(explode("MonitoredStopVisit"),"timestamp")
jsondf=jsondf.select(explode("col"),"timestamp")
jsondf=jsondf.select("col.MonitoredVehicleJourney.FramedVehicleJourneyRef.DatedVehicleJourneyRef",\
               "col.MonitoringRef.value",\
                "col.MonitoredVehicleJourney.MonitoredCall.StopPointName",\
               "col.MonitoredVehicleJourney.MonitoredCall.DestinationDisplay",\
               "col.MonitoredVehicleJourney.MonitoredCall.AimedDepartureTime",\
               "col.MonitoredVehicleJourney.MonitoredCall.ExpectedDepartureTime","timestamp")

jsondf=jsondf.withColumn("StopPointName", explode("StopPointName"))
jsondf=jsondf.withColumn("DestinationDisplay", explode("DestinationDisplay"))

jsondf=jsondf.select("DatedVehicleJourneyRef",col("value").alias("StopPoint"),col("StopPointName.value").alias("StopPointName"),col("DestinationDisplay.value").alias("DestinationDisplay"),"AimedDepartureTime","ExpectedDepartureTime","timestamp")
#Convertir les dates au format unix timestamp pour pouvoir faire la difference
jsondf=jsondf.withColumn('converted_aimed',unix_timestamp(col('AimedDepartureTime'), "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"))
jsondf=jsondf.withColumn('converted_expected',unix_timestamp(col('ExpectedDepartureTime'), "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"))
jsondf=jsondf.withColumn('attente',col('converted_expected')-col('converted_aimed'))
windowedjsondf= jsondf.withWatermark("timestamp", "10 seconds").groupBy(window(col("timestamp"), "60 minutes","60 minutes"),jsondf.DatedVehicleJourneyRef ,jsondf.StopPoint,col("StopPointName"),col("DestinationDisplay")).agg(max('attente').alias('attente'))

windowedjsondf=windowedjsondf.selectExpr("CAST(window.start as STRING)","CAST(window.end as STRING)","DatedVehicleJourneyRef","StopPoint","StopPointName","DestinationDisplay","attente")
#windowedjsondf.createOrReplaceTempView("ratp")
windowedjsondf.createGlobalTempView("ratp")
""" LAUNCH STS """
java_import(spark.sparkContext._gateway.jvm, "")
spark.sparkContext._gateway.jvm.org.apache.spark.sql.hive.thriftserver \
  .HiveThriftServer2.startWithContext(spark._jwrapped)
""" STS RUNNING """

query=windowedjsondf.writeStream\
	  .outputMode("complete")\
      .format("memory")\
	  .trigger(processingTime='2 minutes')\
      .queryName("ratp")\
      .option("truncate",False)\
	  .start()
query.awaitTermination()