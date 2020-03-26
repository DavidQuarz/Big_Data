# Projet Big Data - Mobilité Ile-de-France

## Prérequis
### 1/ Installation de HDP 3.0.1
Suivre la procédure d'installation <https://github.com/qge/hdp>

### 2/ Lancement de HDP (si ce n'est pas fait)
Se connecter à l'instance EC2 et lancer les conteneurs Docker.

```
sudo systemctl start docker
docker start <docker-hdp> <docker-proxy>
```

### 3/ Connexion à la Sandbox HDP

```
docker exec -ti <docker-hdp> bin/bash
```
### 4/ Transfert du fichier du ttempJson.json vers HDFS
Le fichier ttempJson.json contient la structure de données du stream.

```
hdfs dfs –put <PATH/TO/Big_Data/app/api/ttempJson.json> /tmp/ttempJson.json
```

## Lancement du producer Kafka
Ouvrir un terminal, se positionner dans le répertoire Big_Data/app/api et lancer le producer.

```
python producerKafka.py
```

## Lancement du consumer Spark Streaming
### Solution retenue : Stockage dans Thrift (memory + csv)
<p>Idéalement, notre consumer stocke les données issues du stream au format "memory" sur Thrift. Ces données sont ensuite récupérées par Tableau Software au moyen de Spark Thrift Server (STS) qui expose les données Spark. En raison de problèmes de compatibilité des logiciels à notre disposition, Tableau Software ne parvient pas à lire les données au format "memory" depuis STS.</p>

<p>Pour contourner ce problème, nous stockons toujours la sortie du consumer dans Thrift au format "memory" dans une table temporaire. Nous créons dans la même instance Thrift une autre table permanente au format "csv". Avec crontab, nous écrasons toutes les 2 minutes la table permanente avec les données de la table temporaire et tout en nous assurant de la bonne structure de données à insérer.</p>

<p>Ouvrir un nouveau terminal et entrer la commande suivante (depuis le répertoire Big_Data/app/api :</p>

```
#Lancement du consumer consumerJob_thrift_v2.py
spark-submit \
--packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.0 \
--conf spark.sql.hive.thriftServer.singleSession=true \
  consumerJob_thrift_v2.py
```

<p>Lancer un autre terminal puis lancer Beeline :</p>

```
/usr/hdp/current/spark2-thriftserver/bin/beeline -u jdbc:hive2://localhost:10001
```
<p>Dans Beeline, créer la table "transilien" en saisissant la commande :</p>

```
#Création de la table permanente "transilien" dans Beeline (à faire une seule fois)
CREATE EXTERNAL TABLE IF NOT EXISTS transilien(
  `start` STRING,
  `end` STRING,
  `DatedVehicleJourneyRef` STRING,
  `StopPoint` STRING,
  `StopPointName` STRING,
  `DestinationDisplay` STRING,
  `attente` BIGINT
    )
  COMMENT 'Transilien data'
  ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
  STORED AS TEXTFILE
  LOCATION '/user/root/transilien';
```

<p>Sortir de Beeline, et modifier la crontab de la sandbox :</p>

```
#Création de la crontab
crontab -e
```

```
#Création de la tâche planifiée
*/2 * * * * /usr/hdp/current/spark2-thriftserver/bin/beeline -u jdbc:hive2://localhost:10001 --outputformat=csv2 -e "INSERT OVERWRITE TABLE transilien SELECT * FROM ratp;"
```

### Solutions envisagées et abandonnées 
#### Stockage dans Thrift (memory)
<p>Cette solution permet de stocker dans l'instance Thrift l'output du consumer au format "memory". En raison de problèmes de compatibilité entre logiciels, Tableau Software ne parvient pas lire les tables temporaires et donc le format "memory". Cette solution a été abandonnée. Il est a noté que ce problème a été résolu dans les versions postérieures des logiciels que nous utilisons actuellement.</p>
<p>Ouvrir un nouveau terminal :</p>

```
#Lancement du consumer consumerJob_thrift_v0.py
spark-submit \
--packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.0 \
--conf spark.sql.hive.thriftServer.singleSession=true \
  consumerJob_thrift_v0.py
```

#### Stockage dans Thrift (memory) + Persistence dans HIVE
<p>Cette solution permet de stocker dans l'instance Thrift l'output du consumer au format "memory". Les données de l'output sont ensuite persistées dans une table créée manuellement sur HIVE. Cette solution permet à Tableau Software d'accéder aux données depuis HIVE. Néanmoins, en raison du temps de requêtage trop long, cette solution a été abandonnée.</p>
<p>Se connecter à Data Analytics Studio (port 30800), onglet Compose :</p>

```
#Création de la table "transilien" sur Data Analytics Studio (à faire une seule fois)
CREATE TABLE `default`.`transilien` (
  `start` STRING,
  `end` STRING,
  `DatedVehicleJourneyRef` STRING,
  `StopPoint` STRING,
  `StopPointName` STRING,
  `DestinationDisplay` STRING,
  `attente` BIGINT
)
```

<p>Ouvrir un nouveau terminal :</p>

```
#Lancement du consumer consumerJob_thrift_v1.py
spark-submit\
  --jars /usr/hdp/3.0.1.0-187/hive_warehouse_connector/hive-warehouse-connector-assembly-1.0.0.3.0.1.0-187.jar \
  --py-files /usr/hdp/3.0.1.0-187/hive_warehouse_connector/pyspark_hwc-1.0.0.3.0.1.0-187.zip \
  --conf spark.security.credentials.hiveserver2.enabled=false\
  --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.0 consumerJob_thrift_v1.py
```
## Exploitation des données de la ligne H (temps d'attente)
Les données liées au temps d'attente sont exploitées dans le dashboard de Tableau Software dashboard_ligneH.twb.

## Estimation de la position d'un train de la ligne H
Pour estimer la position d'un train, nous stockons pour chaque gare ses prochaines heures de passage communiquées par l'API. Ces données sont stockées dans STS dans la table "passages". La position d'un train est déterminée par rapport à l'heure actuelle :
* Gare de départ à l'instant t : gare dont la prochaine heure de départ est la plus proche de l'heure actuelle par valeur inférieure.
* Gare d'arrivée à l'instant t : gare dont la prochaine heure de départ est la plus proche de l'heure actuelle par valeur supérieure.


<p>S'assurer que le producer et le consumer sont bien lancés. Dans le docker Sandbox HDP, lancer Beeline et créer la table "passages" en saissant la commande :</p>

```
#Connexion à Beeline
/usr/hdp/current/spark2-thriftserver/bin/beeline -u jdbc:hive2://localhost:10001
```

```
#Création de la table permanente "passages" dans Beeline (à faire une seule fois)
CREATE EXTERNAL TABLE IF NOT EXISTS passages(
   `DatedVehicleJourneyRef` STRING,
   `StopPointName` STRING,
  `DestinationDisplay` STRING,
  `converted_expected` BIGINT,
  `converted_expected_arrival` BIGINT
  )
  COMMENT 'Transilien data passages'
  ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
  STORED AS TEXTFILE
  LOCATION '/user/root/passages';
```

<p>Sortir de Beeline, et modifier la crontab de la sandbox :</p>

```
#Création de la crontab
crontab -e
```

```
#Création de la tâche planifiée
*/1 * * * * /usr/hdp/current/spark2-thriftserver/bin/beeline -u jdbc:hive2://localhost:10001 --outputformat=csv2 -e "INSERT OVERWRITE TABLE passages SELECT * FROM passage;"
```

La position du train est donnée dans le dashboard de Tableau Software progression_passage.twb.
