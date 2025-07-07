Development
===========

If you wish to contribute to this project, then you should fork the repository found here:

https://github.com/cjw296/xerotrust

Once that has been done and you have a checkout,
you can follow the instructions below to perform various development tasks.

For detailed development guidelines, code style requirements, and additional commands,
see ``AGENTS.md`` in the repository root.

Setting up a development environment
------------------------------------

.. code-block:: bash

   uv sync --all-groups

Running from a development environment
--------------------------------------

The command line interface can be used from a development environment as follows:

.. code-block:: bash

   uv run xerotrust --help

Running the tests
-----------------

.. code-block:: bash

   uv run -m pytest

Type check the code
-------------------

.. code-block:: bash

   uv run mypy src tests

Building the documentation
--------------------------
The Sphinx documentation is built by doing the following from the directory containing setup.py:

.. code-block:: bash

   cd docs
   make html

Making a release
----------------

To make a release:

- update the version in ``pyproject.toml``
- update the change log in ``CHANGELOG.rst``
- commit on the ``main`` branch and push to https://github.com/cjw296/xerotrust.

Carthorse should take care of the rest.

Xero API Documentation
----------------------

The ``api-docs/`` directory contains markdown files optimized for AI/LLM consumption
that were generated from the `Xero Developer documentation`__.

__ https://developer.xero.com/documentation/api/accounting/overview

See ``api-docs/README.md`` for details.

