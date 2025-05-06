Data Checks
===========

The ``check`` command is provided to validate exported data while the
``reconcile`` command is provided to ensure different sets of exported data are consistent with
each other.

Data Validation
---------------

You can check the integrity of your exported data to ensure it's complete and consistent.
If any issues are found, you'll see detailed error messages showing exactly what's wrong.

**Validate journal entries:**

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         xerotrust check journals */journals-*.jsonl

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         xerotrust check journals *\journals-*.jsonl

This checks for:

- Duplicate journal IDs
- Duplicate journal numbers  
- Missing journal numbers in sequence

**Validate bank transactions:**

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         xerotrust check transactions */transactions-*.jsonl

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         xerotrust check transactions *\transactions-*.jsonl

This checks for:

- Duplicate transaction IDs

Data Reconciliation
-------------------

Compare data between different sources to verify consistency.

**Basic reconciliation:**

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         xerotrust reconcile journals=*/journals-*.jsonl transactions=*/transactions-*.jsonl

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         xerotrust reconcile journals=*\journals-*.jsonl transactions=*\transactions-*.jsonl

This compares account totals between journal entries and bank transactions,
showing any discrepancies in a clear table format.

**Stop on first difference:**

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         xerotrust reconcile --stop-on-diff journals=*/journals-*.jsonl transactions=*/transactions-*.jsonl

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         xerotrust reconcile --stop-on-diff journals=*\journals-*.jsonl transactions=*\transactions-*.jsonl

This stops on the first date where differences are found.
It's useful for digging into differences if they do occur.

**Compare different exports:**

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         xerotrust reconcile journals=old-export/journals-*.jsonl journals=new-export/journals-*.jsonl

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         xerotrust reconcile journals=old-export\journals-*.jsonl journals=new-export\journals-*.jsonl
