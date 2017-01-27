Integrate Corral with Django
============================

Django is...

    ... a high-level Python Web framework that encourages rapid
    development and clean, pragmatic design. Built by experienced developers,
    it takes care of much of the hassle of Web development, so you can focus
    on writing your app without needing to reinvent the wheel. It’s
    free and open source. `[Read Mode] <https://www.djangoproject.com/>`__

So this chapter will teach how to access Corral managed database from django.

----

Lets asume we are trying to integrate a pipeline called *my_pipeline*

First for isolate every view inside a SqlAlchemy transaction add to your
middleware list ``corral.libs.django_integration.CorralSessionMiddleware``


Finally edit your ``settings.py`` file and add to the end of the code.

.. code-block:: python

    os.environ.setdefault("CORRAL_SETTINGS_MODULE", "my_pipeline.settings")

    from corral import core
    core.setup_environment()

Now you can use all the functionaly of corral from python
and access a SQLALchemy_ session from every request.

Example

.. code-block:: python

    # cmodels to avoid django models name
    from my_pypeline import models as cmodels

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


