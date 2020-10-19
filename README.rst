Cylang
======

A module to fully compile Python to C/C++.

Idea
----

The general idea is to use Cython in pure-python mode to compile python code.

Pure-python mode uses type annotations to optimize to transpilation from Python to C/C++.

This modules allows to keep track of the compiled modules, so that you can also
compile installed modules. The idea is to use pure-python mode during
development, gaining the aid of debuggers, LSP, fixing and hinting already
existing for Python.

Then, with only two code lines, you can compile your code to C/C++.

The outcome is something damn similar to Nim Lang, but with the ability of
using Python extensions at the C level (Nim can use Python extensions but it
stays at the Python level).

Internally, ``cylang`` is keeping a cache of compiled extensions. When it is
called, it forces their use and removes the pure Python modules.

Usage
-----

.. highlight:: python

::

  from cylang import cylang
  cylang()

The ``cylang`` function accepts all keyword arguments of ``cythonize``, plus the following:

* ``withelist``: list[str], if not empty, only these modules will be compiled
* ``blacklist``: list[str], modules that will not be compiled
* ``only_subdir``: str, if not empty, only modules in this directory and
  subdirectories will be compiled

To compile, use ``python -m mymodule --compile``
Run with ``python -m mymodule``

Example
-------
TODO

Maintainance
------------

After an upgrade, I suggest to recompile all the extensions (this can take a bit):

``python -c 'import cylang; cylang.recompile_all();'``

After removing packages, remove them from cylang:
``python -c 'import cylang; cylang.remove_unused();'``

Clean cylang cache of compiled modules if needed:
``python -c 'import cylang; cylang.clean();'``

All of these functions can also be accessed from any script that uses cylang via CLI:

* ``python -m mymodule --recompile-all``
* ``python -m mymodule --remove-unused``
* ``python -m mymodule --clean``

TODO
----
* Add a ``--freeze-embed`` option to get a standalone compiled file
