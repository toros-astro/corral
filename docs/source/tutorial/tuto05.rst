Tutorial - Part #5 - Alerts
===========================

Alerts: Inform about some desired State
---------------------------------------

En una sola frase::

    Una Alerta es un step que no guarda información, sino que la envia a
    algun lugar ajeno al pipeline.

En nuestra infraestructura ocupa el lugar e los Views en el patron MVC, ya que
es la responsable de informar a un potencial usuario final de algun estado
anomalo (deseado o no) dentro de los datos del pipeline.

La idea detras de las alerts es diseñarlas como steps, pero ademas agregarles
uno varios destinos (Endpoint); en los modelos escogidos por   se serializen

Por defecto Corral ofrece dos endpoints:

-   ``Email``: Los datos del modelo se envian por emails.
-   ``File``: Los datos del modelo se escriben en un archvo local.


Creando una alerta
------------------

En nuestro ejemplo vamos a escribir una Alert que escriba
cada estadística de los datos en un archivo.

To do so, we aedit  the class MyAlert in ``my_pipeline/alerts.py``

.. code-block:: python

    from corral import run
    from corral.run import endpoints as ep

    from . import models

    class StatisticsAlert(run.Alert):

        model = models.Statistics
        conditions = []
        alert_to = [ep.File("statistics.log")]

los endpoits en una Alert se agregan en la variable ``alert_to``.
El endpoint ``File`` recibe como parametros obligatorios unicamente
el ``path`` al archivo donde escribir, y como opcionales ``mode`` que
es el modo de apertura del archivo (por defecto ``a`` append);
``encoding`` que se refiere al encoding del archivo abierto (por defecto
``utf-8``)

Finalmente el ultimo paso es ir a ``settings.py`` y editar la variable
``ALERTS`` para que contenga nuestra nueva alert.

.. code-block:: python

    # The alerts
    ALERTS = ["irispl.alerts.StatisticsAlert"]

Hecho esto último, podemos verificar si nuestra Alert se agrego correctamente
con el comando ``lsalerts``

.. code-block:: bash

    $ python in_corral.py lsalerts
    +-----------------+---------+---------+
    |   Alert Class   | Process | Groups  |
    +=================+=========+=========+
    | StatisticsAlert | 1       | default |
    +-----------------+---------+---------+
      TOTAL PROCESSES: 1
      DEBUG PROCESS: Enabled


y para correrla alerta solo es necesario ejecutar

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


ahora si vemos el contenido del archivo *statistics.log* veremos lo siguiente

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











