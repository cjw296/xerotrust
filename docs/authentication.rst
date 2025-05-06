Authentication
==============

This document goes through the technical details of how the application handles authentication.
You should not need to read this just to use the application!

See :any:`quickstart` or :any:`usage` instead.

Authentication Flow
-------------------

OAuth 2.0 with PKCE (Proof Key for Code Exchange) is used to authenticate with the Xero API.

The authentication process follows these steps:

1. User provides a Client ID (created in the Xero Developer Portal)
2. A PKCE challenge and verifier are generated,
3. A local web server is started to receive the OAuth callback
4. The user's browser is opened to the Xero authorization page
5. User logs in to Xero and authorizes the application
6. Xero redirects back to the local callback with an authorization code
7. The authorization code is exchanged for access and refresh tokens
8. The tokens are saved locally for future use

Authentication Command
----------------------

To authenticate with Xero, use the ``login`` command:

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         xerotrust login [--client-id CLIENT_ID]

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         xerotrust login [--client-id CLIENT_ID]

If you don't provide a client ID, you'll be prompted to enter one.
If you've previously authenticated, the stored client ID will be used as a default.

Required Permissions
--------------------

The following Xero API scopes are requested:

* ``offline_access`` - Enables refresh tokens for long-term access
* ``accounting.transactions.read`` - Read access to transactions
* ``accounting.contacts.read`` - Read access to contacts
* ``accounting.journals.read`` - Read access to journals
* ``accounting.settings.read`` - Read access to accounting settings
* ``files.read`` - Read access to files
* ``accounting.reports.read`` - Read access to reports
* ``accounting.attachments.read`` - Read access to attachments

These scopes provide read-only access to the data needed for exports and checks.

Token Storage
-------------

After successful authentication, the credentials are stored in a JSON file called `.xerotrust.json`,
stored in the current directory by default.

You can specify a different location with the ``--auth`` option:

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         xerotrust --auth /path/to/auth.json login

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         xerotrust --auth C:\path\to\auth.json login

The file contains:

* ``client_id`` - Your Xero application's client ID
* ``client_secret`` - A placeholder value (actual authentication uses PKCE)
* ``token`` - OAuth tokens including access and refresh tokens

Token Refresh
-------------

Expired tokens are automatically refreshed when you run commands. When a refresh occurs:

1. The new token is obtained from Xero
2. The authentication file is updated with the new token
3. The command proceeds with the refreshed credentials

If token refresh fails, you'll need to authenticate again with ``xerotrust login``.

Multiple Tenants
----------------

After authentication, the list of tenants (organisations) your account has access to will be
displayed:

.. code-block:: text

    Available tenants:
    - 11111111-2222-3333-4444-555555555555: My Company
    - 66666666-7777-8888-9999-000000000000: Another Company

You can specify which tenant to use for commands with the ``--tenant`` option,
or export data from all tenants.

Technical Details
-----------------

PKCE Authentication
^^^^^^^^^^^^^^^^^^^

``xerotrust`` implements the OAuth 2.0 PKCE flow, which is more secure than the traditional
authorization code flow:

1. A cryptographically random verifier is generated
2. A challenge is derived from the verifier using SHA-256
3. The authorization request includes the challenge
4. The token request includes the original verifier

This prevents interception attacks because the verifier is never transmitted until the token
exchange.

Local Web Server
^^^^^^^^^^^^^^^^

During authentication, ``xerotrust`` starts a local web server on port 12010 (by default) to receive
the OAuth callback. The server:

1. Uses FastAPI and Hypercorn for asynchronous handling
2. Provides success and error templates
3. Automatically shuts down after completing authentication
4. Validates the OAuth state parameter to prevent CSRF attacks

Authentication Errors
---------------------

Common authentication errors and their solutions:

1. **Invalid Client ID**:
   Ensure the client ID matches what's in your Xero Developer portal.

2. **State Mismatch**:
   This could indicate a CSRF attempt or a problem with the OAuth flow. Try authenticating again.

3. **Token Refresh Failed**:
   The refresh token may be expired or revoked. Run ``xerotrust login`` again.

4. **Permission Denied**:
   Verify that you granted all the requested permissions during authorization.
