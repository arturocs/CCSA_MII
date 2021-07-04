from pyspark import SparkContext, SparkConf

if __name__ == "__main__":

    columnas_seleccionadas = [
        "PredSS_r2_4",
        "PredSS_r2_3",
        "PSSM_r1_-4_F",
        "PredSS_r2",
        "PSSM_r2_-3_A",
        "PSSM_r1_4_W",
        "class",
    ]

    conf = SparkConf().setAppName("Preprocesamiento practica 4")
    sc = SparkContext(conf=conf)

    # Extraemos todas las columnas del dataset
    columnas = sc.textFile("/user/datasets/ecbdl14/ECBDL14_IR2.header").filter(lambda l: l.startswith(
        "@inputs")).flatMap(lambda l: l.lstrip("@inputs").strip().split(", ")).collect()
    columnas.append("class")

    # Identificamos los indices de las columnas que queremos en el dataset final
    indices_seleccionados = [columnas.index(i) for i in columnas_seleccionadas]

    # Filtramos el dataset dejando solo aquellas columnas cuyo indice se corresponde con alguno de los indices seleccionados
    datos_seleccionados = sc.textFile("/user/datasets/ecbdl14/ECBDL14_IR2.data").map(
        lambda l: [i[1] for i in enumerate(l.split(",")) if i[0] in indices_seleccionados]).collect()

    # Unimos todas las listas en formato CSV
    csv = ",".join(columnas_seleccionadas) + "\n" + \
        "".join(",".join(d) + "\n" for d in datos_seleccionados)

    # Escribimos el string resultante en un archivo
    f = open("./filteredC.small.training", "w")
    f.write(csv)
    f.close()
