Journal Checks
==============

Xerotrust provides functionality to validate the integrity of exported journal data, ensuring its completeness and consistency.

Overview
--------

Journal entries in accounting systems like Xero should follow certain rules:

1. Each journal entry should have a unique ID
2. Journal numbers should be unique
3. Journal numbers should form a continuous sequence without gaps

Xerotrust provides a command to verify these properties in exported journal data.

Check Command
-------------

To check journal exports for integrity:

.. code-block:: bash

    xerotrust journals check [OPTIONS] PATHS...

Arguments:

* ``PATHS`` - One or more paths to journal export files (supports globbing)

Example:

.. code-block:: bash

    xerotrust journals check ~/xero-exports/*/journals-*.jsonl

This will:

1. Read all specified journal files
2. Display a summary of the journals (count, date ranges, number ranges)
3. Check for validation issues
4. Raise an exception if any issues are found

Validation Rules
----------------

The ``check_journals`` function verifies the following:

1. **No Duplicate IDs**: Each journal must have a unique ``JournalID``
2. **No Duplicate Numbers**: Each journal must have a unique ``JournalNumber``
3. **No Number Gaps**: Journal numbers must form a continuous sequence

If any of these rules are violated, an ``ExceptionGroup`` is raised containing all validation errors.

Summary Information
-------------------

Before validation, a summary of the journals is displayed:

.. code-block:: text

    entries: 120
    JournalNumber: 1 -> 120
    JournalDate: 2025-01-01 -> 2025-03-31
    CreatedDateUTC: 2025-01-01T00:00:00Z -> 2025-03-31T23:59:59Z

This provides a quick overview of:

* Total number of journal entries
* Range of journal numbers
* Date range covered by the journals
* Creation date range

Error Handling
--------------

When validation errors are found, they are:

1. Collected into a list
2. Sorted for consistent ordering
3. Raised as an ``ExceptionGroup``

Example error output:

.. code-block:: text

    journal validation errors:
      * ValueError: Duplicate JournalID found: 123
      * ValueError: Duplicate JournalNumber found: 45
      * ValueError: Missing JournalNumbers: 50-55, 60

For missing journal numbers, a compact representation is used to show the gaps in the sequence.

Compact Range Representation
----------------------------

The ``minimal_repr`` function creates a compact string representation of number sequences:

* Single numbers are shown as-is: ``1``
* Consecutive ranges are collapsed: ``1-5``
* Multiple ranges are comma-separated: ``1-5, 7, 10-12``

This format makes it easier to identify gaps in the journal number sequence.

Example:

.. code-block:: python

    minimal_repr([1, 2, 4, 5, 7])  # Returns "1-2, 4-5, 7"

Handling Special Cases
----------------------

The journal check functionality includes special handling for:

* ``None`` values for journal IDs or numbers
* Non-integer journal numbers
* Empty journal collections

These special cases are handled robustly to prevent errors during validation:

1. ``None`` values are excluded from duplicate checks
2. Only integer journal numbers are checked for sequence gaps
3. Empty collections are validated without errors

Usage in Data Pipelines
-----------------------

The journal check functionality can be integrated into data pipelines:

.. code-block:: python

    from xerotrust.check import check_journals
    
    # Read journals from files
    journals = read_journals_from_files(paths)
    
    try:
        # Validate the journals
        check_journals(journals)
        print("Journal validation successful")
    except ExceptionGroup as e:
        print("Journal validation failed:")
        for error in e.exceptions:
            print(f"- {error}")

This allows for programmatic handling of validation results in larger workflows.