Data Export
===========

Xerotrust provides functionality to export data from your Xero account for backup, analysis, or compliance purposes.

Overview
--------

The export functionality allows you to:

* Export data from multiple Xero endpoints
* Export from one or more tenants (organizations)
* Save data in JSON format for easy processing
* Handle rate limiting automatically
* Maintain a clean file structure by tenant and data type
* Display progress during exports
* Perform incremental updates to existing exports

Export Command
--------------

To export data from Xero, use the ``export`` command:

.. code-block:: bash

    xerotrust export [OPTIONS] [ENDPOINTS]...

Arguments:

* ``ENDPOINTS`` - One or more endpoints to export from (e.g., Accounts, Contacts, Journals)
  If no endpoints are specified, all available endpoints will be exported.

Options:

* ``-t, --tenant TEXT`` - Tenant ID(s) to export (defaults to all tenants)
* ``--path DIRECTORY`` - Directory to export data to (default: current directory)
* ``--update`` - Update existing exports instead of starting from scratch
* ``--split [none|years|months|days]`` - Split journal exports by time period (default: months)

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

Journal Export Details
----------------------

Journal entries are exported with a specialized export strategy that:

1. Handles Xero's pagination requirements
2. Organizes journal entries by time period (days, months, years, or no splitting)
3. Automatically retries on rate limit errors
4. Maintains all journal metadata for verification
5. Shows progress during export

Example:

.. code-block:: bash

    xerotrust export Journals --path ~/xero-backups

This will export all journal entries from all tenants, organizing them by month.

Progress Bars
--------------

When exporting data, Xerotrust displays progress bars showing:

* The current tenant and export type being processed
* Number of items downloaded
* File size
* Network bandwidth
* Estimated time remaining

This provides visibility into the export process, especially for large exports that may take some time to complete.

Incremental Updates
--------------------

You can update an existing export instead of downloading all data again:

.. code-block:: bash

    xerotrust export --update

This option uses a ``latest.json`` file in each tenant directory to track what data has already been exported and only fetches new or updated data. With this option:

* For journals, only new journal entries will be appended to existing files
* For other data types, files will be refreshed with the latest data
* Progress is tracked through the ``latest.json`` file, which records the most recent data seen for each export type

The ``latest.json`` file contains timestamps for each export type:

.. code-block:: json

    {
      "Accounts": "2023-05-15T08:30:45Z",
      "Contacts": "2023-05-15T08:31:12Z",
      "Journals": "2023-05-15T08:35:02Z"
    }

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

Technical Implementation
------------------------

File Management
^^^^^^^^^^^^^^^

The ``FileManager`` class handles writing data to files efficiently:

- Keeps a pool of open files for performance
- Limits the number of simultaneously open files
- Ensures parent directories exist
- Handles file modes (write/append) automatically

.. code-block:: python

    with FileManager(serializer=TRANSFORMERS['json']) as files:
        files.write(data, path / filename)

Rate Limiting
^^^^^^^^^^^^^

The export system automatically handles Xero API rate limits:

- Catches ``XeroRateLimitExceeded`` exceptions
- Respects the ``retry-after`` header
- Automatically retries requests after waiting the specified period

.. code-block:: python

    def retry_on_rate_limit(manager_method, *args, **kwargs):
        while True:
            try:
                return manager_method(*args, **kwargs)
            except XeroRateLimitExceeded as e:
                seconds = int(e.response.headers['retry-after'])
                logging.warning(f'Rate limit exceeded, waiting {seconds} seconds')
                sleep(seconds)

Customizing Exports
-------------------

Each export type is defined by an ``Export`` class that specifies:

1. How to name the output files
2. How to retrieve items from the Xero API

To add a new export type, create a subclass of ``Export`` that implements:

- ``name(item)`` - Returns the filename for an item
- ``items(manager)`` - Returns an iterable of items from the API