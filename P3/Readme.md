# Práctica 3: mongodb

Descargamos y ejecutamos mongodb con docker:

```sh
docker run --name some-mongo -d mongo:latest
docker exec -it some-mongo bash
```

Descargamos el conjunto de datos dentro del contenedor:

```sh
apt update
apt install wget
wget https://raw.githubusercontent.com/manuparra/MasterCyberSec_Practice/master/datasetmongodb/SacramentocrimeJanuary2006.csv
```

Importamos los datos en mongo:

```sh
mongoimport -d p3 -c sacramentocrime --type csv --file ./SacramentocrimeJanuary2006.csv --headerline
```

## Querys

### Totalizar el número de delitos por cada tipo

Agrupamos por el campo `crimedescr` que describe el tipo de crimen.

```js
use p3
db.sacramentocrime.aggregate([{"$group": {_id: "$crimedescr",count: { $sum: 1 }} }])
```

Resultado:

```json
{ "_id" : "603  FORCED ENTRY/PROP DAMAGE", "count" : 2 }
{ "_id" : "9.40.020(A) JUVENILE CURFEW", "count" : 3 }
{ "_id" : "23103(A) RECKLESS ON HIGHWAY", "count" : 8 }
{ "_id" : "12025(A)2)CNCLD GUN ON PER/FEL", "count" : 2 }
{ "_id" : "O/S AGENCY -ASSISTANCE- I RPT", "count" : 13 }
{ "_id" : "653M(B) PC ANNOY/RPT CALL HOME", "count" : 12 }
{ "_id" : "FAMILY DISTURBANCE - I RPT", "count" : 13 }
{ "_id" : "TRAFFIC-ACCIDENT INJURY", "count" : 182 }
{ "_id" : "594.3(A)VANDAL/PLACE OF WORSHI", "count" : 4 }
{ "_id" : "653K PC POSS/SELL SWITCHBLADE", "count" : 3 }
{ "_id" : "TRAFFIC - I RPT", "count" : 20 }
{ "_id" : "368(B)(1) CRUELTY/ELDER/ W/INJ", "count" : 1 }
{ "_id" : "653M(A) PC OBSCENE/THREAT CALL", "count" : 17 }
{ "_id" : "452(D)PC CAUSE FIRE OF PROPERT", "count" : 1 }
{ "_id" : "BUSINESS PERMITS - I RPT", "count" : 4 }
{ "_id" : "484E(A)PC THEFT OF CREDIT CARD", "count" : 2 }
{ "_id" : "485 PC PT OF FOUND PROPERTY", "count" : 1 }
{ "_id" : "INTOX REPORT/ADMIN PER - I RPT", "count" : 1 }
{ "_id" : "12025(B)6 UNREG/CONCLED FIREAR", "count" : 1 }
{ "_id" : "484G(A)PC USE FORGED CARD", "count" : 6 }
Type "it" for more
```



### Franja horaria (o franjas) con más número de delitos

Primero pasamos la fecha de string a objeto fecha, proyectamos usando `$hour` que devuelve la hora sin minutos. Finalmente agrupamos por el campo hora  y ordenamos de forma descendente según el número de crimenes

```js
db.sacramentocrime.aggregate(
    {
        $project: {
            cdatetime: {
                $dateFromString:
                    { dateString: "$cdatetime" }
            }
        }
    }, {
    "$project": {
        "hour": { "$hour": "$cdatetime" },
        "count": 1
    }
}, {
    "$group": {
        "_id": "$hour", "total": {
            "$sum": 1
        }
    }
}, {
    $sort: { total: -1 }
})
```

Resultado:

```json
{ "_id" : 16, "total" : 471 }
{ "_id" : 21, "total" : 358 }
{ "_id" : 18, "total" : 430 }
{ "_id" : 22, "total" : 384 }
{ "_id" : 1, "total" : 187 }
{ "_id" : 6, "total" : 114 }
{ "_id" : 20, "total" : 362 }
{ "_id" : 3, "total" : 122 }
{ "_id" : 14, "total" : 385 }
{ "_id" : 23, "total" : 304 }
{ "_id" : 12, "total" : 399 }
{ "_id" : 15, "total" : 417 }
{ "_id" : 7, "total" : 219 }
{ "_id" : 8, "total" : 380 }
{ "_id" : 10, "total" : 306 }
{ "_id" : 9, "total" : 326 }
{ "_id" : 4, "total" : 91 }
{ "_id" : 17, "total" : 458 }
{ "_id" : 19, "total" : 358 }
{ "_id" : 13, "total" : 353 }
Type "it" for more
```

