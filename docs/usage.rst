Usage
=====

The best place to start is the :any:`quickstart`.

Available Commands
------------------

``xerotrust`` provides several commands to interact with your Xero data:

* ``xerotrust login`` - Authenticate with Xero
* ``xerotrust tenants`` - List available tenants
* ``xerotrust explore {ENDPOINT}`` - Explore data from specific endpoints
* ``xerotrust export`` - Export data to files
* ``xerotrust reconcile`` - Compare and validate data consistency between sources
* ``xerotrust check {ENDPOINT}`` - Validate data exported from an endpoint

For help with any command, use:

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         xerotrust {COMMAND} --help

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         xerotrust {COMMAND} --help

Export File Structure
----------------------

When you export data, xerotrust creates this folder structure:

.. code-block:: text

    export-folder/
    ├── Tenant Name 1/
    │   ├── tenant.json              # Tenant metadata
    │   ├── latest.json              # Export tracking information
    │   ├── accounts.jsonl           # Chart of accounts
    │   ├── contacts.jsonl           # Contacts and customers
    │   ├── journals-....jsonl       # Journal entries split by journal date
    │   └── transactions-....jsonl   # Bank transactions split by transaction date
    └── Tenant Name 2/
        ├── tenant.json
        ├── latest.json
        └── ...

Basic Usage Examples
---------------------

**Export all data:**

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         xerotrust export

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         xerotrust export

**Export specific data types:**

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         xerotrust export contacts journals

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         xerotrust export contacts journals

**Update existing export:**

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         xerotrust export --update

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         xerotrust export --update

**Validate your exported data:**

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         xerotrust check journals */journals-*.jsonl
         xerotrust check transactions */transactions-*.jsonl

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         xerotrust check journals *\journals-*.jsonl
         xerotrust check transactions *\transactions-*.jsonl

**Reconcile journals with bank transactions:**

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         xerotrust reconcile journals=*/journals-*.jsonl transactions=*/transactions-*.jsonl

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         xerotrust reconcile journals=*\journals-*.jsonl transactions=*\transactions-*.jsonl
