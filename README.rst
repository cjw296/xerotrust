xerotrust
=========
|Docs|_  |PyPI|_ |Git|_

.. |Docs| image:: https://readthedocs.org/projects/xerotrust/badge/?version=latest
.. _Docs: https://xerotrust.readthedocs.io/

.. |PyPI| image:: https://badge.fury.io/py/xerotrust.svg
.. _PyPI: https://pypi.org/project/xerotrust/

.. |Git| image:: https://github.com/cjw296/xerotrust/actions/workflows/ci.yml/badge.svg
.. _Git: https://github.com/cjw296/xerotrust

This package provides a command line tool to explore and export data from `Xero`__ accounts.
The intention behind this is to give a safety net in the event that you lose access to your
Xero accounting data, and also to allow you to analyse it with traditional tools such as
Excel along with novel approaches you may wish to take using LLMs.

__ https://www.xero.com/

Documentation
-------------

Full documentation is available at https://xerotrust.readthedocs.io/en/latest/

**Quick Start:** https://xerotrust.readthedocs.io/en/latest/

Key resources:

- `Installation Guide <https://xerotrust.readthedocs.io/en/latest/installation.html>`_
- `Command Reference <https://xerotrust.readthedocs.io/en/latest/commands.html>`_
- `API Documentation <https://xerotrust.readthedocs.io/en/latest/api.html>`_
- `GitHub Repository <https://github.com/cjw296/xerotrust>`_

Supported Exports
-----------------

xerotrust can export the following Xero data:

=====================  ====================================================================
Category               Exports
=====================  ====================================================================
**Core Accounting**    Accounts, Contacts, Invoices, Bills (Creditor Invoices),
                       Credit Notes, Bank Transactions, Bank Transfers, Payments,
                       Batch Payments
**Journals**           Journals, Manual Journals
**Reports**            Balance Sheet, Profit & Loss, Trial Balance, Bank Summary,
                       Executive Summary, Aged Receivables, Aged Payables,
                       Budget Summary
**Supporting Data**    Items, Purchase Orders, Quotes, Tax Rates, Tracking Categories,
                       Currencies, Employees, Users, Branding Themes, Contact Groups,
                       Repeating Invoices
**Files**              Attachments from Invoices, Bills, Bank Transactions, Contacts,
                       and other supported entities
=====================  ====================================================================
