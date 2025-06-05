.. include:: ../README.rst

Quickstart
~~~~~~~~~~

1. Make sure you have ``uv`` `installed`__.

   __ https://docs.astral.sh/uv/getting-started/installation/

2. Install ``xerotrust`` as a tool.

   .. code-block:: bash

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

     Check the `terms and conditions` box and then click the `Create app` buttons.

3. Authenticate and allow access by running:

   .. code-block:: bash

       xerotrust login

   For `Client ID`, navigate to the application you set up above in Xero's `App Management page`__,
   then click on the `Configuration` tab and finally click the `Copy` button in the `Client id`
   section.

   __ https://developer.xero.com/app/manage/

   Once you submit the `Client ID`, a web browser will pop up for you to allow access
   for `xerotrust`.

4. Export your Xero data to the current directory:

   .. code-block:: bash

       uv run xerotrust export

5. Flatten all your journals to a single ``.csv``:

   .. code-block:: bash

       uv run xerotrust journals flatten */journals-*.jsonl -o journals.csv

Full documentation is provided here:

.. toctree::
   :maxdepth: 2

   usage.rst
   export.rst
   flattening.rst
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
