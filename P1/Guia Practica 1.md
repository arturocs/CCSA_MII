**Master profesional Ingeniería Informática – Universidad de Granada**
 *Curso 2020-2021*

Sesión 1 - Práctica ->  **Cloud Computing: servicios y aplicaciones**

Profesor de prácticas: Manuel J. Parra Royón
 E-mail: [manuelparra@decsai.ugr.es](mailto:manuelparra@decsai.ugr.es)
 Twitter: [twitter.com/manugrapevine](http://twitter.com/manugrapevine)
 LinkedIn: https://www.linkedin.com/in/manuelparraroyon/

# Servicio  de almacenamiento  con NextCloud

Está sesión práctica consiste en realizar un despligue de NextCloud  completo utilizando diferentes microservicios encargados de tareas  específicas, tales como la administración de las Bases de Datos,  Autenticación, Balanceado (proxy) de carga o gestión del almacenamiento.

Para ello partiremos de un  servicio de almacenamiento en Cloud como  NextCloud, que  convertiremos en un microservicio en contenedores y al  cual le añadiremos todos los demás servicios adionales para darle  soporte. Estos servicios se añadirán de forma incremental, y finalmente  se procederá a crear un fichero de composición de contenedores con `docker-compose`.

### Objetivos

- Comprender el modelo de Cloud Computing con un servicio de almacenamiento de ficheros.
- Conocer el despliegue de software como servicio en Cloud Computing de forma incremental.
- Componer microservicios de forma básica con docker y docker-compose.
- Cononer herramientas básica de balanceado y distribución de carga.
- Conocer los modos de ejecución de órdenes dentro de los contenedores.

### Aquitectura

La composición de microservicios será la siguiente:

- **NGINX** : trabajará como Proxy y Balanceador de carga para el microservicio que albergará NextCloud.
- **NextCloud**: contendrá el microservicio de almacenamiento en Cloud. Puede ser uno o varios.
- **MySQL/MariaDB**: microservicio que dotará a NextCloud de acceso y gestión de los datos.
- **LDAP**: microservicio para conectar la autenticación de NextCloud para los usuarios y el acceso.

De forma opcional, la arquitectura debe permitir balancear la carga  desde el servicio NGINX hasta los contenedores (al menos 2), de modo que el tráfico se encauce hacía los contenedores de NextCloud. Los demás  microservicios sólo es necesario que tengan una única instancia de  ejecución.

### Dónde vamos a trabajar

Para el trabajo con contenedores se usarán dos entornos:

- **Entorno local**: Este entorno corresponde al PC del alumno. Para ello debes tener instalado `docker` y `docker-compose`. Se recomienda utilizar Linux para la sesión.
- **Entorno cloud**: Para este entorno le  proporcionaremos al alumno unas credenciales para que pueda desplegar  sus contendores en un servidor en la nube llamado `hadoop.ugr.es`, al que accederá por `ssh` y tendrá la opción de subir el fichero de composición `docker-compose`.

## Tareas a desarrollar

### Creación de contenedor con NGINX

Este contenedor contendrá el servicio que el usuario conecta desde  Internet, y es el responsable de pasar todas las peticiones a NextCloud  que se encuentra en el BackEnd.
 Además debe incluir las directivas para realizar un balanceado de carga  entre al menos dos contenedores de NextCloud (o solo uno si no se hace  esta opción).

Para ello hay que tener en cuenta:

- Como se despliega NGINX en contendores.

- Como se utiliza la configuración de 

  ```
  nginx.conf
  ```

   para adaptarla a nuestras necesidades:

  - Balanceado de carga
  - Reenvio / Proxy para los contenedores de NextCloud.

**Ejecución del contenedor:**

```
<containersystem> run  --name nginx -v $HOME/practica1/nginx.conf:/etc/nginx/nginx.conf:ro -p 8080:80 -d nginx
```

**Plantilla de configuración de nginx.conf:**

```
http {
    upstream nextcloudservice {
        server nextcloud01;
        server nextcloud02;
        server nextcloud03;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://nextcloudservice;
        }
    }
}
```

### Creación de contenedor con NextCloud

Existen varias formas de crear el contenedor de forma más o menos  automatizada, en nuestro caso la configuración inicial debe permitir  conectar NextCloud con **MySQL/MariaDB**, para poder utilizado de forma distribuida, ya que si se usa **SQLite** no tenemos la opción de hacer un sistema más robusto. De este modo la  opción por defecto que debeis usar es la de Base de Datos con **MySQL/MariaDB**.

Para ello, utilizaremos la siguiente descripción de servicios (en  este caso de ejemplo, sólo se monta un servicio de NextCloud y una BBDD  MaríaSQL), pero debes tener en cuenta que debe admitir al menos 2  servicios idénticos (opcionales) de NextCloud que comparten el espacio  de almacenamiento (no de BBDD, que es sólo una instancia).

```
# Creamos un nuevo directorio
mkdir NextCloud-docker-server

cd NextCloud-docker-server

# Copiamos este codigo en un fichero llamado docker-compose.yml

version: '3'
services:
  nextcloud:
    image: "nextcloud:21.0.0-apache"
    ports:
      - 8080:80
    restart: always
    volumes:
      - nextcloud:/var/www/html
    environment:
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_PASSWORD=<MYSQL_PASSWORD>
      - MYSQL_HOST=mariadb
      - NEXTCLOUD_ADMIN_USER=<NEXTCLOUD_ADMIN_USER>
      - NEXTCLOUD_ADMIN_PASSWORD=<NEXTCLOUD_ADMIN_PASSWORD>
  mariadb:
    image: "mariadb:10.4.8-bionic"
    command: "--transaction-isolation=READ-COMMITTED --binlog-format=ROW"
    restart: always
    volumes:
      - db:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=<MYSQL_ROOT_PASSWORD>
      - MYSQL_PASSWORD=<MYSQL_PASSWORD>
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
volumes:
  nextcloud:
  db:

# (Opcional) Creamos en entorno necesario para la inicialización del sistema, para ello dentro de este mismo directorio añadimos un fichero oculto llamado .env: Añadimos las variables que queramos, por ejemplo las de las claves que son más sensibles:

MYSQL_PASSWORD=<MYSQL_PASSWORD>
MYSQL_ROOT_PASSWORD=<MYSQL_ROOT_PASSWORD>
MYSQL_PASSWORD=<MYSQL_PASSWORD>
NEXTCLOUD_ADMIN_PASSWORD=<NEXTCLOUD_ADMIN_PASSWORD>


# Construimos el contenedor 
docker-compose up -d
# o bien, si queremos ver el proceso de carga y los logs en tiempo real, usaremos:
docker-compose up
```

### Creación de contenedor con MariaDB/MySQL

Hay muchas formas de componer MySQL/MariaDB, una de ellas puede ser la siguiente:
 wget https://raw.githubusercontent.com/owncloud/docs/master/modules/admin_manual/examples/installation/docker/docker-compose.yml

### Creación de contenedor con LDAP

Está parte es más compleja integrarla directamente sobre NextCloud,  por lo que se hace una vez que el sistema está funcionando y se tiene  acceso al microservicio de LDAP que se despliega con todo el sistema.

Aquí está toda la documentación: https://github.com/manuparra/docker_ldap

### Modos de ejecución de Docker:  Customización de NextCloud

Otro de los aspectos a considerar en esta práctica es que una vez que se ha desplegado la estructura de contenedores, y el sistema está  funcionando, es necesario ejecutar unas órdenes dentro de los  contenedores de NextCloud, de modo que podamos intereactuar con el  contenedor sin tener que entrar explicitamente en cada contenedor.

NextCloud incluye en su instalación y por tanto dentro del contenedor una serie de órdenes para hacer modificaciones en la configuración sin  tener que hacerlo manualmente desde el interfaz de administración web  del servicio. Esta órden es `occ` y permite gestionar la  configuración de NextCloud de forma directa desde la línea de órdenes.  Para ello debes revisar la documentación de la aplicación `occ` aquí: https://docs.nextcloud.com/server/20/admin_manual/configuration_server/occ_command.html

Este comando debe llamarse usando docker del siguiente modo:

*Por ejemplo para ver la lista de opciones de configuración:*

```
 docker exec -u www-data -it <nombre servicio NextCloud> php occ config:list
```

*Por ejemplo para ver la lista de opciones de configuración:*

```
 docker exec -u www-data -it <nombre servicio NextCloud> php occ config:list
```

*Para ver la lista de opciones modificables de la aplicación (plugins)*:

```
sudo docker exec -u www-data -it <nombre servicio NextCloud> php occ app:list
```

En esta parte se pide deshabilitar los siguientes plugins de la  aplicación utilizando docker para hacer los cambios en el interior del  contenedor, pero usando docker:

`accessibility`, `dashboard`, `accessibility`, `firstrunwizard`, `nextcloud_announcements`, `photos`,`weather_status`, `user_status`, `survey_client`, `support`, `recommendations` y `updatenotification`.

Estas operaciones pueden ir dentro de un fichero `.sh` que se puede ejecutar al terminar de desplegar todos los contenedores.

## Resultados de la sesión

- El alumno debe poder conectar a un servicio NextCloud y utilizarlo sin problemas.

- El alumno debe customizar el servicio NextCloud, ejecutando  órdenes del servicio con docker para hacer modificaciónes en la configuración.

- El alumno debe crear un fichero 

  ```
  docker-compose.yml
  ```

   que incluya:

  - a) Servicio NGINX
  - b) Servicio/s NextCloud
  - c) Servicio MySQL o María SQL
  - d) Servicio de Autenticación

- La arquitectura resultante debe ser la siguiente:

```
Usuario --> NGINX --> NextCloudCloud01 --> MariaDB00
                      NextCloudCloud00 --> MariaDB00
                      ----------
                          v
                      Auth LDAP
```

## Preguntas - Cuestionario

- ¿Cuál sería el  cuello de botella del sistema?.
- ¿Qué ocurre si uno de los contenedores de NextCloud deja de funcionar?:
  - ¿Caería todo el sistema?.
- ¿Qué medidas tomarías para evitar sobrecargar el sistema por ejemplo lanzando varias decenas de contedores cuando el uso el sistema es  mínimo?.
  - ¿Qué directivas tomarías si la demanda de uso del sistema crece, qué microservicios 	deberías tener en cuenta?.
  - ¿Y si se cae la instancia de MySQL, qué ocurriría?, ¿Cómo solucionarías el problema?.