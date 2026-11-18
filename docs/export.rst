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


Rate limits and safe retries
----------------------------

``export`` retries short rate limits using Xero's ``Retry-After`` delay. Set
``--rate-limit-max-wait`` (seconds, default 120) and ``--rate-limit-max-attempts``
(total attempts per API request, default 5) to adjust this policy. The wait must
be nonnegative and the attempt count positive. Python callers can pass a
``RateLimitPolicy`` to an exporter's ``rate_limit`` parameter.

A daily-limit response, a wait above the configured maximum, or exhaustion of
the configured attempts stops the export with exit code **75**. The attempt
limit also bounds repeated minute or application-minute limits while daily
capacity remains available, for example when another worker keeps consuming
the shared minute budget. Each successful API request resets the attempt count
for the next request. Missing or malformed ``Retry-After`` headers remain errors;
they are not classified as a normal quota deferral.

A scheduler should wait at least the delay reported in the error before retrying.
Short waits are never shortened to fit the configured maximum: longer waits are
deferred instead. See `Xero's rate-limit guidance
<https://developer.xero.com/documentation/best-practices/api-call-efficiencies/rate-limits/>`_.

All tenant data and checkpoints are staged privately inside the destination until
every requested API export succeeds. A quota or API failure discards these staged
writes and leaves the previous exported files and checkpoints unchanged. Rerun
the same command after the quota resets, including ``--update`` when originally
used: interrupted pages will not be appended twice. Successful incremental writes
retain the existing data; unrelated files are preserved. This does not repair
duplicates left by earlier versions or provide a point-in-time view of Xero.

Publication replaces individual files and writes checkpoints last. Caught
publication failures roll back changed files; if rollback itself fails, the error
identifies a private directory containing recovery copies. Allow only one exporter
to write to a destination at a time. This is not a crash-atomic transaction across
files: after power loss or a forced kill during publication, inspect the retained
``.xerotrust-*`` staging/recovery directory before rerunning.
