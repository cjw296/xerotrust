# Batch Payments

[Try in API Explorer](https://api-explorer.xero.com/accounting/batchpayments)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/BatchPayments](https://api.xero.com/api.xro/2.0/BatchPayments) |
| **Methods Supported** | [GET](#get-batchpayments), [PUT](#put-batchpayments), [POST](#post-batchpayments), [DELETE](#delete-batchpayments) |
| **Description** | Allows you to create individual batch payments in a Xero organisation<br/>Allows you to retrieve batch payments<br/>Allows you to update details on a batch payment<br/>Allows you to delete a batch payment |

## GET Batch Payments

The following elements are returned in the Batch Payments response

| Field | Description |
|-------|-------------|
| **Account** | See [Bank Accounts](/documentation/api/accounting/types#bank-accounts) |
| **Reference** | Reference for the batch payment |
| **Particulars** | The particulars of the batch payment |
| **Code** | A code for the batch payment |
| **Details** | The details of the batch payment |
| **Narrative** | The narrative of the batch payment |
| **BatchPaymentID** | Xero identifier |
| **DateString** | The date of the batch payment – YYYY-MM-DD |
| **Date** | The date of the batch payment |
| **Amount** | The amount of the batch payment |
| **Payments** | See [Payments](/documentation/api/accounting/payments) |
| **Type** | See [Batch Payment Types](#batch-payment-types) |
| **Status** | See [Batch Payment Status Codes](#batch-payment-status-codes) |
| **TotalAmount** | The total amount of the batch payment |
| **UpdatedDateUTC** | Last modified date UTC format |
| **IsReconciled** | Boolean to show if batch payment is reconciled |

### Optional parameters for GET Batch Payments

| Field | Description |
|-------|-------------|
| **BatchPaymentID** | The Xero identifier for a batch payment – specified as a string following the endpoint name |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |

## POST Batch Payments

You can create new batch payments by POST to the batch payments endpoint.

### Required fields for POST Batch Payments

| Field | Description |
|-------|-------------|
| **Account** | See [Bank Accounts](/documentation/api/accounting/types#bank-accounts) |
| **Reference** | Reference for the batch payment |
| **Date** | The date of the batch payment |
| **Payments** | See [Payments](/documentation/api/accounting/payments) |

## PUT Batch Payments

You can update batch payments by PUT to the batch payments endpoint.

## DELETE Batch Payments

You can delete batch payments by DELETE to the batch payments endpoint.

## Batch Payment Types

| Value | Description |
|-------|-------------|
| **PAYBATCH** | Pay batch |
| **RECBATCH** | Receive batch |

## Batch Payment Status Codes

| Value | Description |
|-------|-------------|
| **AUTHORISED** | Approved batch payments awaiting payment |
| **DELETED** | Draft batch payments that are deleted |