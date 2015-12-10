The command line interface
==========================

The Corral library gives you the power to manage a chain of processes, or
pipeline, that relies on a database by delivering command line commands.

This works for example for creating a databased::

    $python in_corral.py createdb
    $python in_corral.py sqlitebrowser

And if you have the sqlitebrowser program installed you should be able to open
in a window a database manager and search into the contents of your data
structures.

Another feature of corral is the ability to execute a shell environment where
you have the most important imports already done, giving you even a ``session``
instance from sqlalchemy working and ready to receive queries and to commit
entries.

This can be done by simply typing ``python in_corral.py shell`` in your
terminal, and it will simply give you a IPython shell, or if you don't have
IPython a bPython -in case you also lack of a bPython interpreter a plain
python prompt is what you get-.

Even more Corral can give you a IPython Notebook by running

.. code-block:: console

    $ python in_corral.py notebook


Other useful utility is the ``exec`` command available, which can give a
script for input to the Corral environment, just as if you were importing the
script on a shell. I works by running:


.. code-block:: console

    $ python in_corral.py exec your_script.py

