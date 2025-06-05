Journal Flattening
==================

After exporting your journal data from Xero, you may want to convert it to CSV format for easier analysis in spreadsheet applications or databases.

Converting Journals to CSV
--------------------------

The ``flatten`` command converts hierarchical journal data into a flat, row-based CSV format:

.. code-block:: bash

    xerotrust flatten [OPTIONS] PATHS...

where ``PATHS`` are the paths to your journal export files.

How It Works
^^^^^^^^^^^^

The flattening process:

1. Reads the JSONL journal files from your exports
2. Flattens the hierarchical journal structure into row-based format
3. Outputs CSV data (to stdout by default, or to a file with ``--output``)

Each journal line becomes a separate row in the CSV, combined with data from its parent journal entry.

Examples
--------

Flatten journal files to stdout:

.. code-block:: bash

    xerotrust flatten ~/xero-backups/*/journals-*.jsonl

Save to a specific CSV file:

.. code-block:: bash

    xerotrust flatten ~/xero-backups/*/journals-*.jsonl --output all-journals.csv

Using the CSV Data
------------------

The resulting CSV format makes it easier to:

* Analyze journal data in Excel or Google Sheets
* Import into databases for reporting
* Process with data analysis tools like Python pandas
* Create custom reports and visualizations

The CSV includes all journal and journal line fields, providing a complete view of your accounting transactions in a format that's easy to work with outside of Xero.