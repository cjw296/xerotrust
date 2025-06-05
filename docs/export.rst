Data Export
===========

Xerotrust provides functionality to export data from your Xero account for backup, analysis, or compliance purposes.

Exporting Your Data
-------------------

There are two main scenarios for exporting data from Xero:

1. **Creating a fresh export** - Starting a new backup or data collection
2. **Updating an existing export** - Adding new data to previous exports

For the best experience with either scenario, create a dedicated directory for your exports and run xerotrust from within that directory:

.. code-block:: bash

    mkdir ~/xero-backups
    cd ~/xero-backups
    xerotrust export

Fresh Export
^^^^^^^^^^^^

When starting fresh, simply run the export command in an empty directory:

.. code-block:: bash

    # Export all data from all tenants
    xerotrust export
    
    # Export specific endpoints only
    xerotrust export Journals Contacts
    
    # Export from a specific tenant
    xerotrust export --tenant YOUR_TENANT_ID

This will create a clean directory structure organized by tenant name, with all your Xero data saved in JSONL format.

Updating an Existing Export
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To add new data to an existing export without re-downloading everything:

.. code-block:: bash

    cd ~/xero-backups  # Navigate to your existing export directory
    xerotrust export --update

The ``--update`` option intelligently determines what new data is available and only downloads what's changed since your last export. This is much faster for regular backups.

Supported Endpoints
-------------------

Xerotrust currently supports exporting from the following Xero endpoints:

* ``Accounts`` - Chart of accounts
* ``Contacts`` - Contacts and customers
* ``Journals`` - Journal entries

Each endpoint has a specific export strategy optimized for that data type.

Export Structure
----------------

The export creates a directory structure organized by tenant name:

.. code-block:: text

    path/
    ├── Tenant1Name/
    │   ├── tenant.json              # Tenant metadata
    │   ├── latest.json              # Export tracking information
    │   ├── accounts.jsonl           # Accounts data
    │   ├── contacts.jsonl           # Contacts data
    │   └── journals-YYYY-MM.jsonl   # Journal entries by month
    └── Tenant2Name/
    │   ├── tenant.json
    │   ├── latest.json
    │   └── ...

File Formats
------------

All exports are saved in either JSON or JSONL (JSON Lines) format:

* Single objects are saved as JSON files
* Collections are saved as JSONL files (one JSON object per line)

For journal entries, the files are organized by time period according to the ``--split`` option.


Splitting Journal Exports
--------------------------

For large journal exports, you can control how the data is split into files using the ``--split`` option:

.. code-block:: bash

    xerotrust export Journals --split days

Options include:

* ``none`` - All journals in a single file
* ``years`` - Split by year (journals-YYYY.jsonl)
* ``months`` - Split by month (journals-YYYY-MM.jsonl) - Default
* ``days`` - Split by day (journals-YYYY-MM-DD.jsonl)

The appropriate splitting option depends on the size of your Xero account and how you plan to use the data.

Journal Management
-------------------

Journal Flattening
^^^^^^^^^^^^^^^^^^^

To convert journal exports to CSV format for easier analysis:

.. code-block:: bash

    xerotrust journals flatten [OPTIONS] PATHS...

where ``PATHS`` are the paths to journal export files.

This command:

1. Reads the JSONL journal files
2. Flattens the hierarchical journal structure into row-based format
3. Outputs CSV files with the same name but .csv extension

The CSV format makes it easier to analyze the data in spreadsheet applications or load it into databases.

Working with the Exported Data
------------------------------

The exported data can be used for:

* Creating backups of your Xero data
* Performing data analysis outside of Xero
* Integrating with other systems
* Compliance and audit purposes

Journal files can be validated using the ``journals check`` command (see :doc:`checks` for details).

