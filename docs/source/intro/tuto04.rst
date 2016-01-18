Escribiendo tu primer Pipeline con Corral - Parte 4
===================================================

Steps: Procesando Datos
-----------------------

Luego de ejecutar ``python in_corral load`` ya tenemos los datos de iris_
en nuestra base de datos y ahora lo que queremos es calcular la media, minimos
y máximos de  ``sepal_length``, ``sepal_width``,
``petal_length``y ``petal_width`` en paralelo para cada especie.

.. warning::

    En todos el tutorial hemos usado como base de datos SQLite la cual
    no sporta concurrencia. Tenga en cuenta que esto es solo un ejercicio y
    en un verdadero Pipeline deberia usar alguna base de datos como
    PostgreSQL, MySQL, Oracle o incluso algo mas pontente como Hive_


Modelo para las estadísticas
----------------------------

Para almacenar las estadisticas definiremos un modelo que defina las 3 medidas
estadísticas para las 4 características de las obsrvaciones y a su ves
referencia a que especie de iris correponde (una relacion a la tabla ``Name``)

Asi que al final de ``my_pipeline/models.py`` agregaremos la clase

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

Si ya se leyeron las explicaciones en el capitulo anterior las unicas
diferencias que tiene este modelo con los anteriores, son los parametros
``unique=True`` y ``userlist=False`` en las lineas donde se definen la
relación para indicar que cada instancia de ``Name`` solo puede tener una
instancia de ``Statistics``.

Para crear la tabla ejecutamos en la linea de commandos nuevamente
``python in_corral createdb`` y solo se creara la tabla nueva sin alterar
la forma y el contenido de las anteriores.


Los Steps
---------

Crearemos  4 stapes dentro del módulo ``my_pypeline/steps.py``.


#. Step 1: Creando Statistics para cada Name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

En primer lugar en la parte de imports descomentar la linea
``# from . import models``; y luego editar la clase ``MyStep``
para que luzca como la siguiente:


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


Este step persigue el objetivo de crear una instancia de ``Statistics`` por
cada nombre diference que encuentre en la tabla ``Name``.

En primer lugar se observa que en la variable ``model`` se le informa al
*Step* que trabajara con las instancias del modelo ``Name`` sin ninguna
condicion. Corral automaticamente enviará secuencialmente las instancias
almacenadas (por el Loader) que cumplan las condiciones (Todas en nuestro caso)
método process.

``process()`` recibe por parámetro cada instancia de ``Name`` y de no existir
una instancia de ``Statistics`` asociada la crea con todos los valores en *0*
retornandola a corral (con ``yield``).

#. Step 2: Calculando Statistics para "Iris-Setosa"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Si creamos un Step llamado ``SetosaStatistics`` y as u variable model le
asigamos la clase ``Statistics`` y en ``conditions`` escribimos:

.. code-block:: python

    conditions = [
            models.Statistics.name.has(name="Iris-setosa"),
            models.Statistics.mean_sepal_length==0.]

Lo que obtendremos es un step que solo calcule las estadisticas de
**Iris-setosa** si es que no han sido calculadas
(la media de ``sepal_length`` es ``0.``)

Por otra parte el metodo ``process()`` recibiria por parametro dicha
instancia de ``Statistics`` y para llenarla el codigo completo del step
sería:

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


#. Step 3 y 4: Calculando Statistics para "Iris-Virginica" e "Iris-Versicolor"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Los ultimos dos steps son exactamente iguales al enterior execptuando las
variables ``model`` y  ``conditions``.

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


