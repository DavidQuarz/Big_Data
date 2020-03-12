from pyspark.sql import SparkSession
from pyspark.sql.functions import *

#Construction du contexte spark
#spark = SparkSession.builder.appName("spark streaming from Kafka").getOrCreate()

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
windowedjsondf= jsondf.groupBy(window(jsondf.timestamp, "2 minutes","2 minutes"),jsondf.DatedVehicleJourneyRef ,jsondf.StopPoint).agg(max('attente').alias('attente'))
windowedjsondf.writeStream.outputMode("complete").format("console").option("numRows",10000).option("truncate",False).start().awaitTermination()

