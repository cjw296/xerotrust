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

Global Options
--------------

The following options can be used with any command:

.. code-block:: bash

    xerotrust [OPTIONS] COMMAND [ARGS]...

Options:

* ``--auth PATH`` - Path to the authentication file (default: ``.xerotrust.json``)
* ``-l, --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]`` - Set the logging level

Authentication
--------------

Before using the CLI, you need to authenticate with Xero:

.. code-block:: bash

    xerotrust login [--client-id CLIENT_ID]

This will:

1. Prompt for your client ID if not provided
2. Initiate the OAuth2 authentication flow
3. Open your browser to authenticate with Xero
4. Save the authentication tokens locally

After successful authentication, the available Xero tenants will be displayed.

Viewing Tenants
---------------

To list the tenants your account has access to:

.. code-block:: bash

    xerotrust tenants [OPTIONS]

Options:

* ``-t, --transform TEXT`` - Apply a transformation to the output
* ``-f, --field TEXT`` - Select specific fields to display
* ``-n, --newline`` - Add a newline between rows

Exploring Xero Data
-------------------

The explore command allows you to examine data from specific Xero API endpoints:

.. code-block:: bash

    xerotrust explore [OPTIONS] ENDPOINT

where ``ENDPOINT`` is one of the Xero API endpoints (e.g., Accounts, Contacts, Invoices, etc.)

Options:

* ``--tenant TEXT`` - Tenant ID (uses first tenant if not specified)
* ``-i, --id TEXT`` - Return a specific entity by ID
* ``-t, --transform TEXT`` - Apply a transformation to the output
* ``-f, --field TEXT`` - Select specific fields to display
* ``-n, --newline`` - Add a newline between rows
* ``--since DATETIME`` - Filter by date/time
* ``--offset INTEGER`` - Start from a specific offset

Exporting Data
--------------

To export data from Xero:

.. code-block:: bash

    xerotrust export [OPTIONS] [ENDPOINTS]...

where ``ENDPOINTS`` is one or more of: Accounts, Contacts, Journals (defaults to all if none specified)

Options:

* ``-t, --tenant TEXT`` - Tenant ID(s) to export (defaults to all tenants)
* ``--path DIRECTORY`` - Directory to export data to (default: current directory)
* ``--update`` - Update existing exports instead of starting from scratch
* ``--split [none|years|months|days]`` - Split journal exports by time period (default: months)

For more detailed information about export options, see the :doc:`export` documentation.

Journal Management
-------------------

Checking Journal Integrity
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To check journal exports for integrity:

.. code-block:: bash

    xerotrust journals check [OPTIONS] PATHS...

where ``PATHS`` are the paths to journal export files.

This command verifies that:
- Journal IDs are unique
- Journal numbers are unique
- There are no gaps in journal number sequences

For more details on journal checking, see the :doc:`checks` documentation.

Flattening Journal Exports
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To convert journal exports to CSV format for easier analysis:

.. code-block:: bash

    xerotrust journals flatten [OPTIONS] PATHS...

where ``PATHS`` are the paths to journal export files.

This command:
1. Reads the JSONL journal files
2. Flattens the hierarchical journal structure into row-based format
3. Outputs CSV files with the same name but .csv extension

The CSV format makes it easier to analyze the data in spreadsheet applications or load it into databases.

Transformation Options
----------------------

Many commands support the following transformation options:

* ``-t, --transform TEXT`` - Apply a transformation to the output (json, yaml, table, etc.)
* ``-f, --field TEXT`` - Select specific fields to display
* ``-n, --newline`` - Add a newline between row transforms instead of a space

Examples
--------

1. Authenticate with Xero:

   .. code-block:: bash

       xerotrust login

2. List all contacts in JSON format:

   .. code-block:: bash

       xerotrust explore Contacts -t json

3. Export all journal entries to the current directory:

   .. code-block:: bash

       xerotrust export Journals

4. Update an existing export with new data:

   .. code-block:: bash

       xerotrust export --update

5. Export journals split by day:

   .. code-block:: bash

       xerotrust export Journals --split days

6. Check journal files for inconsistencies:

   .. code-block:: bash

       xerotrust journals check ~/exports/*/journals-*.jsonl

7. Convert journal exports to CSV format:

   .. code-block:: bash

       xerotrust journals flatten ~/exports/*/journals-*.jsonl