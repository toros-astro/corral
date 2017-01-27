Tutorial - Part #2 - Models
===========================

El caso: Iris Pipeline
----------------------

Llevaremos adelante un ejemplo sencillo, utilizaremos nuestro pipeline recien
creado para crear un pipeline para el calculo sencillo de estadisticas del
famoso `Fisher Iris Dataset`_.

La idea global es que las estadisticas de cada tipo de Iris (Setosa, Virgínica
y Versicolor) se ejecute por separado para aprovechar el multiprocesamiento de
3 procesadores simultaneamente.

Finalmente definiremos unas alertas para informar algun estado deseado.

Así mismo definiremos algunos comandos para ver el estado general del pipeline.


Descargando los datos
---------------------

Primero es necesario descargar el archivo csv_ con los datos con los cuales
alimentaremos el pipeline. Puede descargar desde:

https://github.com/toros-astro/corral/raw/master/datasets/iris.csv

Y ubicarlo dentro del directorio ``my_pipeline``. Nuestra estructura en este
punto tiene la forma::

    in_corral.py
    my_pipeline/
    ├── __init__.py
    ├── iris.csv
    ├── settings.py
    ├── pipeline.py
    ├── models.py
    ├── load.py
    ├── steps.py
    ├── alerts.py
    └── commands.py


Configuración Básica
--------------------

El primer paso es editar el archivo ``settings.py``.

Primero debemos importar el modulo *os* que nos servira para determinar
el path donde se encuentra nuestro pipeline de manera dinamica. Asi los imports
deberian quedar con la forma

.. code-block:: python

    import logging
    import os


En la variable ``CONNECTION`` se encuentra especificada en el formato
*RFC-1738* (utilizado por SQLAlchemy_) la conexcion a la base de datos. Por
defecto deberia decir algo como:

.. code-block:: python

    CONNECTION = "sqlite:///my_pipeline-dev.db"

Con esto se creara un archivo ``pipeline-dev.db`` en la misma carpeta donde se
encuentra ``in_corral.py`` que contendra la base de datos SQLite_.

.. seealso::

    Para más informacón de que otras bases de datos se pueden utilizar lea
    la documentación de SQLAlchemy:
    http://docs.sqlalchemy.org/en/latest/core/engines.html


Al final del archivo agregaremos las siguientes lineas

.. code-block:: python

    PATH = os.path.abspath(os.path.dirname(__file__))
    IRIS_PATH = os.path.join(PATH, "iris.csv")

La primer linea guarda en la variable ``PATH`` el directorio donde se encuentra
el archivo ``settings.py`` la segunda linea crea un path al archivo *iris.csv*
que bajamos en el paso anterior.


Los modelos
-----------

Ahora nuestro pipeline necesita una defeinicion de como seran los datos
que guardaran la información sobre cada uno de los campos del iris data set.

Dentro del archivo ``my_pipeline/models.py`` borraremos la clase ahi definida
como ``Example``. Luego modificaremos el arhivo para que se vea de la siguiente
forma nueva para que se vea de la siguiente forma:

.. code-block:: python

    class Name(db.Model):

        __tablename__ = 'Name'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), unique=True)


    class Observation(db.Model):

        __tablename__ = 'Observation'

        id = db.Column(db.Integer, primary_key=True)

        name_id = db.Column(
            db.Integer, db.ForeignKey('Name.id'), nullable=False)
        name = db.relationship("Name", backref=db.backref("observations"))

        sepal_length = db.Column(db.Float, nullable=False)
        sepal_width = db.Column(db.Float, nullable=False)
        petal_length = db.Column(db.Float, nullable=False)
        petal_width = db.Column(db.Float, nullable=False)


Como podemos ver la clase ``Name`` y ``Observarion`` hereda de  ``db.Model``,
con esto informamos a corral que deseamos persistir estos objetos y que son
de interes en nuestra base de datos.

El modelo ``Name`` sera el encargado de guardar cada nombre diferente que
exista en nuestro dataset. Hay que recordar que el dataset tiene tres tipos
distingos de flores iris: *setosa*, *versicolor* y *virginica* con lo cual
persistiremos 3 instancias de este modelo. En la misma clase solo tenemos
tres atributos el primero ``__tablename__`` determinara cual será el nombre de
la tabla que se creara en la base de datos para persitir esta informacion
(*Name* sera el nombre en nuestro caso). ``id`` es una columna de la tabla
*Nane* que sera la clave primaria de timpo entero. Finalmente la columna
``name`` contendra el nombre propiamente dicho con una longitud máxima de 50
caracteres y no podra repetirse.

El modelo ``Observation`` por otra parte ademas de los atributos
``__tablename__`` y ``id``; posee una references_ al modelo ``Name`` (atributos
``name_id`` y ``name``) con lo cual cada instancia de esta tabla tiene que
tener un nombre y ademas 4 columnas en formato de numeros flotantes para
almacenar las otras 4 columnas del dataset.

.. note::

    Los modelos son en todo sentido modelos del ORM de SQLAlchemy; y
    ``db.Model`` es un `declarative_base`_

    Para conocer mas sobre el orm de Sqlalchemy por favor lee la documentacion
    http://docs.sqlalchemy.org/en/rel_1_1/orm/tutorial.html

.. note::

    Al ejecutar ``from corral import db``, dentro del namespace ``db`` estan
    disponibles los namespaces ``sqlalchemy``, ``sqlalchemy.orm`` y
    ``sqlalchemy_utils``.

    Para conocer mas sqlalchemy_utils: http://sqlalchemy-utils.readthedocs.org


Ahora para crear la base de datos debemos ejecutar el comando

.. code-block:: bash

    $ python in_corral.py createdb

Luego de una confirmación la salida deberia verse asi:

.. code-block:: bash

    Do you want to create the database [Yes/no]? yes
    [my_pipeline-INFO @ 2016-01-08 01:44:01,027] SELECT CAST('test plain returns' AS VARCHAR(60)) AS anon_1
    [my_pipeline-INFO @ 2016-01-08 01:44:01,028] ()
    [my_pipeline-INFO @ 2016-01-08 01:44:01,029] SELECT CAST('test unicode returns' AS VARCHAR(60)) AS anon_1
    [my_pipeline-INFO @ 2016-01-08 01:44:01,029] ()
    [my_pipeline-INFO @ 2016-01-08 01:44:01,031] PRAGMA table_info("Observation")
    [my_pipeline-INFO @ 2016-01-08 01:44:01,031] ()
    [my_pipeline-INFO @ 2016-01-08 01:44:01,060] PRAGMA table_info("Name")
    [my_pipeline-INFO @ 2016-01-08 01:44:01,060] ()
    [my_pipeline-INFO @ 2016-01-08 01:44:01,061]
    CREATE TABLE "Name" (
        id INTEGER NOT NULL,
        name VARCHAR(50),
        PRIMARY KEY (id),
        UNIQUE (name)
    )

    [my_pipeline-INFO @ 2016-01-08 01:44:01,201] ()
    [my_pipeline-INFO @ 2016-01-08 01:44:01,333] COMMIT
    [my_pipeline-INFO @ 2016-01-08 01:44:01,334]
    CREATE TABLE "Observation" (
        id INTEGER NOT NULL,
        name_id INTEGER NOT NULL,
        sepal_length FLOAT NOT NULL,
        sepal_width FLOAT NOT NULL,
        petal_length FLOAT NOT NULL,
        petal_width FLOAT NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(name_id) REFERENCES "Name" (id)
    )

    [my_pipeline-INFO @ 2016-01-08 01:44:01,334] ()
    [my_pipeline-INFO @ 2016-01-08 01:44:01,467] COMMIT

En la salida podran ver las sentencias sql que crearon las tablas para persistir
nuestros modelos mas algunas tablas de soporte utilizadas por corral como
``__corral_alerted__``

Podemos explorar nuestra base de datos recien creada y vacia ejecutando
el comando ``python in_corral.py dbshell``


.. code-block:: console

    $ python in_corral.py dbshell
    Connected to: Engine(sqlite:///my_pipeline-dev.db)
    Type 'exit;' or '<CTRL> + <D>' for exit the shell

    SQL> select * from sqlite_master where type = 'table' and name != '__corral_alerted__';
    +-------+-------------+-------------+----------+-----------------------------------------------------+
    | type  |    name     |  tbl_name   | rootpage |                         sql                         |
    +=======+=============+=============+==========+=====================================================+
    | table | Name        | Name        | 2        | CREATE TABLE "Name" (                               |
    |       |             |             |          |         id INTEGER NOT NULL,                        |
    |       |             |             |          |         name VARCHAR(50),                           |
    |       |             |             |          |         PRIMARY KEY (id),                           |
    |       |             |             |          |         UNIQUE (name)                               |
    |       |             |             |          | )                                                   |
    | table | Observation | Observation | 5        | CREATE TABLE "Observation" (                        |
    |       |             |             |          |         id INTEGER NOT NULL,                        |
    |       |             |             |          |         name_id INTEGER NOT NULL,                   |
    |       |             |             |          |         sepal_length FLOAT NOT NULL,                |
    |       |             |             |          |         sepal_width FLOAT NOT NULL,                 |
    |       |             |             |          |         petal_length FLOAT NOT NULL,                |
    |       |             |             |          |         petal_width FLOAT NOT NULL,                 |
    |       |             |             |          |         PRIMARY KEY (id),                           |
    |       |             |             |          |         FOREIGN KEY(name_id) REFERENCES "Name" (id) |
    |       |             |             |          | )                                                   |
    +-------+-------------+-------------+----------+-----------------------------------------------------+
    SQL>
