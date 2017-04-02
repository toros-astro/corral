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

Como se esperabase creo un registo por cada estadística creada. Si tramos
de volver a correr la Alert veremos que no se crean mas registros, ya que
corral mantiene un registro interno de los modelos alertados.

Si queremos mejorar el mensaje de alerta Podemos hacerlo redefiniendo el
método ``render_alert()`` de nuestra Alert; el cual recibe 3 parámetros:

- ``utcnow`` fecha y hora actual en formato utc.
- ``endpoint`` el endpoint para el cual estamos renderizando el mensaje.
-  ``obj`` el objeto sobre el cual hay que alertar.

Por ejemplo si quisieramos mejorar el mensaje para que informe sobre todas
las estadísticas se podria hacer:


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

Esto generaria un archivo como este:

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

El endpoint ``Email`` conlleva un poco mas configuración.

Primero es necesario configurar el servido SMTP_ (email server)
en ``settings.py`` de la siguiente forma

.. code-block:: python

   EMAIL = {
        "server": "smtp.foo.com:587",  # Host and port of SMTP server.
        "tls": True,  # If the smtp uses the TLS security
        "user": "foo@foo.com",  # User
        "password": "secret"  # Password
    }

Luego al agregar el endpoint al alerta es obligatorio agregar una lista
de destinos en el parámetro ``to``.

.. code-block:: python

        class StatisticsAlert(run.Alert):

            model = models.Statistics
            conditions = []
            alert_to = [ep.File("statistics.log"),
                        ep.Email(to=["dest0@host.com", "dest1@host.com", ...])]

Opcionalmente ``Email`` soporta tres parámetros mas:

-   ``sent_from`` un email origen (por defecto se construye con la
    *user* + *host* de la configuración del SMTP_.)
-   ``subject`` una subject para los emails enviados (default:
    nombre de la alerta + nombre del proyecto)
-   ``message``: un string que puede tener un espacio para renderizar el
    objeto para que sirva de template para crear los mensajes
    (por defecto usa el metodo ``render_alert()`` de la alerta)


Selective Runs By Name and Groups
---------------------------------

Asi como los steps pueden ejecutarse Alerts por su nombre agregando
el parámetro ``--alerts|-a`` al comando ``check-alerts``; y a su ves
es posible agregar alertas a grupos (con el atributo ``groups`` en la
Alert); y ejecutar estos grupos de manera selectiva con el flag
``--alert-groups|-ag``

Cualquier duda remitirse al tutorial de
:ref:`selective_steps_run`
