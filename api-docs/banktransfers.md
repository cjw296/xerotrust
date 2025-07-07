# Bank Transfers

[Try in API Explorer](https://api-explorer.xero.com/accounting/banktransfers)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/BankTransfers](https://api.xero.com/api.xro/2.0/BankTransfers) |
| **Methods Supported** | [GET](#get-banktransfers), [PUT](#put-banktransfers), [POST](#post-banktransfers), [DELETE](#delete-banktransfers) |
| **Description** | Allows you to create individual bank transfers in a Xero organisation<br/>Allows you to retrieve bank transfers<br/>Allows you to update details on a bank transfer<br/>Allows you to delete a bank transfer |

## GET Bank Transfers

The following elements are returned in the Bank Transfers response

| Field | Description |
|-------|-------------|
| **FromBankAccount** | See [Bank Accounts](/documentation/api/accounting/types#bank-accounts) |
| **ToBankAccount** | See [Bank Accounts](/documentation/api/accounting/types#bank-accounts) |
| **Amount** | The amount of the transfer |
| **Date** | The date of the transfer – YYYY-MM-DD |
| **BankTransferID** | Xero identifier |
| **CurrencyRate** | The currency rate at the time of the transfer |
| **FromBankTransactionID** | The Bank Transaction ID for the source account |
| **ToBankTransactionID** | The Bank Transaction ID for the destination account |
| **Reference** | Reference for the bank transfer |
| **HasAttachments** | Boolean to indicate if a bank transfer has an attachment |
| **UpdatedDateUTC** | Last modified date UTC format |

### Optional parameters for GET Bank Transfers

| Field | Description |
|-------|-------------|
| **BankTransferID** | The Xero identifier for a bank transfer – specified as a string following the endpoint name |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |

## POST Bank Transfers

You can create new bank transfers by POST to the bank transfers endpoint.

### Required fields for POST Bank Transfers

| Field | Description |
|-------|-------------|
| **FromBankAccount** | See [Bank Accounts](/documentation/api/accounting/types#bank-accounts) |
| **ToBankAccount** | See [Bank Accounts](/documentation/api/accounting/types#bank-accounts) |
| **Amount** | The amount of the transfer |

## PUT Bank Transfers

You can update bank transfers by PUT to the bank transfers endpoint.

## DELETE Bank Transfers

You can delete bank transfers by DELETE to the bank transfers endpoint.