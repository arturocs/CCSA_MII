# Databricks notebook source
# DBTITLE 1,Carga de datos
# Cargamos el archivo de datos
import pyspark.sql.types as tp
file_location = "/FileStore/tables/filteredC_small_training.csv"

# Creamos un schema para que las variables numericas sean parseadas automaticamente de string a entero
my_schema = tp.StructType([
    tp.StructField(name= 'PredSS_r2_4',      dataType= tp.StringType(),   nullable= True),
    tp.StructField(name= 'PredSS_r2_3', dataType= tp.StringType(),    nullable= True),
    tp.StructField(name= 'PSSM_r1_-4_F',       dataType= tp.StringType(),   nullable= True),
    tp.StructField(name= 'PredSS_r2',  dataType= tp.IntegerType(),    nullable= True),
    tp.StructField(name= 'PSSM_r2_-3_A',   dataType= tp.IntegerType(),    nullable= True),
    tp.StructField(name= 'PSSM_r1_4_W',       dataType= tp.IntegerType(),    nullable= True),
    tp.StructField(name= 'class',    dataType= tp.IntegerType(),   nullable= True),
   
])

df = spark.read.csv(file_location,schema= my_schema,header= True, sep=",")

display(df)

# COMMAND ----------

# DBTITLE 1,Equilibración de los datos
# Vemos el ratio de unos respecto a ceros en la columna clase
ratio = df[df['class'] == 1].count()/df[df['class'] == 0].count()
print(ratio)

# Arreglamos el desbalanceo de clases
def resample(base_features,ratio,class_field,base_class):
    pos = base_features.filter(col(class_field)==base_class)
    neg = base_features.filter(col(class_field)!=base_class)
    total_pos = pos.count()
    total_neg = neg.count()
    fraction=float(total_pos*ratio)/float(total_neg)
    sampled = neg.sample(False,fraction)
    return sampled.union(pos)
  
balanced_df = resample(df,1,"class",1)

# Comprobamos el ratio del dataframe resultante
ratio = balanced_df[balanced_df['class'] == 1].count()/balanced_df[balanced_df['class'] == 0].count()
print("Nuevo ratio:",ratio)

# COMMAND ----------

# DBTITLE 1,Indexado de variables categóricas
# Creamos una nueva columna numerica para las variables categoricas
from pyspark.ml.feature import StringIndexer
SI_PredSS_r2_4 = StringIndexer(inputCol='PredSS_r2_4',outputCol='PredSS_r2_4_Index')
SI_PredSS_r2_3 = StringIndexer(inputCol='PredSS_r2_3',outputCol='PredSS_r2_3_Index')
SI_PSSM_r1__4_F = StringIndexer(inputCol='PSSM_r1_-4_F',outputCol='PSSM_r1_-4_F_Index')

df = SI_PredSS_r2_4.fit(balanced_df).transform(balanced_df)
df = SI_PredSS_r2_3.fit(df).transform(df)
df = SI_PSSM_r1__4_F.fit(df).transform(df)
display(df)


# COMMAND ----------

# DBTITLE 1,Creación de vectores one hot
# Codificamos como vector one hot las variables categoricas para obtener mejores resultados
from pyspark.ml.feature import OneHotEncoder
OHE = OneHotEncoder(inputCols=['PredSS_r2_4_Index', 'PredSS_r2_3_Index', 'PSSM_r1_-4_F_Index'],outputCols=['PredSS_r2_4_OHE', 'PredSS_r2_3_OHE', 'PPSSM_r1_-4_F_OHE'])

df = OHE.fit(df).transform(df)

display(df)

# COMMAND ----------

# DBTITLE 1,Creación de la columna features
# Creamos una columna features que agrupa las variables predictoras
from pyspark.ml.feature import VectorAssembler

assembler = VectorAssembler(inputCols=['PredSS_r2',
                                       'PSSM_r2_-3_A',
                                       'PSSM_r1_4_W',
                                       'PredSS_r2_4_Index',
                                       'PredSS_r2_3_Index',
                                       'PSSM_r1_-4_F_Index',
                                       'PredSS_r2_4_OHE', 
                                       'PredSS_r2_3_OHE', 
                                       'PPSSM_r1_-4_F_OHE'
                                       ],
                           outputCol='features')
df = df.fillna(0)
df = assembler.transform(df)

display(df)

# COMMAND ----------

# DBTITLE 1,División del conjunto de datos en train y test
# Creamos los conjuntos de entrenamiento y test
train, test = df.randomSplit([0.7, 0.3], 1234)

# COMMAND ----------

# DBTITLE 1,Modelo Random Forest classifier 1
# Creamos un modelo random forest con 10 arboles
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

rf = RandomForestClassifier(labelCol="class", featuresCol="features", numTrees=10)

model = rf.fit(train)

predictions = model.transform(test)

display(predictions)

evaluator = MulticlassClassificationEvaluator(labelCol="class", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Test Error = %g" % (1.0 - accuracy))


# COMMAND ----------

# DBTITLE 1,Modelo Random Forest classifier 2
# Creamos un modelo random forest con 50 arboles y una profundidad maxima de 10
rf = RandomForestClassifier(labelCol="class", featuresCol="features", numTrees=50, maxDepth=10)

model = rf.fit(train)

predictions = model.transform(test)

display(predictions)

evaluator = MulticlassClassificationEvaluator(labelCol="class", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Test Error = %g" % (1.0 - accuracy))


# COMMAND ----------

# DBTITLE 1,Modelo Linear Support Vector Machine 1
from pyspark.ml.classification import LinearSVC

lsvc = LinearSVC(labelCol="class", maxIter=10, regParam=0.1)

model = lsvc.fit(train)

predictions = model.transform(test)

display(predictions)

evaluator = MulticlassClassificationEvaluator(labelCol="class", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Test Error = %g" % (1.0 - accuracy))



# COMMAND ----------

# DBTITLE 1,Modelo Linear Support Vector Machine 2
lsvc = LinearSVC(labelCol="class", maxIter=20, regParam=0.2)

model = lsvc.fit(train)

predictions = model.transform(test)

display(predictions)

evaluator = MulticlassClassificationEvaluator(labelCol="class", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Test Error = %g" % (1.0 - accuracy))


# COMMAND ----------

# DBTITLE 1,Modelo Decision tree classifier 1
from pyspark.ml.regression import DecisionTreeRegressor

dt = DecisionTreeRegressor(labelCol="class")

model = dt.fit(train)

predictions = model.transform(test)
predictions = predictions.withColumn("prediction",  (col("prediction") >0.45).cast("Double"))
display(predictions)

evaluator = MulticlassClassificationEvaluator(labelCol="class", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Test Error = %g" % (1.0 - accuracy))


# COMMAND ----------

# DBTITLE 1,Modelo Decision tree classifier 2

dt = DecisionTreeRegressor(labelCol="class", maxDepth=10, checkpointInterval=5)

model = dt.fit(train)

predictions = model.transform(test)
predictions = predictions.withColumn("prediction",  (col("prediction") >0.45).cast("Double"))
display(predictions)

evaluator = MulticlassClassificationEvaluator(labelCol="class", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Test Error = %g" % (1.0 - accuracy))




# COMMAND ----------

# DBTITLE 1,Modelo Gradient-boosted tree classifier 1
from pyspark.ml.regression import GBTRegressor

gbt = GBTRegressor(labelCol="class", maxIter=10)

model = gbt.fit(train)

predictions = model.transform(test)
predictions = predictions.withColumn("prediction",  (col("prediction") >0.5).cast("Double"))
display(predictions)

evaluator = MulticlassClassificationEvaluator(labelCol="class", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Test Error = %g" % (1.0 - accuracy))


# COMMAND ----------

# DBTITLE 1,Modelo Gradient-boosted tree classifier 2
gbt = GBTRegressor(labelCol="class", maxIter=20, maxDepth=3)

model = gbt.fit(train)

predictions = model.transform(test)
predictions = predictions.withColumn("prediction",  (col("prediction") >0.5).cast("Double"))
display(predictions)

evaluator = MulticlassClassificationEvaluator(labelCol="class", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Test Error = %g" % (1.0 - accuracy))

# COMMAND ----------

# DBTITLE 1,Modelo Binomial logistic regression  1
from pyspark.ml.classification import LogisticRegression

mlr = LogisticRegression(labelCol="class", maxIter=10, regParam=0.3, elasticNetParam=0.8, family="binomial")

model = mlr.fit(train)

predictions = model.transform(test)

display(predictions)

evaluator = MulticlassClassificationEvaluator(labelCol="class", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Test Error = %g" % (1.0 - accuracy))

# COMMAND ----------

# DBTITLE 1,Modelo Binomial logistic regression  2
mlr = LogisticRegression(labelCol="class", maxIter=20, regParam=0.2, elasticNetParam=0.7, family="binomial")

model = mlr.fit(train)

predictions = model.transform(test)

display(predictions)

evaluator = MulticlassClassificationEvaluator(labelCol="class", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Test Error = %g" % (1.0 - accuracy))
