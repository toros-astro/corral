Integrate Corral to Another Projects
====================================

This chapter contains how do you configure Corral to make it run
cleanly whit another projects/frameworks

Lets asume we are trying to integrate a pipeline called *my_pipeline*


Django
------

First for isolate every view inside a SqlAlchemy transaction add to your
middleware list ``corral.lib.django_integration.CorralSessionMiddleware``


Finally edit your ``settings.py`` file and add to the end of the code.

.. code-block:: python

	os.environ.setdefault("CORRAL_SETTINGS_MODULE", "my_pipeline.settings")

	from corral import core
	core.setup_environment()

Now you can use all the functionaly of corral from python
and access a SQLALchemy_ session from every request.

Example

.. code-block:: python

    from my_pypeline.Models import MyModel

    def django_view(request):
        session = request.corral_session
        session.query(MyModel).filter(MyModel.attr=="Foo")
        ...


Also if you want to exclude a view from the Corral scope you can
add the decorator ``no_corral`

Example

.. code-block:: python

    from corral.lib.django_integration import no_corral

    @no_corral
    def django_view(request):
        ...


