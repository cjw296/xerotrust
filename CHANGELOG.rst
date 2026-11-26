Changes
=======

1.2.0 (26 Nov 2026)
-------------------

- ``Invoices``, ``CreditNotes`` and ``ManualJournals`` are now exported using pagination, so their
  ``LineItems`` and ``JournalLines`` are included. These endpoints are fetched in full even with
  ``--update``, and exports made with older versions should be re-exported to replace their
  summary-only data. See :doc:`export` for details.

- Fixed a bug where a full export aborted with a 404 because Xero has removed the Accounting API's
  ``Employees`` endpoint. It is no longer exported.

- Fixed a bug where ``export --update`` raised a ``KeyError`` when ``latest.json`` was saved before
  Xero started returning a date field, such as ``CreatedDateUTC`` on accounts.

- Fixed compatibility with click 8.4, which is now the minimum supported version.

Thanks to jakemike1 for the paginated exports.

1.1.0 (2025-07-08)
------------------

- Added export support for most endpoints, with exclusions explained.
- Improved error handling with better context when exceptions occur during export.
- Added an AI-friendly version of Xero's API documentation in ``api-docs/`` directory.
- Added rate limiting to all simple endpoints.

1.0.0 (2025-06-27)
------------------

First stable release.

- Added ``reconcile`` command to compare and validate data consistency between sources.
- Added bank transactions export functionality.
- Re-worked ``journals check`` into a more generate ``check`` command.
- Added pagination support to ``explore`` through ``--page` and ``--page-size`` options.
- Cross-platform documentation with Linux, macOS and Windows PowerShell examples.
- Improved handling of duplicate bank transaction updates.
- Better rate limiting and pagination handling.
- Switched to decimal handling for JSON floats.
- Fixed typos in ``expired_at``/``expires_as`` naming.
- Removed flatten functionality entirely; it's not possible to do sensibly and generically.

0.2.0 (2025-05-17)
------------------

Initial functionality:

- Implemented ``login``, ``explore``, ``export`` and ``tenants`` commands.
- Implemented ``journals`` command with ``flatten`` and ``check`` sub-commands.

0.1.0 (2025-04-10)
------------------

Placeholder release with functional continuous integration.
