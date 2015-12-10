Quick install guide
===================

Before you can use Corral, you’ll need to get it installed. We have a complete
installation guide that covers all the possibilities; this guide will guide
you to a simple, minimal installation that’ll work while you walk through the
introduction.


Install Python
--------------

Being a Python framework, Corral requires Python.
Python includes a lightweight database called SQLite_ so you won't need to
set up a database just yet.

Get the latest version of Python at https://www.python.org/download/ or with
your operating system's package manager.


You can verify that Python is installed by typing ``python`` from your shell;
you should see something like::

    Python 3.4.x
    [GCC 4.x] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>>


Get your database running
-------------------------

If you plan to use Corral's database API functionality, you'll need to make
sure a database server is running. Corral supports all the database
servers provided by SQLAlchemy_

If you are developing a simple project or something you don't plan to deploy
in a production environment, SQLite_ is generally the simplest option as it
doesn't require running a separate server. However, SQLite has many differences
from other databases, so if you are working on something substantial, it's
recommended to develop with the same database as you plan on using in
production.

In addition to a database backend, you'll need to make sure your SqlAlchemy
database bindings_ are installed.

.. _removing-old-versions-of-corral:

Remove any old versions of Corral
---------------------------------

If you are upgrading your installation of Corral from a previous version,
you will need to uninstall the old Corral version before installing the
new version.

If you installed Corral using pip_ or ``easy_install`` previously, installing
with pip_ or ``easy_install`` again will automatically take care of the old
version, so you don't need to do it yourself.

If you previously installed Corral using ``python setup.py install``,
uninstalling is as simple as deleting the ``corral`` directory from your Python
``site-packages``. To find the directory you need to remove, you can run the
following at your shell prompt (not the interactive Python prompt):

.. code-block:: console

    $ python -c "import corral; print(corral.__path__)"


Install Corral
--------------

Installation instructions are slightly different depending on whether you're
installing a distribution-specific package, downloading the latest official
release, or fetching the latest development version.

It's easy, no matter which way you choose.


Installing an official release with ``pip``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the recommended way to install Corral.

1. Install pip_. The easiest is to use the `standalone pip installer`_. If your
   distribution already has ``pip`` installed, you might need to update it if
   it's outdated. If it's outdated, you'll know because installation won't
   work. If you're using an old version of setuptools, you might see some
   **harmless SyntaxErrors** also.

2. Take a look at virtualenv_ and virtualenvwrapper_. These tools provide
   isolated Python environments, which are more practical than installing
   packages systemwide. They also allow installing packages without
   administrator privileges.

3. After you've created and activated a virtual environment, enter the command
   ``pip install corral`` at the shell prompt.


Installing the development version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you'd like to be able to update your corral code occasionally with the
latest bug fixes and improvements, follow these instructions:

1. Make sure that you have Git_ installed and that you can run its commands
   from a shell. (Enter ``git help`` at a shell prompt to test this.)

2. Check out Corral's main development branch like so:

   .. code-block:: console

        $ git clone git@github.com:toros-astro/corral.git

   This will create a directory ``corral`` in your current directory.

3. Make sure that the Python interpreter can load Corral's code. The most
   convenient way to do this is to use virtualenv_, virtualenvwrapper_, and
   pip_.

4. After setting up and activating the virtualenv, run the following command:

   .. code-block:: console

        $ pip install -e corral/

   This will make Corral's code importable, and will also make the
   ``corral`` utility command available. In other words, you're all
   set!

When you want to update your copy of the Corral source code, just run the
command ``git pull`` from within the ``corral`` directory. When you do this,
Git will automatically download any changes.
