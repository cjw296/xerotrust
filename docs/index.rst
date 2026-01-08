.. include:: ../README.rst

.. note::

  This tool makes use of the Xero API Journals endpoint in order to extract the
  raw data from the Xero general ledger. To access this you will need to register your own
  app within the Xero developer portal. Xero has announced a new pricing structure that
  will take effect 2 March 2026. Under the new pricing tiers access to Journals endpoint
  will only be available to apps that are on their advanced tier.
  We would suggest contacting api@xero.com with any questions.

.. _quickstart:

Quickstart
~~~~~~~~~~

1. Make sure you have ``uv`` `installed`__.

   __ https://docs.astral.sh/uv/getting-started/installation/

2. Install ``xerotrust`` as a tool:

   .. tabs::

      .. group-tab:: Linux/macOS

         .. code-block:: bash

            uv tool install -U xerotrust

      .. group-tab:: Windows (PowerShell)

         .. code-block:: powershell

            uv tool install -U xerotrust

3. Set up the App in Xero Developer:

   - Go to Xero's `App Management page`__.

     __ https://developer.xero.com/app/manage/

   - Click the `New app` button and fill in the form as follows:

     `App name`
       ``zerotrust`` - Xero won't allow apps with "xero" in their name!

     `Integration type`
       Select "**Mobile or desktop app** - Auth code with PKCE.
       For native apps that can’t securely store a client secret".

     `Company or application URL`
       ``https://xerotrust.readthedocs.io/``

     `Redirect URI`
       ``http://localhost:12010/``

     Check the `terms and conditions` box and then click the `Create app` button.

4. Authenticate:

   .. tabs::

      .. group-tab:: Linux/macOS

         .. code-block:: bash

            xerotrust login

      .. group-tab:: Windows (PowerShell)

         .. code-block:: powershell

            xerotrust login

   For `Client ID`, navigate to the application you set up above in Xero's `App Management page`__,
   then click on the `Configuration` tab and finally click the `Copy` button in the `Client ID`
   section.

   __ https://developer.xero.com/app/manage/

   Once you submit the `Client ID`, a web browser will pop up for you to allow access
   for `xerotrust`.

   .. tabs::

      .. group-tab:: Linux/macOS

         .. code-block:: bash

            xerotrust login

      .. group-tab:: Windows (PowerShell)

         .. code-block:: powershell

            xerotrust login

   Enter your app's Client ID when prompted.

5. Export your data:

   .. tabs::

      .. group-tab:: Linux/macOS

         .. code-block:: bash

            xerotrust export

      .. group-tab:: Windows (PowerShell)

         .. code-block:: powershell

            xerotrust export

Your Xero data is now saved in folders organized by tenant name.
You can later update your exported data with:

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         xerotrust export --update

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         xerotrust export --update

Full documentation is provided here:

.. toctree::
   :maxdepth: 2

   usage.rst
   export.rst
   checks.rst
   authentication.rst
   development.rst
   changes.rst
   license.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
