Development
===========

.. highlight:: bash

This document provides guidance for developers who want to contribute to Xerotrust.

Setting Up a Development Environment
------------------------------------

Clone the Repository
^^^^^^^^^^^^^^^^^^^^

First, clone the repository from GitHub:

.. code-block:: bash

    git clone https://github.com/cjw296/xerotrust.git
    cd xerotrust

Install Dependencies
^^^^^^^^^^^^^^^^^^^^

Xerotrust uses ``uv`` for dependency management. To set up a development environment:

.. code-block:: bash

    # Install dependencies
    uv sync

    # For development, you may want to install in editable mode
    uv pip install -e .

Code Style
----------

Xerotrust follows strict code style guidelines:

* Python 3.13+ with strict type annotations
* Line length: 100 characters
* Imports: standard library first, then third-party, then local
* Naming: snake_case for functions/variables, CamelCase for classes
* Custom exceptions inherit from standard exceptions
* Comprehensive error handling with context
* Automated formatting with ruff

Type Checking
^^^^^^^^^^^^^

Xerotrust uses MyPy for static type checking with strict settings:

.. code-block:: bash

    uv run mypy src tests

The project requires complete type annotations for all functions and methods.

Running Tests
-------------

Xerotrust uses pytest for testing:

.. code-block:: bash

    # Run all tests
    uv run -m pytest

    # Run a specific test
    uv run -m pytest tests/test_file.py::TestClass::test_method -v

    # Run tests with coverage
    uv run -m pytest --cov

    # Generate a coverage report
    uv run coverage report --show-missing --skip-covered --fail-under 100

Testing Guidelines
^^^^^^^^^^^^^^^^^^

1. Maintain 100% test coverage for all code
2. Use testfixtures.compare for assertions instead of assert:

   .. code-block:: python

       from testfixtures import compare
       
       # Good
       compare(actual, expected=expected)
       
       # Not recommended
       assert actual == expected

3. Use fixtures for test setup
4. Test both success and error cases
5. Mock external services (like Xero API) during tests

Building Documentation
----------------------

Documentation is built using Sphinx with the Furo theme:

.. code-block:: bash

    cd docs
    make html

After building, the documentation will be available in ``_build/html/``.

Project Structure
-----------------

Xerotrust follows a standard Python package structure:

.. code-block:: text

    xerotrust/
    ├── docs/              # Documentation
    ├── src/               # Source code
    │   └── xerotrust/     # Main package
    │       ├── __init__.py
    │       ├── authentication.py
    │       ├── check.py
    │       ├── exceptions.py
    │       ├── export.py
    │       ├── main.py
    │       ├── py.typed   # Marker for typing support
    │       ├── templates/ # HTML templates
    │       └── transform.py
    └── tests/             # Test suite
        ├── __init__.py
        ├── conftest.py
        ├── helpers.py
        └── test_*.py      # Test modules

Dependency Management
---------------------

Xerotrust uses the following dependency management:

1. Runtime dependencies are defined in ``pyproject.toml``
2. Development dependencies are defined in the ``dev`` dependency group
3. Documentation dependencies are defined in the ``docs`` dependency group
4. Dependencies are locked using ``uv.lock``

Release Process
---------------

To make a release:

1. Update version information
2. Update the changelog
3. Run all tests and ensure they pass
4. Build and check documentation
5. Create a new git tag
6. Push to GitHub

Contributing Guidelines
-----------------------

When contributing to Xerotrust:

1. Create a feature branch for your changes
2. Ensure all tests pass and coverage is maintained
3. Add tests for new functionality
4. Update documentation as needed
5. Format code with ruff
6. Submit a pull request

Troubleshooting
---------------

Common development issues:

1. **Type checking errors**: Ensure all functions have proper type annotations

2. **Import errors**: Check that you've installed the package in development mode

3. **Test failures**: Make sure all dependencies are installed and up-to-date

4. **Documentation build issues**: Verify that Sphinx and all documentation dependencies are installed
