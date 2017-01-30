Tutorial - Part #2 - Models
===========================

Study case: Iris Pipeline
-------------------------

We will carry out a simple exercise, using our recently initialized pipeline
to develop a piepeline for statistic calculations of the famous `Fisher Iris Dataset`_.

The global idea is to obtain information for each class of Iris (
Setosa, Virginica, and Versicolor) that is being calculated separatedly, 
seizing the multi processing of 3 cores at the time.

Finally we will define some alerts, just to let us know if any expected 
results are obtained.

We will define some commands as well, to check the pipeline general
status.


Download the Data
-----------------

First of all we need to download the csv_ file, with the raw data to feed the
pipeline. We can get it from: https://github.com/toros-astro/corral/raw/master/datasets/iris.csv
and put it inside ``my_pipeline`` directory. 

Taking a glance of our files
at this point we should get::

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


Basic Configuration
-------------------

First thing to do is to edit ``settings.py``.

Something that we need to be able is to find pahts dinamically, so we import
the *os* module. So the import should look like

.. code-block:: python

    import logging
    import os


The ``CONNECTION`` variable specifies the *RFC-1738* (used by SQLAlchemy_)
format for database connection. Default should look something like this:

.. code-block:: python

    CONNECTION = "sqlite:///my_pipeline-dev.db"

With this a ``pipeline-dev.db`` file will be created in the same directory where
``in_corral.py`` is located, containing the SQLite_ database.

.. seealso::

    For more information regarding another databases you can search the
    SQLAlchemy documentation at:
    http://docs.sqlalchemy.org/en/latest/core/engines.html


At the end of the file we will add the following lines

.. code-block:: python

    PATH = os.path.abspath(os.path.dirname(__file__))
    IRIS_PATH = os.path.join(PATH, "iris.csv")

First line stores in ``PATH`` the directory where ``settings.py`` is located,
second line just creates a path to file *iris.csv* downloaded before.


The Models
----------

Now our pipeline needs to know the looks of our data stored in the
database.

In ``my_pipeline/models.py`` file we erase the ``Example`` class. 
Then we modify the file so it looks just like this:

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


As we can se ``Name`` and ``Observation`` class inheritates from 
``db.Model``, and by doing this we let Corral know that these are
tables in our database.

The ``Name`` model is in charge of storing every different
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
