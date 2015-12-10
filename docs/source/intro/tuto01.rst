Escribiendo tu primer Pipeline con Corral - Parte 1
===================================================

Let's learn by example.

Throughout this tutorial, we'll walk you through the creation of a basic
application pipeline.

We'll assume you have :doc:`Corral installed </intro/install>` already. You can
tell Corral is installed and which version by running the following command:

.. code-block:: console

    $ python -c "python -c "import corral; print(corral.VERSION)""

If Corral is installed, you should see the version of your installation. If it
isn't, you'll get an error telling "No module named corral".

This tutorial is written for Corral |version| and Python 3.4 or later. If the
Corral version doesn't match, you can refer to the tutorial for your version
of Corral by using the version switcher at the bottom right corner of this
page, or update Corral to the newest version. If you are still using Python
2.7, you will need to adjust the code samples slightly, as described in
comments.

See :doc:`How to install Corral </intro/install>` for advice on how to remove
older versions of Corral and install a newer one.

.. admonition:: Where to get help:

    If you're having trouble going through this tutorial, please post a message
    to |corral-users| to chat with other Corral users who might
    be able to help.


Creating a project
------------------

If this is your first time using Corral, you'll have to take care of some
initial setup. Namely, you'll need to auto-generate some code that establishes a
Corral :term:`pipeline` -- a collection of settings for an instance of Corral,
including database configuration, Corral-specific options and
pipeline-specific settings.

From the command line, ``cd`` into a directory where you'd like to store your
code, then run the following command:

.. code-block:: console

   $ corrral create pipeline

This will create a ``pipeline`` directory in your current directory.

.. note::

    You'll need to avoid naming projects after built-in Python or Corral
    components. In particular, this means you should avoid using names like
    ``corral`` (which will conflict with Django itself) or ``test`` (which
    conflicts with a built-in Python package). In most cases Corral must
    forbid the use of most commons names.


Let's look at what ``create`` created::

    in_corral.py
    pipeline/
    ├── __init__.py
    ├── alerts.py
    ├── commands.py
    ├── load.py
    ├── models.py
    ├── pipeline.py
    ├── settings.py
    └── steps.py

These files are:


