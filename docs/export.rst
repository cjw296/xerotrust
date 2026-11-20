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

``export`` waits for Xero's full ``Retry-After`` delay before retrying a short
rate limit. ``--rate-limit-max-wait`` sets the longest individual delay this
process will wait for, in seconds (default 120, minimum 0). Python callers can
pass ``max_wait=120`` to ``exporter.items(...)``. There is no attempt-count limit:
repeated short limits continue to wait and retry while daily capacity remains.

For example, with ``--rate-limit-max-wait 120``, a ``Retry-After`` of 60 seconds
waits 60 seconds and retries. A ``Retry-After`` of 300 seconds stops immediately
with exit code **75**; it does not sleep for 120 seconds and retry early. A daily
limit also stops immediately with exit code 75. A scheduler should wait at least
the delay reported in the error before retrying. Missing or malformed
``Retry-After`` headers remain ordinary errors. See `Xero's rate-limit guidance
<https://developer.xero.com/documentation/best-practices/api-call-efficiencies/rate-limits/>`_.

Each endpoint is downloaded into a private directory under the system temporary
directory. When that endpoint completes, its data and checkpoint are published
before starting the next endpoint. If a quota or API request fails, the failed
endpoint's existing data and checkpoint are unchanged. Earlier completed endpoints
and tenants stay published. Rerun the same command after the quota resets, including
``--update`` when originally used: completed incremental endpoints resume from
their saved checkpoints, and the interrupted endpoint repeats its uncommitted
pages without appending them twice. Successful fresh exports replace the requested
endpoint's files; unrelated files and endpoint checkpoints are preserved. This
does not repair duplicates left by earlier versions or provide a point-in-time
view of Xero.

Failed output is retained for **every failure**, and its directory is printed to
standard error. It contains the downloaded rows, including the original rows in
staged incremental files. Successful staging directories are removed. Retained
directories have owner-only access and follow the operating system's temporary-file
cleanup policy; move them elsewhere if needed for longer-term investigation.

Publication copies each staged file through a temporary file beside its destination,
then atomically replaces that one destination file. The checkpoint is replaced last.
The complete endpoint is **not** a transaction across files: a filesystem error,
power loss, or forced termination during publication may leave some files replaced
and the old checkpoint in place. In that case, inspect the retained directory and
recover the complete endpoint and its checkpoint (or restore an earlier backup)
before rerunning an incremental export. All staged originals remain available even
if their destination files were already replaced. Allow only one exporter to write
to a destination at a time.
