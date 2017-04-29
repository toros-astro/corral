Tutorial - Part #3 - Loaders
============================

Loading Data on the Stream: Loader
----------------------------------

At this point we already have:

- Data in a file ``iris.csv``.
- The ``settings.py`` containing the path to the file.
- Models already defined (in ``models.py``) to store *Name* and the
  *Observations*

Now the next step is to parse data in the ``iris.csv`` on the
*modelos* working with Corral's **Loader**.

The loaders idea is to work as an entry point for raw data to the pipeline
processing chain. Opposed to the *Steps* (on the next tutorial section),
the *Loaders* are not restricted by the defined models of our stream.

As everythin in Corral, the **Loaders** are defined as a Class, suggested to be
in a separated file named ``load.py`` of your project. Also this Class must be registered
in the ``settings.py`` file.

Reading iris.csv data
^^^^^^^^^^^^^^^^^^^^^

Python can work with CSV files module
https://docs.python.org/3.5/library/csv.html which contains a
parser capable to transform each row in the file into a dictionary
with it's keys as column names

So for instance

.. code-block:: pycon

    $ python in_corral.py shell # open a shell inside the pipeline environment
    LOAD: Name, Observation (my_pipeline.models)
    LOAD: session (sqlalchemy.orm.session)
    --------------------------------------------------------------------------------

    # import the settings to load the IRIS_PATH
    >>> from corral.conf import settings
    >>> settings.IRIS_PATH
    'path/to/my_pipeline/iris.csv'

    # import the csv handler module and also read the file with it and print
    # the output into the console
    >>> import csv
    >>> for row in csv.DictReader(open(settings.IRIS_PATH)):
    ...     print row
    ...
    {'SepalLength': '5.1', 'PetalLength': '1.4', 'PetalWidth': '0.2', 'SepalWidth': '3.5', 'Name': 'Iris-setosa'}
    {'SepalLength': '4.9', 'PetalLength': '1.4', 'PetalWidth': '0.2', 'SepalWidth': '3.0', 'Name': 'Iris-setosa'}
    {'SepalLength': '4.7', 'PetalLength': '1.3', 'PetalWidth': '0.2', 'SepalWidth': '3.2', 'Name': 'Iris-setosa'}
    {'SepalLength': '4.6', 'PetalLength': '1.5', 'PetalWidth': '0.2', 'SepalWidth': '3.1', 'Name': 'Iris-setosa'}
    {'SepalLength': '5.0', 'PetalLength': '1.4', 'PetalWidth': '0.2', 'SepalWidth': '3.6', 'Name': 'Iris-setosa'}
    {'SepalLength': '5.4', 'PetalLength': '1.7', 'PetalWidth': '0.4', 'SepalWidth': '3.9', 'Name': 'Iris-setosa'}
    {'SepalLength': '4.6', 'PetalLength': '1.4', 'PetalWidth': '0.3', 'SepalWidth': '3.4', 'Name': 'Iris-setosa'}
    {'SepalLength': '5.0', 'PetalLength': '1.5', 'PetalWidth': '0.2', 'SepalWidth': '3.4', 'Name': 'Iris-setosa'}
    # ... MANY MORE LINES ... #

To write the loader what we should do is to open the file
``pipeline/load.py`` which should look like this:

.. code-block:: python

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    # =============================================================================
    # DOCS
    # =============================================================================

    """pipeline main loader

    """


    # =============================================================================
    # IMPORTS
    # =============================================================================

    from corral import run


    # =============================================================================
    # LOADER
    # =============================================================================

    class Loader(run.Loader):

        def generate(self):
            # write your logic here
            pass


First we need to import the python module ``csv``, the ``settings`` from
corral and import from our pipeline the models module, in order to
generate them using the loader. With all this the import block should 
have this looks:

.. code-block:: python

    # =============================================================================
    # IMPORTS
    # =============================================================================

    import csv

    from corral import run
    from corral.conf import settings

    from my_pipeline import models


The ``Loader.generate()`` method now could start reading the csv file
and screen print it, as like we did in the interactive session:

.. code-block:: python

    class Loader(run.Loader):

        def generate(self):
            for row in csv.DictReader(open(settings.IRIS_PATH)):
                print row

Now if we go to the command line and execute

.. code-block:: bash

    $ python in_corral.py load

We will get an output just like the following:

.. code-block:: bash

    [my_pipeline-INFO @ 2016-01-10 17:59:00,393] Executing loader '<class 'my_pipeline.load.Loader'>' #1
    {'SepalLength': '5.1', 'PetalLength': '1.4', 'PetalWidth': '0.2', 'SepalWidth': '3.5', 'Name': 'Iris-setosa'}
    {'SepalLength': '4.9', 'PetalLength': '1.4', 'PetalWidth': '0.2', 'SepalWidth': '3.0', 'Name': 'Iris-setosa'}
    {'SepalLength': '4.7', 'PetalLength': '1.3', 'PetalWidth': '0.2', 'SepalWidth': '3.2', 'Name': 'Iris-setosa'}
    {'SepalLength': '4.6', 'PetalLength': '1.5', 'PetalWidth': '0.2', 'SepalWidth': '3.1', 'Name': 'Iris-setosa'}
    {'SepalLength': '5.0', 'PetalLength': '1.4', 'PetalWidth': '0.2', 'SepalWidth': '3.6', 'Name': 'Iris-setosa'}
    {'SepalLength': '5.4', 'PetalLength': '1.7', 'PetalWidth': '0.4', 'SepalWidth': '3.9', 'Name': 'Iris-setosa'}
    {'SepalLength': '4.6', 'PetalLength': '1.4', 'PetalWidth': '0.3', 'SepalWidth': '3.4', 'Name': 'Iris-setosa'}
    {'SepalLength': '5.0', 'PetalLength': '1.5', 'PetalWidth': '0.2', 'SepalWidth': '3.4', 'Name': 'Iris-setosa'}
    {'SepalLength': '4.4', 'PetalLength': '1.4', 'PetalWidth': '0.2', 'SepalWidth': '2.9', 'Name': 'Iris-setosa'}
    {'SepalLength': '4.9', 'PetalLength': '1.5', 'PetalWidth': '0.1', 'SepalWidth': '3.1', 'Name': 'Iris-setosa'}
    # ... MANY MORE LINES ... #
    {'SepalLength': '6.2', 'PetalLength': '5.4', 'PetalWidth': '2.3', 'SepalWidth': '3.4', 'Name': 'Iris-virginica'}
    {'SepalLength': '5.9', 'PetalLength': '5.1', 'PetalWidth': '1.8', 'SepalWidth': '3.0', 'Name': 'Iris-virginica'}
    [my_pipeline-INFO @ 2016-01-10 17:59:00,396] Done Loader '<class 'my_pipeline.load.Loader'>' #1

Which tells us that the loader is able to acces the ``iris.csv`` file, and printing
its content.

As a matter of order and safety it is convenient that files close
explicitly just one time per process. To get this we could just redefine
the ``Loader`` method's ``setup`` and ``teardown``.

``setup`` is executed just before ``generate`` and it is the best place
to open our file. On the other hand ``teardown`` gets information related to
the error state of the ``generate`` method, and runs just after this one ends.
The simplest way to implement this is the following:

.. code-block:: python

    class Loader(run.Loader):

    def setup(self):
        # we open the file and assign it to an instance variable
        self.fp = open(settings.IRIS_PATH)

    def teardown(self, *args):
        # checking that the file is really open
        if self.fp and not self.fp.closed:
            self.fp.close()

    def generate(self):
        # now we make use of "self.fp" for the reader
        for row in csv.DictReader(self.fp):
            print row

For the sake of simplicity now we split the processing into two sides:

#. A method named ``get_name_instance`` which receives the row as a parameter
   and returns a ``my_pipeline.models.Name`` instance referred to the *name*
   of such file (*Iris-virginica*, *Iris-versicolor*, or *Iris-setosa*).
   Something to take into account is that every time a name is non existant
   this method must create a new one and to store this model before returning it.
#. A method named ``store_observation`` which receives the row as a parameter, and
   also the instance of ``my_pipeline.models.Name`` just created by the previous
   model. This method just needs to return the instance and deliver it to the 
   loader without saving it.


.. warning::

    This tutorial is going to assume a certain level of knowledge in sessions,
    queries from SQLAlchemy_.
    If any doubts arise, please go to `orm tutorial`_


First of all we define the method ``get_name_instance``


.. code-block:: python

    def get_name_instance(self, row):
        name = self.session.query(models.Name).filter(
            models.Name.name == row["Name"]).first()

        # if exists we don't need to create one
        if name is None:
            name = models.Name(name=row["Name"])

            # we need to add the new instance and save it
            self.save(name)
            self.session.commit()

        return name

now ``store_observation``:

.. code-block:: python

    def store_observation(self, row, name):
        return models.Observation(
            name=name,
            sepal_length=row["SepalLength"], sepal_width=row["SepalWidth"],
            petal_length=row["PetalLength"], petal_width=row["PetalWidth"])


Finally the ``generate`` method would be defined as:

.. code-block:: python

    def generate(self):
        # now we use the "self.fp" for the reader
        for row in csv.DictReader(self.fp):
            name = self.get_name_instance(row)
            obs = self.store_observation(row, name)
            yield obs

In the very last line with the ``yield`` command,
we deliver the instance created by ``store_observation`` 
to corral so it would be persisted when the time comes.


.. warning::

    Bare in mind that ``generate`` *by default* can only return ``None``
    or an *models* instances *iterator* or a single *model*. 
    If you wish for it to generate another object it is necessary to redefine
    the ``validate`` method which is not treated on this tutorial.


Finally the loader should be defined as:


.. code-block:: python

class Loader(run.Loader):

    def setup(self):
        # we open the file and assign it to an instance variable
        self.fp = open(settings.IRIS_PATH)

    def teardown(self, *args):
        # checking that the file is really open
        if self.fp and not self.fp.closed:
            self.fp.close()

    def get_name_instance(self, row):
        name = self.session.query(models.Name).filter(
            models.Name.name == row["Name"]).first()

        # if exists we need don't need to create one
        if name is None:
            name = models.Name(name=row["Name"])

            # we need to add the new instance and save it
            self.save(name)
            self.session.commit()

        return name

    def store_observation(self, row, name):
        return models.Observation(
            name=name,
            sepal_length=row["SepalLength"], sepal_width=row["SepalWidth"],
            petal_length=row["PetalLength"], petal_width=row["PetalWidth"])

    def generate(self):
        # now we make use of "self.fp" for the reader
        for row in csv.DictReader(self.fp):
            name = self.get_name_instance(row)
            obs = self.store_observation(row, name)
            yield obs


.. note::

    If you wish to register another name for the loader class, just update the value
    of the ``LOADER`` variable in ``settings.py``.

Now when we run 

.. code-block:: bash

    $ python in_corral load

the result will be a list of sql commands that should look like this:

.. code-block:: bash

    ...
    [my_pipeline-INFO @ 2016-01-10 19:10:21,800] ('Iris-setosa', 1, 0)
    [my_pipeline-INFO @ 2016-01-10 19:10:21,801] INSERT INTO "Observation" (name_id, sepal_length, sepal_width, petal_length, petal_width) VALUES (?, ?, ?, ?, ?)
    [my_pipeline-INFO @ 2016-01-10 19:10:21,801] (1, 4.6, 3.4, 1.4, 0.3)
    [my_pipeline-INFO @ 2016-01-10 19:10:21,802] SELECT "Name".id AS "Name_id", "Name".name AS "Name_name"
    FROM "Name"
    WHERE "Name".name = ?
     LIMIT ? OFFSET ?
    [my_pipeline-INFO @ 2016-01-10 19:10:21,802] ('Iris-setosa', 1, 0)
    [my_pipeline-INFO @ 2016-01-10 19:10:21,804] INSERT INTO "Observation" (name_id, sepal_length, sepal_width, petal_length, petal_width) VALUES (?, ?, ?, ?, ?)
    [my_pipeline-INFO @ 2016-01-10 19:10:21,804] (1, 5.0, 3.4, 1.5, 0.2)
    ...

We can explore the loaded data with:

.. code-block:: bash

    $ python in_corral.py dbshell
    Connected to: Engine(sqlite:///my_pipeline-dev.db)
    Type 'exit;' or '<CTRL> + <D>' for exit the shell

    SQL> select * from observation limit 10;
    +----+---------+--------------+-------------+--------------+-------------+
    | id | name_id | sepal_length | sepal_width | petal_length | petal_width |
    +====+=========+==============+=============+==============+=============+
    | 1  | 1       | 5.100        | 3.500       | 1.400        | 0.200       |
    | 2  | 1       | 4.900        | 3           | 1.400        | 0.200       |
    | 3  | 1       | 4.700        | 3.200       | 1.300        | 0.200       |
    | 4  | 1       | 4.600        | 3.100       | 1.500        | 0.200       |
    | 5  | 1       | 5            | 3.600       | 1.400        | 0.200       |
    | 6  | 1       | 5.400        | 3.900       | 1.700        | 0.400       |
    | 7  | 1       | 4.600        | 3.400       | 1.400        | 0.300       |
    | 8  | 1       | 5            | 3.400       | 1.500        | 0.200       |
    | 9  | 1       | 4.400        | 2.900       | 1.400        | 0.200       |
    | 10 | 1       | 4.900        | 3.100       | 1.500        | 0.100       |
    +----+---------+--------------+-------------+--------------+-------------+
    SQL>

Or more easily with Python:

.. code-block:: python

    >>> for obs in session.query(Observation).all():
    ...     print obs
    ...
    [my_pipeline-INFO @ 2016-01-10 19:24:20,555] SELECT CAST('test plain returns' AS VARCHAR(60)) AS anon_1
    [my_pipeline-INFO @ 2016-01-10 19:24:20,556] ()
    [my_pipeline-INFO @ 2016-01-10 19:24:20,556] SELECT CAST('test unicode returns' AS VARCHAR(60)) AS anon_1
    [my_pipeline-INFO @ 2016-01-10 19:24:20,556] ()
    [my_pipeline-INFO @ 2016-01-10 19:24:20,557] BEGIN (implicit)
    [my_pipeline-INFO @ 2016-01-10 19:24:20,558] SELECT "Observation".id AS "Observation_id", "Observation".name_id AS "Observation_name_id", "Observation".sepal_length AS "Observation_sepal_length", "Observation".sepal_width AS "Observation_sepal_width", "Observation".petal_length AS "Observation_petal_length", "Observation".petal_width AS "Observation_petal_width"
    FROM "Observation"
    [my_pipeline-INFO @ 2016-01-10 19:24:20,558] ()
    <my_pipeline.models.Observation object at 0x7fd14f45ee90>
    <my_pipeline.models.Observation object at 0x7fd14f45e9d0>
    <my_pipeline.models.Observation object at 0x7fd14f45eb50>
    <my_pipeline.models.Observation object at 0x7fd14f45e950>

    >>> for name in session.query(Name).all():
    ...     print name
    ...
    [my_pipeline-INFO @ 2016-01-10 19:26:01,907] SELECT "Name".id AS "Name_id", "Name".name AS "Name_name"
    FROM "Name"
    [my_pipeline-INFO @ 2016-01-10 19:26:01,907] ()
    <my_pipeline.models.Name object at 0x7fd14f414a50>
    <my_pipeline.models.Name object at 0x7fd14f414b10>
    <my_pipeline.models.Name object at 0x7fd14f414bd0>

This output could be improved, since it doesn't give much information.
To do this, we can redefine the ``__repr__`` method for each model 
(https://docs.python.org/2/reference/datamodel.html#object.__repr__)


Improving the interactive session instance feedback
----------------------------------------------------

We can define the ``__repr__`` of ``Name`` as:

.. code-block:: python

    class Name(db.Model):

        ...

        def __repr__(self):
            return "<Name '{}' {}>".format(self.name, self.id)

and of ``Observation`` like this:

.. code-block:: python

    class Observation(db.Model):

        ...

        def __repr__(self):
            return "<Observation ({}, {}, {}, {}, {}) {}>".format(
                self.name.name,
                self.sepal_length, self.sepal_width,
                self.petal_length, self.petal_width, self.id)


.. code-block:: bash

    $ python in_corral.py shell --shell plain
    LOAD: Name, Observation (my_pipeline.models)
    LOAD: session (sqlalchemy.orm.session)
    --------------------------------------------------------------------------------
    >>> for obs in session.query(Observation).all():
    ...     print obs
    ...
    <Observation (Iris-setosa, 5.1, 3.5, 1.4, 0.2) 1>
    <Observation (Iris-setosa, 4.9, 3.0, 1.4, 0.2) 2>
    <Observation (Iris-setosa, 4.7, 3.2, 1.3, 0.2) 3>

    # Or we could search for every versicolor
    >>> name_versicolor = session.query(Name).filter(Name.name=="Iris-versicolor").first()
    >>>  name_versicolor.observations
    ...
    [<Observation (Iris-versicolor, 7.0, 3.2, 4.7, 1.4) 51>,
     <Observation (Iris-versicolor, 6.4, 3.2, 4.5, 1.5) 52>,
     <Observation (Iris-versicolor, 6.9, 3.1, 4.9, 1.5) 53>,
     <Observation (Iris-versicolor, 5.5, 2.3, 4.0, 1.3) 54>,
     <Observation (Iris-versicolor, 6.5, 2.8, 4.6, 1.5) 55>,
     ...]

