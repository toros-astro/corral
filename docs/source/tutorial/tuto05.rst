Tutorial - Part #5 - Alerts
===========================

Alerts: Inform about some desired State
---------------------------------------

In a single phrase::

    An Alert is a step that does not store information, but it will send it to
    some other place, away from the pipeline.

In our infrastructure, an Alert is a View in the MVC pattern, since it is
responsible to inform some potential final user about some anomalous state
(desired or not) within the pipeline data.

The idea behind alerts is to design them as steps, but to add them one
or several destinations (Endpoints) on top; in the chosen models (?)

La idea detras de las alerts es diseñarlas como steps, pero ademas agregarles
uno varios destinos (Endpoint); en los modelos escogidos por   se serializen

Corral offers two default endpoints:

-   ``Email``: The model data is sent by email.
-   ``File``: The model data are written to a local file.


Creating an Alert
-----------------

In our example, we will write an Alert that writes each statistics of the data
to a file.

To do so, we edit the class MyAlert in ``my_pipeline/alerts.py``

.. code-block:: python

    from corral import run
    from corral.run import endpoints as ep

    from . import models

    class StatisticsAlert(run.Alert):

        model = models.Statistics
        conditions = []
        alert_to = [ep.File("statistics.log")]

An Alert's endpoints are added to the variable ``alert_to``.
The endpoint ``File`` only receives as a required parameter the path to the
file to write to, and optional parameters ``mode`` and ``enconding``.
The mode parameter refers to the mode the file is opened (``a`` append by
default); ``encoding`` refers to the encoding of the file to open (``utf-8`` by
default).

Finally, the last step is editing the variable ``ALERTS`` in ``settings.py``
so that it contains our new alert.

.. code-block:: python

    # The alerts
    ALERTS = ["irispl.alerts.StatisticsAlert"]

Once it's done, we can verify if out Alert is addded correctly by running the
command ``lsalerts``

.. code-block:: bash

    $ python in_corral.py lsalerts
    +-----------------+---------+---------+
    |   Alert Class   | Process | Groups  |
    +=================+=========+=========+
    | StatisticsAlert | 1       | default |
    +-----------------+---------+---------+
      TOTAL PROCESSES: 1
      DEBUG PROCESS: Enabled

To run the alert we just need to execute

.. code-block:: bash

    $ python in_corral check-alerts
    [INFO] Executing alert '<class 'irispl.alerts.StatisticsAlert'>' #1
    [INFO] SELECT CAST('test plain returns' AS VARCHAR(60)) AS anon_1
    [INFO] ()
    [INFO] SELECT CAST('test unicode returns' AS VARCHAR(60)) AS anon_1
    [INFO] ()
    [INFO] BEGIN (implicit)
    [INFO] SELECT count(*) AS count_1
    FROM (SELECT __corral_alerted__.model_ids AS __corral_alerted___model_ids
    FROM __corral_alerted__
    WHERE __corral_alerted__.model_table = ? AND __corral_alerted__.alert_path = ?) AS anon_1
    [INFO] ('Statistics', 'irispl.alerts.StatisticsAlert')
    [INFO] SELECT __corral_alerted__.model_ids AS __corral_alerted___model_ids
    FROM __corral_alerted__
    WHERE __corral_alerted__.model_table = ? AND __corral_alerted__.alert_path = ?
    [INFO] ('Statistics', 'irispl.alerts.StatisticsAlert')
    [INFO] SELECT "Statistics".id AS "Statistics_id", "Statistics".name_id AS "Statistics_name_id", "Statistics".mean_sepal_length AS "Statistics_mean_sepal_length", "Statistics".mean_sepal_width AS "Statistics_mean_sepal_width", "Statistics".mean_petal_length AS "Statistics_mean_petal_length", "Statistics".mean_petal_width AS "Statistics_mean_petal_width", "Statistics".min_sepal_length AS "Statistics_min_sepal_length", "Statistics".min_sepal_width AS "Statistics_min_sepal_width", "Statistics".min_petal_length AS "Statistics_min_petal_length", "Statistics".min_petal_width AS "Statistics_min_petal_width", "Statistics".max_sepal_length AS "Statistics_max_sepal_length", "Statistics".max_sepal_width AS "Statistics_max_sepal_width", "Statistics".max_petal_length AS "Statistics_max_petal_length", "Statistics".max_petal_width AS "Statistics_max_petal_width"
    FROM "Statistics"
    WHERE "Statistics".id NOT IN (?, ?, ?)
    [INFO] (1, 2, 3)
    [INFO] COMMIT
    [INFO] Done Alert '<class 'irispl.alerts.StatisticsAlert'>' #1


If we now check the content of the *statistics.log* file, we'll see the
following

.. code-block:: bash

    $ cat statistics.log
    [irispl-ALERT @ 2017-03-30T02:43:36.123542-15s] Check the object '<Statistics of 'Iris-setosa'>'
    [irispl-ALERT @ 2017-03-30T02:43:36.124799-15s] Check the object '<Statistics of 'Iris-versicolor'>'
    [irispl-ALERT @ 2017-03-30T02:43:36.126659-15s] Check the object '<Statistics of 'Iris-virginica'>'

As expected, we created a register of each created statistic. If we run
the Alert again, we'll see that no more registers are added, since Corral
keeps an internal record of the alerted models.

If we want to improve the alert message we can do so, redefining the method
``render_alert()`` of our Alert. This method receives three parameters:

- ``utcnow`` current date and time in UTC format.
- ``endpoint`` the endpoint to which we render the message.
-  ``obj`` the object we alert about.

For instance, if we wanted to improve the message so that it informs us about
all the statistics, we could write:

.. code-block:: python

        class StatisticsAlert(run.Alert):

            model = models.Statistics
            conditions = []
            alert_to = [ep.File("statistics.log")]

            def render_alert(self, utcnow, endpoint, obj):
                return """
                    ALERT@{now}: {name}
                        - mean_sepal_length = {mean_sepal_length}
                        - mean_sepal_width  = {mean_sepal_width}
                        - mean_petal_length = {mean_petal_length}
                        - mean_petal_width  = {mean_petal_width}
                    -------------------------------------------------------
                """.rstrip().format(
                    now=utcnow, name=obj.name.name,
                    mean_sepal_length=obj.mean_sepal_length,
                    mean_sepal_width=obj.mean_sepal_width,
                    mean_petal_length=obj.mean_petal_length,
                    mean_petal_width=obj.mean_petal_width)

This will generate a file like this:

.. code-block:: bash

    $ cat statistics.log

            ALERT@2017-03-30 03:35:56.951190: Iris-setosa
                - mean_sepal_length = 5.006
                - mean_sepal_width  = 3.418
                - mean_petal_length = 1.464
                - mean_petal_width  = 0.244
            -------------------------------------------------------
            ALERT@2017-03-30 03:35:56.952553: Iris-versicolor
                - mean_sepal_length = 5.936
                - mean_sepal_width  = 2.77
                - mean_petal_length = 4.26
                - mean_petal_width  = 1.326
            -------------------------------------------------------
            ALERT@2017-03-30 03:35:56.954868: Iris-virginica
                - mean_sepal_length = 6.588
                - mean_sepal_width  = 2.974
                - mean_petal_length = 5.552
                - mean_petal_width  = 2.026
            -------------------------------------------------------

Email Endpoint
^^^^^^^^^^^^^^

The ``Email`` endpoint takes a little bit more configuration.

First we need to configure the SMTP_ server (email server)
in ``settings.py``, like so

.. code-block:: python

   EMAIL = {
        "server": "smtp.foo.com:587",  # Host and port of SMTP server.
        "tls": True,  # If the smtp uses the TLS security
        "user": "foo@foo.com",  # User
        "password": "secret"  # Password
    }

Then when we add the endpoint to the alert, it is mandatory to add a list of
destinations in the ``to`` parameter.

.. code-block:: python

        class StatisticsAlert(run.Alert):

            model = models.Statistics
            conditions = []
            alert_to = [ep.File("statistics.log"),
                        ep.Email(to=["dest0@host.com", "dest1@host.com", ...])]

``Email`` accepts three other optional parameters:

-   ``sent_from`` a from email (by default we build one with the *user* and
    *host* of the SMTP_ configuration)
-   ``subject`` a subject for the sent emails (default:
    name of the alert + name of the project)
-   ``message`` a string that can have a slot to render the object, so that it
    can be used as a template to create the messages (it will use the method
    ``render_alert()`` of the alert by default.)


Selective Runs By Name and Groups
---------------------------------

Just like the steps can be run by their names, Alerts can also be run this way
by adding the parameter ``--alerts|-a`` to the ``check-alerts`` command.
It is also possible to add alerts to groups with the attribute ``groups`` in
Alert).
We can selectively run this groups using the flag ``--alert-groups|-ag``.


If you need more information, please check the tutorial for
:ref:`selective_steps_run`
