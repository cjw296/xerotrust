Data Export
===========

The ``export`` command is used to export your `Xero`__ data to local files.

__ https://www.xero.com/

What can be exported
--------------------

Export of the following types of content has been implemented:

* **Contacts** - Contact and customer details
* **Chart of accounts** - Account structure and details
* **Account transactions** - Reconciled bank account transaction records
* **Journal entries** - Accounting transactions and journal entries

If something you need is missing, it should be easy enough to add, please file
a `feature request <https://github.com/cjw296/xerotrust/issues>`_.

What can't be Exported
----------------------

* **Bank statements** - apparently for `commercial reasons`__.

  __ https://xero.uservoice.com/forums/5528-xero-api/suggestions/2884040-reconcile-via-the-api

* **Custom reports** - Xero's `reports API`__ has no support for either running custom reports
  or exporting their configuration.

  __ https://developer.xero.com/documentation/api/accounting/reports

Basic usage
-----------

**Export everything:**

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

**Update an existing export:**

This is faster when you already have an existing export.

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         xerotrust export --update

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         xerotrust export --update

File Organisation
-----------------

Exported data is saved in folders organised by tenant name.
The exported files are either `JSON`__ or `JSON Lines`__ making it easy to process with
standard tools.

__ https://www.json.org/
__ https://jsonlines.org/

For the complete file structure, see :doc:`usage`.
