Tutorial - Part #2 - Models
===========================

Study case: Iris Pipeline
-------------------------

We will carry out a simple exercise, using our recently initialized pipeline
to develop a pipeline for statistic calculations of the famous `Fisher Iris Dataset`_.

The plan is to obtain information for each class of the Iris species (
Setosa, Virginica, and Versicolor) calculated separately,
seizing the multi-processing of 3 cores at a time.

Finally we will set-up some alerts, just to let us know if any expected
results are obtained.

We will define some commands as well, to check the pipeline general
status.


Downloading the Data
--------------------

First of all we need to download the csv_ file, with the raw data to feed the
pipeline. We can get it from https://github.com/toros-astro/corral/raw/master/datasets/iris.csv
and copy it inside the ``my_pipeline`` directory.

If we take a glance at our files
at this point, it should look like::

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

A thing we need to be able to do, is finding paths dynamically, so we import
the *os* module. The import should look like

.. code-block:: python

    import logging
    import os


The ``CONNECTION`` variable specifies the *RFC-1738* format (used by SQLAlchemy_)
for database connection. Default should look something like this:

.. code-block:: python

    CONNECTION = "sqlite:///my_pipeline-dev.db"

With this instruction, a file ``pipeline-dev.db`` will be created in the same directory where
``in_corral.py`` is located, containing the SQLite_ database that we just defined.

.. seealso::

    For more information regarding other databases, you can search the
    SQLAlchemy documentation at:
    http://docs.sqlalchemy.org/en/latest/core/engines.html


At the end of the file we will add the following lines

.. code-block:: python

    PATH = os.path.abspath(os.path.dirname(__file__))
    IRIS_PATH = os.path.join(PATH, "iris.csv")

First line stores in the variable ``PATH`` the directory where ``settings.py`` is located.
The second line just creates a path to the file *iris.csv* that we downloaded before.


The Models
----------

Now our pipeline needs to know the looks of our data stored in the
database.

In ``my_pipeline/models.py`` file, we delete the ``Example`` class.
Then we modify the file to look just like this:

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


As we can see, the ``Name`` and ``Observation`` classes inherit from
``db.Model``, and by doing so, we let Corral know that these are
tables in our database.

The ``Name`` model will be in charge of storing every different name on our
dataset. Let's remember that the dataset has three different types of
Iris flowers: *setosa*, *versicolor* and *virginica*, which will translate to
three different instances of this model.
In this same class we have only three attributes.
The first one, ``__tablename__``, will determine the name of the table that will
be created on the database to make our data persistent (*Name* in our case).
``id`` is a column on the *Name* table for the primary key, with an integer
type.
Finally, the column ``name`` will hold the name of the species itself,
with a maximum length of 50 characters, and this name cannot repeat across the
column.

On the other hand, the model ``Observation`` has, besides the attributes 
``__tablename__`` and ``id``, references_ to the model ``Name`` (the attributes
``name_id`` and ``name``).
This implies that each instance of this table must have a name and 4 other columns
with floating point numbers to hold the other 4 columns of the dataset.

.. note::

    The models are models of the SQLAlchemy ORM in every sense; and
    ``db.Model`` is a `declarative_base`_

    To learn more about SQLAlchemy ORM please refer to their documentation on
    http://docs.sqlalchemy.org/en/rel_1_1/orm/tutorial.html

.. note::

    When we execute the line ``from corral import db``, we have available
    inside the ``db`` namespace, the namespaces for ``sqlalchemy``, 
    ``sqlalchemy.orm`` and ``sqlalchemy_utils``.

    Learn more about sqlalchemy_utils on: http://sqlalchemy-utils.readthedocs.org


To create the database, we need to execute the command:

.. code-block:: bash

    $ python in_corral.py createdb

After a confirmation question, the output should look like this:

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

We can read in the output, the SQL instructions used to create the tables
to make our models persistent, plus some extra tables used as support by corral,
like ``__corral_alerted__``

We can explore our recently created empty database, with the 
command ``python in_corral.py dbshell``


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
