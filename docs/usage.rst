Usage
=====

Xerotrust provides a command-line interface (CLI) for interacting with the Xero API. 
This document covers the basic usage of the CLI and its commands.

Installation
------------

You can install xerotrust using pip:

.. code-block:: bash

    pip install xerotrust

After installation, the ``xerotrust`` command will be available in your terminal.

Command Line Interface
----------------------

Xerotrust provides a comprehensive CLI for interacting with Xero data. For detailed information about all available commands, options, and arguments, run:

.. code-block:: bash

    xerotrust --help

For help with a specific command, use:

.. code-block:: bash

    xerotrust COMMAND --help

Common Commands
^^^^^^^^^^^^^^^

* ``xerotrust login`` - Authenticate with Xero
* ``xerotrust tenants`` - List available tenants
* ``xerotrust explore ENDPOINT`` - Explore data from specific endpoints
* ``xerotrust export`` - Export data to files
* ``xerotrust flatten`` - Convert journal data to CSV format
* ``xerotrust journals check`` - Validate journal data integrity

For detailed information about specific functionality, see the corresponding sections in this documentation.

Key Concepts
------------

Authentication
^^^^^^^^^^^^^^

Xerotrust uses OAuth 2.0 with PKCE for secure authentication. See :doc:`authentication` for detailed setup instructions.

Data Export
^^^^^^^^^^^

Export functionality allows you to backup and analyze your Xero data locally. See :doc:`export` for comprehensive export options.

Journal Management
^^^^^^^^^^^^^^^^^^

Xerotrust provides tools for validating and processing journal data. See :doc:`checks` for validation details.

Output Transformation
^^^^^^^^^^^^^^^^^^^^^

Most commands support flexible output formatting. Use the ``--help`` option with any command to see available transformation options.

Quick Start Examples
--------------------

.. code-block:: bash

    # Authenticate with Xero
    xerotrust login

    # Export all data
    xerotrust export

    # Explore specific endpoints
    xerotrust explore Contacts

    # Validate journal integrity
    xerotrust journals check */journals-*.jsonl

For more detailed examples and options, see the specific documentation sections and use ``xerotrust COMMAND --help``.