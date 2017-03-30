Tutorial - Part #4 - Steps
==========================

Steps: Processing Data
----------------------

After we execute the line ``python in_corral load`` we have the iris_ data loaded
in our database and now we want to calculate the mean, minimum and maximum
values for ``sepal_length``, ``sepal_width``, ``petal_length`` and ``petal_width``
in parallel for each species.

.. warning::

    All throughout this tutorial we have used SQLite as our database. SQLite
    does not support concurrency. Keep in mind this is just an excercise and
    a real pipeline should use a database like PostgreSQL_, MySQL_, Oracle_
    or something even more powerful like Hive_


A Model for the Statistics
--------------------------

To hold the statistics, we will define a model with the three statistical
measures for the four observed properties of the species.
It will also hold a reference to the Iris species to which it belong
(a relation to the ``Name`` table.)

To do so, we add at the end of ``my_pipeline/models.py``, the class

.. code-block:: python

    class Statistics(db.Model):

        __tablename__ = 'Statistics'

        id = db.Column(db.Integer, primary_key=True)

        name_id = db.Column(
            db.Integer, db.ForeignKey('Name.id'), nullable=False, unique=True)
        name = db.relationship(
            "Name", backref=db.backref("statistics"), uselist=False)

        mean_sepal_length = db.Column(db.Float, nullable=False)
        mean_sepal_width = db.Column(db.Float, nullable=False)
        mean_petal_length = db.Column(db.Float, nullable=False)
        mean_petal_width = db.Column(db.Float, nullable=False)

        min_sepal_length = db.Column(db.Float, nullable=False)
        min_sepal_width = db.Column(db.Float, nullable=False)
        min_petal_length = db.Column(db.Float, nullable=False)
        min_petal_width = db.Column(db.Float, nullable=False)

        max_sepal_length = db.Column(db.Float, nullable=False)
        max_sepal_width = db.Column(db.Float, nullable=False)
        max_petal_length = db.Column(db.Float, nullable=False)
        max_petal_width = db.Column(db.Float, nullable=False)

        def __repr__(self):
            return "<Statistics of '{}'>".format(self.name.name)

If you have already read our last tutorial, the only differences this model has
with the previous ones are the parameters ``unique=True`` and ``userlist=False``
on the lines where we define the relation.
These are used to enforce that each instance of ``Name`` has one and
only one instance of ``Statistics``.

To create the table we execute once again on the command line
``python in_corral createdb`` and only the new table will be crated without
changing the shape and form of the previous ones.

The Steps
---------

We will create four steps in the ``my_pypeline/steps.py`` module.


#. Step 1: Creating Statistics for each Name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, uncomment on the import section the line
``# from . import models``; and then edit the class ``MyStep``
so that it looks like the following:


.. code-block:: python

    class StatisticsCreator(run.Step):

        model = models.Name
        conditions = []

        def process(self, name):
            stats = self.session.query(models.Statistics).filter(
                models.Statistics.name_id==name.id).first()
            if stats is None:
                yield models.Statistics(
                    name_id=name.id,
                    mean_sepal_length=0., mean_sepal_width=0.,
                    mean_petal_length=0., mean_petal_width=0.,
                    min_sepal_length=0., min_sepal_width=0.,
                    min_petal_length=0., min_petal_width=0.,
                    max_sepal_length=0., max_sepal_width=0.,
                    max_petal_length=0., max_petal_width=0.)


This step's goal is to create an instance of ``Statistics`` for each different
name it finds on the ``Name`` table.

Notice that we let the *Step* know in the variable ``model`` that it will
be working with unconditioned instances of the model ``Name``.
Corral will sequentially send the stored (by the Loader) instances, that
meet the conditions (all of the instances in our case).

The ``process()`` method receives each instance of ``Name`` and if there is no
associated instance of ``Statistic``, it will create one with all the values
set to *0*, yielding back the control to corral (with ``yield``).


#. Step 2: Calculating Statistics for "Iris-Setosa"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If we create a Step ``SetosaStatistics`` and we assign to its model variable
the class ``Statistics`` and we add the ``conditions``:

.. code-block:: python

    conditions = [
            models.Statistics.name.has(name="Iris-setosa"),
            models.Statistics.mean_sepal_length==0.]

we will create a step that only calculates the statistics of **Iris-setosa**
if they were not previously calculated (the mean for ``sepal_length`` is ``0.``)

The ``process()`` method will be passed by parameter said instance
of ``Statistics``. To fill the statistics out,
the complete code for this step will be:

.. code-block:: python

    class SetosaStatistics(run.Step):

        model = models.Statistics
        conditions = [
            models.Statistics.name.has(name="Iris-setosa"),
            models.Statistics.mean_sepal_length==0.]

        def process(self, stats):
            sepal_length, sepal_width, petal_length, petal_width = [], [], [], []
            for obs in stats.name.observations:
                sepal_length.append(obs.sepal_length)
                sepal_width.append(obs.sepal_width)
                petal_length.append(obs.petal_length)
                petal_width.append(obs.petal_width)

            stats.mean_sepal_length = sum(sepal_length) / len(sepal_length)
            stats.mean_sepal_width = sum(sepal_width) / len(sepal_width)
            stats.mean_petal_length = sum(petal_length) / len(petal_length)
            stats.mean_petal_width = sum(petal_width) / len(petal_width)

            stats.min_sepal_length = min(sepal_length)
            stats.min_sepal_width = min(sepal_width)
            stats.min_petal_length = min(petal_length)
            stats.min_petal_width = min(petal_width)

            stats.max_sepal_length = max(sepal_length)
            stats.max_sepal_width = max(sepal_width)
            stats.max_petal_length = max(petal_length)
            stats.max_petal_width = max(petal_width)


#. Step 3 and 4: Calculating Statistics for "Iris-Virginica" and "Iris-Versicolor"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The last two steps are exactly the same as the previous ones, except for the
variables ``model`` and ``conditions``.

.. code-block:: python

    class VersicolorStatistics(run.Step):

        model = models.Statistics
        conditions = [
            models.Statistics.name.has(name="Iris-versicolor"),
            models.Statistics.mean_sepal_length==0.]

        def process(self, stats):
            # SAME CODE AS SetosaStatistics.process


    class VirginicaStatistics(run.Step):

        model = models.Statistics
        conditions = [
            models.Statistics.name.has(name="Iris-virginica"),
            models.Statistics.mean_sepal_length==0.]

        def process(self, stats):
            # SAME CODE AS SetosaStatistics.process


#. Step 5: Add the new steps to ``settings.STEPS``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The last piece is to make your pipelne aware of the new steps. For
this, you need to add the full python path to the ``STEPS`` list inside
the settings.py file.

.. code-block:: python

    # Pipeline processor steps
    STEPS = [
        "pipeline.steps.StatisticsCreator",
        "pipeline.steps.SetosaStatistics",
        "pipeline.steps.VirginicaStatistics",
        "pipeline.steps.VersicolorStatistics"]

Finally you can inspect the registered steps with the ``lssteps`` command

.. code-block:: bash

    $python in_corral.py lssteps
    +----------------------+---------+---------+
    |      Step Class      | Process | Groups  |
    +======================+=========+=========+
    | SetosaStatistics     | 1       | default |
    | StatisticsCreator    | 1       | default |
    | VersicolorStatistics | 1       | default |
    | VirginicaStatistics  | 1       | default |
    +----------------------+---------+---------+
      TOTAL PROCESSES: 4
      DEBUG PROCESS: Enabled

Also note that (by default) every step is on the **default** group.


.. note::

    The command  ``python in_corral groups`` shows all available groups
    in steps and alerts.


Running The Steps
-----------------

The main command to run the corral steps is **run**.

when you excecute ``python in_corral run`` all the steps are executed
asynchronous. If for some particular case you need to run the steps sequentially
(in the same order of ``settings.STEPS``) you can add the ``--sync`` flag.


.. warning::

    By design, SQLite_ is not capable to serve as a multiprocess database, so it
    is highly recommended to run the steps with the ``--sync`` flag.

Here is a **run** example output

.. code-block:: bash

    $ python in_corral.py run --sync
    [INFO] Executing step '<class 'pipeline.steps.SetosaStatistics'>' #1
    [INFO] SELECT CAST('test plain returns' AS VARCHAR(60)) AS anon_1
    [INFO] ()
    [INFO] SELECT CAST('test unicode returns' AS VARCHAR(60)) AS anon_1
    [INFO] ()
    [INFO] BEGIN (implicit)
    [INFO] SELECT "Statistics".id AS "Statistics_id", "Statistics".name_id AS "Statistics_name_id", "Statistics".mean_sepal_length AS "Statistics_mean_sepal_length", "Statistics".mean_sepal_width AS "Statistics_mean_sepal_width", "Statistics".mean_petal_length AS "Statistics_mean_petal_length", "Statistics".mean_petal_width AS "Statistics_mean_petal_width", "Statistics".min_sepal_length AS "Statistics_min_sepal_length", "Statistics".min_sepal_width AS "Statistics_min_sepal_width", "Statistics".min_petal_length AS "Statistics_min_petal_length", "Statistics".min_petal_width AS "Statistics_min_petal_width", "Statistics".max_sepal_length AS "Statistics_max_sepal_length", "Statistics".max_sepal_width AS "Statistics_max_sepal_width", "Statistics".max_petal_length AS "Statistics_max_petal_length", "Statistics".max_petal_width AS "Statistics_max_petal_width"
    FROM "Statistics"
    WHERE (EXISTS (SELECT 1
    FROM "Name"
    WHERE "Name".id = "Statistics".name_id AND "Name".name = ?)) AND "Statistics".mean_sepal_length = ?
    [INFO] ('Iris-setosa', 0.0)
    [INFO] COMMIT
    [INFO] Done Step '<class 'pipeline.steps.SetosaStatistics'>' #1
    [INFO] Executing step '<class 'pipeline.steps.StatisticsCreator'>' #1
    [INFO] BEGIN (implicit)
    [INFO] SELECT "Name".id AS "Name_id", "Name".name AS "Name_name"
    FROM "Name"
    ...


.. _selective_steps_run:

Selective Steps Runs By Name and Groups
---------------------------------------

In some cases it is useful to run only a single or a group of steps.


Run by Name
^^^^^^^^^^^

You can run a single step by using the ``--steps|-s`` flag followed by
the class-names of the steps you want to run.

.. code-block:: bash

    $ python in_corral.py run --steps SetosaStatistics VersicolorStatistics
    [INFO] Executing step '<class 'irispl.steps.SetosaStatistics'>' #1
    [INFO] Executing step '<class 'irispl.steps.VersicolorStatistics'>' #1
    ...


Run by Groups
^^^^^^^^^^^^^

One of the most important concepts with Corral steps is the notion of groups.

Certain steps can be grouped together by adding a ``groups`` attribute to
a Step class. For exampe, if we want to add the tree statiscis calculators
steps to a ``statistics`` group, we'd write:


.. code-block:: python

    class SetosaStatistics(run.Step):
        model = models.Statistics
        conditions = [
            models.Statistics.name.has(name="Iris-versicolor"),
            models.Statistics.mean_sepal_length==0.]
        groups = ["default", "statistics"]

        ...


    class VersicolorStatistics(run.Step):

        model = models.Statistics
        conditions = [
            models.Statistics.name.has(name="Iris-versicolor"),
            models.Statistics.mean_sepal_length==0.]
        groups = ["default", "statistics"]

        ...


    class VirginicaStatistics(run.Step):

        model = models.Statistics
        conditions = [
            models.Statistics.name.has(name="Iris-virginica"),
            models.Statistics.mean_sepal_length==0.]
        groups = ["default", "statistics"]

You can check the changes on the column ``Groups`` by running ``lssteps`` again

.. code-block:: bash

    $ python in_corral.py lssteps
    +----------------------+---------+--------------------+
    |      Step Class      | Process |       Groups       |
    +======================+=========+====================+
    | SetosaStatistics     | 1       | default:statistics |
    | StatisticsCreator    | 1       | default            |
    | VersicolorStatistics | 1       | default:statistics |
    | VirginicaStatistics  | 1       | default:statistics |
    +----------------------+---------+--------------------+
      TOTAL PROCESSES: 4
      DEBUG PROCESS: Enabled

You can also list only the steps of a particular group with the
``--groups|-g`` flag

.. code-block:: bash

    $ python in_corral.py lssteps -g statistics
    +----------------------+---------+--------------------+
    |      Step Class      | Process |       Groups       |
    +======================+=========+====================+
    | SetosaStatistics     | 1       | default:statistics |
    | VersicolorStatistics | 1       | default:statistics |
    | VirginicaStatistics  | 1       | default:statistics |
    +----------------------+---------+--------------------+
      TOTAL PROCESSES: 3
      DEBUG PROCESS: Enabled

Finally, you can run the group of your choice with the ``--step-groups|--sg``
flag on the **run** command


.. code-block:: bash

    $ python in_corral.py run -sg statistics
    [INFO] Executing step '<class 'irispl.steps.SetosaStatistics'>' #1
    [INFO] Executing step '<class 'irispl.steps.VersicolorStatistics'>' #1
    [INFO] Executing step '<class 'irispl.steps.VirginicaStatistics'>' #1
    ...

As you can see, the ``StatisticsCreator`` step didn't run.





