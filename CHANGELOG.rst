Changes
=======

Next release
------------

- Add resumable Files API exports for uploaded attachments, inbox files, metadata,
  folders and document associations, with size/hash validation and explicit quota failure.

- Add opt-in fixed-asset register, asset type and settings exports, with all-status
  pagination and a completion manifest. ``login --assets`` requests read-only permission;
  token refresh preserves the scopes already granted by the user.

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
