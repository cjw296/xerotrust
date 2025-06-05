Development
===========

If you wish to contribute to this project, then you should fork the repository found here:

https://github.com/cjw296/xerotrust.git

Once that has been done and you have a checkout, you can follow these instructions to perform
various development tasks:

Code Style and Commands
-----------------------

Please refer to the ``CLAUDE.md`` file in the repository root for detailed information about:

* Code style guidelines
* Development commands (build, test, type check, format)
* Testing requirements and conventions
* Git commit message format

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
