## Práctica 4 de Cloud Computing: Servicios y Aplicaciones: Procesamiento y minería de datos en Big Data con Spark sobre plataformas cloud

### Introducción

El objetivo de esta práctica es aprender a procesar grandes cantidades de datos y extraer conocimiento mediante el paradigma map reduce. Para ello se ha realizado un flujo de trabajo en Spark con el que se ha analizado el dataset ECBDL14_IR2. Además utilizando la biblioteca MLLib de Spark se han realizado múltiples predicciones sobre este. 



### Resolución del problema de clasificación

Este proceso se ha dividido en tres partes principales:

1. <u>Limpieza de datos</u>: 

   Dado que el dataset tiene mas de 600 columnas el primer paso consiste en eliminar la mayoría y quedarse con solo unas pocas previamente seleccionadas, que en mi caso son: PredSS_r2_4, PredSS_r2_3,PSSM_r1_-4_F, PredSS_r2,PSSM_r2_-3_A, PSSM_r1_4_W  y class. Para ello he creado un primer flujo de trabajo en spark `P4 preprocesado.py` . 

   Este flujo carga tanto `ECBDL14_IR2.header` como `ECBDL14_IR2.data` en RDDs. Del RDD de `ECBDL14_IR2.header`  extrae la lista de columnas y la utiliza para encontrar el indice de cada una de las columnas que me han sido asignadas. A continuación filtra el  RDD de `ECBDL14_IR2.data`  en base a esos indicies y finalmente guarda las columnas en formato CSV en un archivo. 

   Este flujo ha sido ejecutado en hadoop.ugr.es.

2. <u>Preprocesado para MLLib</u>: 

   He empezado cargando el csv generado en la sección anterior en databricks. El código de ejemplo de databricks para cargar CSVs genera un dataframe de strings, esto es problemático porque la mitad de las variables son numéricas. Para arreglarlo he generado un schema con el que he indicado el tipo de dato de cada columna. Al pasarle este schema a la función lectora de csv, esta devolverá un dataframe con los tipos adecuados.

   A continuación he equilibrado los datos, ya que en la variable `class` los ceros aparecen el doble de veces que los unos. Para ello he utilizado una función resample a la que pasandole entre otros el ratio de ceros y unos deseado, devuelve un dataframe con dicha proporción.

   Posteriormente he indexado las variables categóricas utilizando un StringIndexer, ya que los algoritmos de MLLib que he usado no son capaces de trabajar directamente con strings. 

   Con la esperanza de mejorar los resultados he aprovechado los resultados del StringIndexer para crear una vectores one-hot por cada variable categórica. 

   Finalmente he agrupado todas las variables predictoras en una sola columna llamada features y he creado los conjuntos de entrenamiento y test con una partición 70/30. Crear una columna que agrupe las variables predictoras parece ser un requisito de funcionamiento de los algoritmos de MLLib.

3. <u>Predicciones:</u>

   He realizado predicciones con los siguientes modelos:

   1. Random Forest:
      1. El primer modelo random forest es un `RandomForestClassifier` con 10 arboles y ha arrojado una tasa de error sobre el conjunto test de 0.409296.
      2. El segundo modelo random forest ha usado 50 arboles y una profundidad máxima de 10. La tasa de error sobre el conjunto test ha sido de 0.408386, ligeramente mejor que el caso anterior pero ha tomado una cantidad considerable de tiempo
   2. Linear Support Vector Machine:
      1. El primer modelo tiene un máximo de 10 iteraciones y un regParam de 0.1. La tasa de error sobre el conjunto test ha sido de 0.411708.
      2. El segundo modelo tiene un máximo de 20 iteraciones y un regParam de 0.2. Sus resultados son ligeramente mejores que los del modelo anterior con una tasa de error de 0.411706. Aunque una diferencia tan pequeña no es significativa.
   3. Decision tree
      1. El primer modelo es un decision tree con los parametros por defecto, y tiene una tasa de error de 0.411706 sobre el conjunto de test. En el caso de este predictor las predicciones realizadas son en coma flotante, por lo que la columna de predicciones debe de ser convertida a 0 o 1, en este caso si el valor predicho es superior a 0.45 se redondea a 1.
      2. Este segundo modelo tiene una profundidad máxima de 10 y un checkpointInterval de 5. Ofrece una tasa de error de 0.413644, por lo que estas modificaciones al comportamiento por defecto han empeorado el resultado del algoritmo.
   4. Gradient-boosted tree
      1. El primer modelo es un `GBTRegressor` con un máximo de 10 iteraciones. Tiene una tas de error de 0.408644, de las mejores hasta el momento. De igual forma que en el algoritmo anterior, los resultados de este predictor son en coma flotante, por ello deben ser redondeados antes de calcular la tasa de error.
      2. En este segundo modelo inicialmente había probado unas iteraciones máximas de 20 y una profundidad máxima de 10, pero el tiempo de ejecución se disparó de tal forma que tuve que cortarlo. Finalmente me decanté por poner una profundidad máxima de 3 en lugar de 10. Con este cambio el tiempo de ejecución fue similar al del modelo anterior, aunque los resultados un poco peores, obtuve una tasa de error de 0.409537
   5. Binomial logistic regression
      1. Este primer modelo utiliza un regParam de 0.3, un elasticNetParam de 0.8, unas iteraciones máximas de 10 y una familia binomial. La tasa de error es de 0.501521, el peor resultado hasta el momento.
      2. Este segundo modelo  utiliza un regParam de 0.2, un elasticNetParam de 0.7, unas iteraciones máximas de 20 y una familia binomial. La tasa de error vuelve a ser  0.501521, lo que me hace pensar que tanto este modelo como el anterior están prediciendo continuamente la misma clase.

También he probado los modelos Naive Bayes y Multilayer perceptron classifier pero por alguna razón que desconozco causaban que saltase una excepción en el código interno de Spark.



### Conclusiones

Spark me ha parecido una herramienta muy interesante, pero la plataforma en la que he realizado la mayoría del trabajo, databricks, está un tanto limitada en su versión gratuita, por lo que el proceso se ha hecho lento y un poco tedioso. Además como he comentado antes, me he encontrado con errores en el propio Spark que me han impedido probar el perceptron multicapa y el naive bayes. Respecto al resto de predictores me ha llamado la atención que todos ellos a excepción de Binomial logistic regression tienen una tasa de error que ronda el 40%, una tasa un tanto alta. Desconozco si esto se debe a limitaciones del dataset o a algún error que he cometido durante el desarrollo de esta práctica.

