Tutorial - Part #6 - Quality Assurance
======================================

This final section of the turorial are not necesary for write a Pipeline. Here
we try to elavorate some concepts and tools to make you confident about your
data reduction. So here you gonna find the most unique feature of all
pipelene frameworks: An integrated Quality Assurance (QA) for make thrustworty
pipelines.


Some words about QA
-------------------

In "*Total Quality Control*" (Feigenbaum, 1983) Feigenbaum
defines software quality as

.. pull-quote::

  "Quality is a customer determination, not an engineer's determination,
  not a marketing determination, nor a general management determination.
  It is based on the customer's actual experience with the product or service,
  measured against his or her requirements --
  stated or unstated, conscious or merely sensed, technically operational or
  entirely subjective --
  and always representing a moving target in a competitive market"

In our context, a customer is not a single person but a role that
our scientific requirements define, and the engineers are responsible
for the design and development of a pipeline able to satisfy
the functionality defined in those requirements. Measuring the
quality of software is a task that involves the extraction of qualitative
and quantitative metrics. One of the most common ways
to measure Software Quality is Code Coverage (CC). To understand
CC is necessary to define first the idea behind unit-testing.
The unit-test objective is to isolate each part of the program and
show that the individual parts are correct Jazayeri (2007). Following
this, the CC is the ratio of code being executed by the
tests –usually expressed as a percentage– (Miller and Maloney,
1963). Another metric in which we are interested, is the maintainability
of the software. This may seem like a subjective parameter,
but it can be measured using a standardization of code
style; putting the number of style deviations as a tracer of code
maintainability.


What is QA for Corral
---------------------

Como diimos en el parrafo anterior, la QA es una medida subjetiva.
Por consiguiente Corral ofrece herramientas para dejar el al autor de un
pipeline que desee tener un cordigo de mas calidad evaluar 3 caracteristicas
relacionadas a la funcionalidad Esperada (unit-testing), cantidad de codigo
probada por los tests (coverage) y una medida de cuan legible es el codigo
y por ende que tan mantenible es el pipeline por developers que no sean
el autor original (style). Finalmente se ofrece 3 herramientas ara genear
un reporte de estado global para tner una idea de la calidad del pipeline
y poder informarla a todos los stackholders.

En resumen, es trabajo del desarrolador del pipeline estblecer:

- Cuales son los test minimos para probar el funcionamiento de su pipeline
  (si no programe cosas que no valen)
- Asumir que esos test establecen la linea base de toda la calidad del
  pipeline
- Asumir riesgos de su propio codigo.

.. note::

    Siguiendo la idea de sujetividad, esta herramienta es opcional, nuestro
    diseño original parte de saber a priori con que confianza deplegamos
    nuevas versiones de un pipeline basados en una "linea-base" bien
    establecida.


Unit-Testing
------------

From Wikipedia:

.. pull-quote::

    Intuitively, one can view a unit as the smallest testable part of an
    application. In procedural programming, a unit could be an entire module,
    but it is more commonly an individual function or procedure.
    In object-oriented programming, a unit is often an entire interface,
    such as a class.

    Because some classes may have references to other classes, testing a class
    can frequently spill over into testing another class. A common example of
    this is classes that depend on a database: in order to test the class, the
    tester often writes code that interacts with the database. This is a
    mistake, because a unit test should usually not go outside of its own
    class boundary, and especially should not cross such process/network
    boundaries because this can introduce unacceptable performance problems
    to the unit test-suite. Crossing such unit boundaries turns unit tests
    into integration tests, and when test cases fail, makes it less clear
    which component is causing the failure. Instead, the software developer
    should create an abstract interface around the database queries, and then
    implement that interface with their own mock object. By abstracting this
    necessary attachment from the code (temporarily reducing the net effective
    coupling), the independent unit can be more thoroughly tested than may
    have been previously achieved. This results in a higher-quality unit that
    is also more maintainable.

    `Wikipedia <https://en.wikipedia.org/wiki/Unit_testing>`_


En el caso de corral, se ofrece un sub-framework en el cual se propone
probar por separado en uno o mas test, el loader, cada step y cada alert.

Por ejemplo si quisieramos probar si el **subject**
``StatisticsCreator`` crea una nueva instancia de una ``Statistics`` para
cada da instancia de ``Name``

.. note::

    Llamamos **subject** a todo step, loader o alert el cual va a ser sujeto a
    una prueba.


.. code-block:: python
    :linenos:

    from corral import qa

    from . import models, steps

    class StatisticsCreateAnyNameTest(qa.TestCase):

        subject = steps.StatisticsCreator

        def setup(self):
            name = models.Name(name="foo")
            self.save(name)

        def validate(self):
            self.assertStreamHas(
                models.Name, models.Name.name=="foo")
            self.assertStreamCount(1, models.Name)

            name = self.session.query(models.Name).first()

            self.assertStreamHas(
                models.Statistics, models.Statistics.name_id==name.id)
            self.assertStreamCount(1, models.Statistics)


Desglozando el código tenemos:

-   En la lines **5** declaramos el caso de testeo poniendole un nombre
    descriptivo y heredando de la clase ``corral.qa.TestCase``.
-   En la **7**, enlazamos que subject queremos evaluar.
-   Entre las lineas **9** y **11** (metodo ``setup()``), preparamos agregamos al
    stream de datos una instancia de ``Name`` con cualquier nombre, ya que
    sabemos por la definicion del steps ``StatisticsCreator`` que este modelo
    sera seleccionado para crear una estadistica.
-   En el metodo ``validate()`` (linea **13** en adelante) se evalua en que
    estado quedo el el **stream** luego de ejecutar ``StatisticsCreator``:

    -   En primer lugar en las **14** y **15**, se verifica que efectivamente
        exista una en el stream una instancia de ``Name`` con el nombre "foo".
    -   En **16** se evalua que solo exista una instancia de ``Name`` en el
        Stream (recordemos que cada unittest se ejecuta aislado de los demas,
        por lo cual lo que hayamos agregado en ``setup()`` o
        lo que cree el **subject**, es todo lo que deberia haber en el stream)
    -   Luego, en la linea **18** extraemos esta unica instancia
        de ``Name`` del Stream
    -   Finalmente en las lineas **20** a la **22**, verificamos que
        ``StatisticsCreator`` haya creado una instancia de ``Statistics``
        enlazada a la instancia de ``Name`` recuperada, y que no haya mas
        de una instancia en el Stream.

Este ejemplo de testeo verifica el correcto funcionamiento de una step simple.
Tenga en cuenta que puede creear mas Test con el subject variando el
``setup()`` y por consiguiente logrando diferentes estados de inicio en el
*subject* generalizando todos los estados posibles.

.. important::

    Tenga en cuenta que un test **no solamente** verifica el correcto
    funcionamiento de su código. En muchos casos es interesante evaluar
    si su algoritmo falla como es devido.

    **Por ejemplo** si usted crea un Step que convierta imagenes
    cree varios tests teniendo en cuenta los tipos de imagenes mas comunes, como
    puede ser una imagen bien formada, un stream de bytes vacio o una imagen que
    no entra en memoria.


Mocks
^^^^^

Muchas veces nos vemos en la obligación de utilizar ciertas funcionalidades de
Python (o de alguna biblioteca de terceros) que exede al scope del subject
que queremos probar, o utilizarlo implicaria algun tipo de penalización

Por ejemplo si tenemos definida alguna variable en ``settings.py`` llamada
``DATA_PATH`` que indica donde guardar algun archivo procesado por el pipeline,
y nuestro subject crea datos en ese path. Si utilizaramos esto sin cuidado
nuestros casos de testeo ensuciarian de archivos basura nuestro directorio de
trabajo.

Para ayudarnos en estos casos existen los
`Mock Objects <https://en.wikipedia.org/wiki/Mock_object>`_, los cuales
ya vienen integrados en los TestCases de Corral; y cuya mayor ventaja es
que luego de salir del test case donde fueron creados no dejan rastros de
su utilización.



.. code-block:: python

    import tempfile
    import shutil

    class SomeTest(qa.TestCase):

        subject = # some subject

        def setup(self):

            # creamos un directorio temporal
            self.data_path = tempfile.tempdir()

            # cambiamos el settings.DATA_PATH por el directorio temporal
            self.patch("corral.conf.settings.DATA_PATH", self.data_path)

        def validate(self):
            # aqui adentro todo lo que suceda y utilice DATA_PATH
            # utilizara el mock

        def teardown(self):
            # aqui adentro todo lo que suceda y utilice DATA_PATH
            # utilizara el mock

            # eliminamos el directorio temporal para no dejar basura en
            # el disco
            shutil.rmtree(self.data_path)


El metodo ``teardown()`` no necesita encargarse de restaurar ``DATA_PATH`` a
su valor original, solamente se usa (en este caso) para liberar espacio
en disco que solo se utiliza durante el test.

.. note::

    Los mocks de corral implementan gran parte de la funcionalidad de los mocks
    de python, principalmente:

    -   ``patch``
    -   ``patch.object``
    -   ``patch.dict``
    -   ``patch.multiple``

    Para mas información sobre como utilizar los mocks por favor dirijase a
    https://docs.python.org/3/library/unittest.mock.html


Corral  Unit-Test Life cycle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Cada unit test se ejecuta de manera aislada, para garantizar esto corral
ejecuta los siguientes pasos para **CADA** caso de prueba.

1.  Se recolectan todos los clases que heredan de ``corral.qa.TestCase`` en el
    modulo ``tests.py``
2.  Para cada *TestCase* se ejecuta:

        #.  Se crea una base de datos de testeo para contener el Stream.
        #.  Se crean todas los modelos en el Stream.
        #.  Se crea una ``session`` para interactuar con la DB y se la asigna al
            caso de testeo.
        #.  Se ejecuta el metodo ``setup()`` del caso de testeo.
        #.  Se confirman los cambios en la base de datos y se cierra la session.
        #.  Se ejecuta el ``subject`` con su propia ``session``.
        #.  Se crea una nueva ``session`` y se la asigna al caso de testeo.
        #.  Se ejecuta el metodo ``validate()`` y se cierra la ``session``.
        #.  Se crea una nueva ``session`` y se la asigna al caso de testeo.
        #.  Se ejecuta el metodo ``teardown()`` del caso de testeo (Este método es
            opcional y puede usarse por ejemplo para eliminar archivos creados
            sin sentido)
        #.  Se destruye la base de datos y se eliminan todos los mocks que puedan
            haberse creado.

3.  Se recupera los resultados de todos los tests ejecutados.

.. important::

    El hecho de que se creen **4** ``session`` distintas para interatuar con las bases
    de datos, garantiza que toda la comunicacón dentro del caso de testeo se haga
    justamente a traves del stream y no a travez de algun objeto mantenido en
    memoria por Python.

.. note::

    La base de datos de testeo es po por defecto es un SQLite_ en memoria
    (``"sqlite:///:memory:"``),  pero puede configurarse en la variable.
    ``TEST_CONNECTION`` en el módulo ``settings.py``


Code-Coverage
-------------


Code Style
----------


Reporting
---------
