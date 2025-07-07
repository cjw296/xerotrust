# Payments

[Try in API Explorer](https://api-explorer.xero.com/accounting/payments)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/Payments](https://api.xero.com/api.xro/2.0/Payments) |
| **Methods Supported** | [GET](#get-payments), [PUT](#put-payments), [POST](#post-payments), [DELETE](#delete-payments) |
| **Description** | Allows you to create individual payments in a Xero organisation<br/>Allows you to retrieve payments<br/>Allows you to update details on a payment<br/>Allows you to delete a payment |

## GET Payments

The following elements are returned in the Payments response

| Field | Description |
|-------|-------------|
| **Invoice** | See [Invoices](/documentation/api/accounting/invoices) |
| **CreditNote** | See [Credit Notes](/documentation/api/accounting/creditnotes) |
| **Prepayment** | See [Prepayments](/documentation/api/accounting/prepayments) |
| **Overpayment** | See [Overpayments](/documentation/api/accounting/overpayments) |
| **InvoiceNumber** | Number of Invoice |
| **CreditNoteNumber** | Number of Credit Note |
| **BatchPayment** | See [Batch Payments](/documentation/api/accounting/batchpayments) |
| **Account** | See [Accounts](/documentation/api/accounting/accounts) |
| **Code** | Code of account you are using to make the payment |
| **Date** | Date the payment is being made – YYYY-MM-DD |
| **CurrencyRate** | Exchange rate when payment is received |
| **Amount** | The amount of the payment |
| **Reference** | An optional description for the payment |
| **IsReconciled** | An optional parameter for the payment |
| **Status** | See [Payment Status Codes](#payment-status-codes) |
| **PaymentType** | See [Payment Types](#payment-types) |
| **UpdatedDateUTC** | Last modified date UTC format |
| **PaymentID** | Xero identifier |
| **BatchPaymentID** | Present if the payment was created as part of a batch |
| **BankAccountNumber** | The suppliers bank account number |
| **Particulars** | The suppliers bank account particulars |
| **Details** | The suppliers bank account details |
| **HasAccount** | A boolean to indicate if a contact has an validated bank account |
| **HasValidationErrors** | A boolean to indicate if a payment has an validation errors |
| **StatusAttributeString** | A string to indicate if a invoice status |

### Optional parameters for GET Payments

| Field | Description |
|-------|-------------|
| **PaymentID** | The Xero identifier for a payment – specified as a string following the endpoint name |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |
| **page** | e.g. page=1 – Up to 100 payments will be returned in a single API call |

## POST Payments

You can create new payments by POST to the payments endpoint.

### Required fields for POST Payments

| Field | Description |
|-------|-------------|
| **Invoice** | See [Invoices](/documentation/api/accounting/invoices) |
| **Account** | See [Accounts](/documentation/api/accounting/accounts) |
| **Date** | Date the payment is being made – YYYY-MM-DD |
| **Amount** | The amount of the payment |

## PUT Payments

You can update payments by PUT to the payments endpoint.

## DELETE Payments

You can delete payments by DELETE to the payments endpoint.

## Payment Status Codes

| Value | Description |
|-------|-------------|
| **AUTHORISED** | Authorised payment |
| **DELETED** | Payment has been deleted |

## Payment Types

| Value | Description |
|-------|-------------|
| **ACCRECPAYMENT** | Accounts Receivable Payment |
| **ACCPAYPAYMENT** | Accounts Payable Payment |
| **ARCREDITPAYMENT** | Accounts Receivable Credit Payment |
| **APCREDITPAYMENT** | Accounts Payable Credit Payment |
| **AROVERPAYMENTPAYMENT** | Accounts Receivable Overpayment Payment |
| **ARPREPAYMENTPAYMENT** | Accounts Receivable Prepayment Payment |
| **APPREPAYMENTPAYMENT** | Accounts Payable Prepayment Payment |
| **APOVERPAYMENTPAYMENT** | Accounts Payable Overpayment Payment |