Data Export
===========

The ``export`` command is used to export your `Xero`__ data to local files.

__ https://www.xero.com/

What can't be exported
----------------------

* **Bank statements** - apparently for `commercial reasons`__.

  __ https://xero.uservoice.com/forums/5528-xero-api/suggestions/2884040-reconcile-via-the-api

* **Expense Claims** - `Deprecated by Xero`__ and no longer supported.

  __ https://developer.xero.com/documentation/api/accounting/expenseclaims

* **Custom reports** - Xero's `reports API`__ has no support for either running custom reports
  or exporting their configuration.

  __ https://developer.xero.com/documentation/api/accounting/reports

* **History** and **Notes** for endpoints - `Not supported`__ by the ``pyxero`` library.

  __ https://github.com/freakboy3742/pyxero/issues/382

* **Linked Transactions** - `Not supported`__ by the ``pyxero`` library.

  __ https://github.com/freakboy3742/pyxero/issues/383

* **Receipts** - `Deprecated by Xero`__ and no longer supported.

  __ https://developer.xero.com/documentation/api/accounting/receipts

* **PaymentServices** - Requires the ``paymentservices`` OAuth scope which is only available after
  `additional Xero partner certification and commercial agreements`__.

  __  https://developer.xero.com/documentation/guides/oauth2/scopes/#organisation-scopes

Basic usage
-----------

Rate limits
~~~~~~~~~~~

``export`` retries short rate limits using Xero's ``Retry-After`` delay, with at
most five attempts per API request. It stops immediately when Xero indicates
the daily limit, requests a wait longer than 120 seconds, or supplies a missing
or invalid delay. Five consecutive rate-limit responses also stop the export.
These cases report an incomplete export and exit with code **75**. A scheduler
should defer the next run until at least the indicated delay has elapsed,
rather than immediately restarting the command. Without a valid delay, retry
later instead of using a tight retry loop.

The affected tenant's ``latest.json`` checkpoint is not saved on deferral, but
files already written by the command remain partial. Export into a fresh staging
directory and publish it only after a successful, validated run. Do not repeatedly
run ``--update`` on a partial export: incremental output may contain duplicates.

See `Xero's rate-limit guidance
<https://developer.xero.com/documentation/best-practices/api-call-efficiencies/rate-limits/>`_.

Commands
~~~~~~~~

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


What can be exported
--------------------

Export of the following types of content has been implemented:

**Core Accounting Data:**

* **Accounts** - Chart of accounts structure and details
* **Contacts** - Contact and customer details
* **Journals** - Accounting transactions and journal entries
* **BankTransactions** - Reconciled bank account transaction records
* **BankTransfers** - Bank transfer records between accounts

**Transaction Records:**

* **Invoices** - Sales invoices and bills
* **CreditNotes** - Credit notes for refunds and adjustments
* **Payments** - Payment records and receipts
* **Overpayments** - Customer overpayment records
* **Prepayments** - Supplier prepayment records
* **ManualJournals** - Manual journal entries
* **BatchPayments** - Batch payment records

**Business Operations:**

* **PurchaseOrders** - Purchase order records
* **Quotes** - Quote and estimate records
* **RepeatingInvoices** - Recurring invoice templates

**Reference Data:**

* **Currencies** - Currency definitions and exchange rates
* **TaxRates** - Tax rate configurations
* **Items** - Product and service item definitions
* **TrackingCategories** - Custom tracking category definitions

**Organization Setup:**

* **Organisations** - Organization profile and settings
* **Users** - User accounts and permissions
* **Employees** - Employee records
* **BrandingThemes** - Invoice branding themes
* **ContactGroups** - Contact grouping configurations

If something you need is missing, it should be easy enough to add, please file
a `feature request <https://github.com/cjw296/xerotrust/issues>`_.

