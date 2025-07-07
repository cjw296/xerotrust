# Bank Transactions

[Try in API Explorer](https://api-explorer.xero.com/accounting/banktransactions)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/BankTransactions](https://api.xero.com/api.xro/2.0/BankTransactions) |
| **Methods Supported** | [GET](#get-banktransactions), [PUT](#put-banktransactions), [POST](#post-banktransactions), [DELETE](#delete-banktransactions) |
| **Description** | Allows you to create individual bank transactions in a Xero organisation<br/>Allows you to retrieve bank transactions<br/>Allows you to update details on a bank transaction<br/>Allows you to delete a bank transaction |

## GET Bank Transactions

The following elements are returned in the Bank Transactions response

| Field | Description |
|-------|-------------|
| **Type** | See [Bank Transaction Types](#bank-transaction-types) |
| **Contact** | See [Contacts](/documentation/api/accounting/contacts) |
| **Lineitems** | See [Line Items](/documentation/api/accounting/types#line-items) |
| **BankAccount** | See [Bank Accounts](/documentation/api/accounting/types#bank-accounts) |
| **IsReconciled** | Boolean to show if transaction is reconciled |
| **Date** | Date of transaction – YYYY-MM-DD |
| **Reference** | Reference for the transaction. Only supported for SPEND and RECEIVE transactions. |
| **CurrencyCode** | The currency that bank transaction has been raised in |
| **CurrencyRate** | The currency rate at the time of the transaction |
| **URL** | URL link to a source document – shown as "Go to [appName]" in the Xero app |
| **Status** | See [Bank Transaction Status Codes](#bank-transaction-status-codes) |
| **LineAmountTypes** | See [Line Amount Types](/documentation/api/accounting/types#line-amount-types) |
| **SubTotal** | Total of bank transaction excluding taxes |
| **TotalTax** | Total tax on bank transaction |
| **Total** | Total of bank transaction tax inclusive |
| **BankTransactionID** | Xero identifier |
| **PrepaymentID** | Xero identifier for Prepayment |
| **OverpaymentID** | Xero identifier for Overpayment |
| **UpdatedDateUTC** | Last modified date UTC format |
| **HasAttachments** | Boolean to indicate if a bank transaction has an attachment |
| **StatusAttributeString** | A string to indicate if a invoice status |

### Optional parameters for GET Bank Transactions

| Field | Description |
|-------|-------------|
| **BankTransactionID** | The Xero identifier for a bank transaction – specified as a string following the endpoint name |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |

## POST Bank Transactions

You can create new bank transactions by POST to the bank transactions endpoint.

### Required fields for POST Bank Transactions

| Field | Description |
|-------|-------------|
| **Type** | See [Bank Transaction Types](#bank-transaction-types) |
| **Contact** | See [Contacts](/documentation/api/accounting/contacts) |
| **LineItems** | See [Line Items](/documentation/api/accounting/types#line-items) |
| **BankAccount** | See [Bank Accounts](/documentation/api/accounting/types#bank-accounts) |

## PUT Bank Transactions

You can update bank transactions by PUT to the bank transactions endpoint.

## DELETE Bank Transactions

You can delete bank transactions by DELETE to the bank transactions endpoint.

## Bank Transaction Types

| Value | Description |
|-------|-------------|
| **RECEIVE** | Money received |
| **SPEND** | Money spent |

## Bank Transaction Status Codes

| Value | Description |
|-------|-------------|
| **AUTHORISED** | Approved bank transactions awaiting payment |
| **DELETED** | Draft bank transactions that are deleted |