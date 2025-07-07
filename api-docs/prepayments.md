# Prepayments

[Try in API Explorer](https://api-explorer.xero.com/accounting/prepayments)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/Prepayments](https://api.xero.com/api.xro/2.0/Prepayments) |
| **Methods Supported** | [GET](#get-prepayments), [PUT](#put-prepayments) |
| **Description** | Allows you to retrieve prepayments for a Xero organisation<br/>Allows you to update details on a prepayment |

## GET Prepayments

The following elements are returned in the Prepayments response

| Field | Description |
|-------|-------------|
| **Type** | See [Prepayment Types](#prepayment-types) |
| **Contact** | See [Contacts](/documentation/api/accounting/contacts) |
| **Date** | The date of the prepayment – YYYY-MM-DD |
| **Status** | See [Prepayment Status Codes](#prepayment-status-codes) |
| **LineAmountTypes** | See [Line Amount Types](/documentation/api/accounting/types#line-amount-types) |
| **LineItems** | See [Line Items](/documentation/api/accounting/types#line-items) |
| **SubTotal** | The subtotal of the prepayment |
| **TotalTax** | The total tax on the prepayment |
| **Total** | The total of the prepayment |
| **UpdatedDateUTC** | Last modified date UTC format |
| **CurrencyCode** | The currency that prepayment has been raised in |
| **CurrencyRate** | The currency rate for a multicurrency prepayment |
| **PrepaymentID** | Xero identifier |
| **HasAttachments** | Boolean to indicate if prepayment has an attachment |
| **Allocations** | See [Allocations](#allocations) |
| **Payments** | See [Payments](/documentation/api/accounting/payments) |
| **AppliedAmount** | The amount of applied to an invoice |
| **RemainingCredit** | The remaining credit balance on the prepayment |

### Optional parameters for GET Prepayments

| Field | Description |
|-------|-------------|
| **PrepaymentID** | The Xero identifier for a prepayment – specified as a string following the endpoint name |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |
| **page** | e.g. page=1 – Up to 100 prepayments will be returned in a single API call |
| **unitdp** | e.g. unitdp=4 – You can opt in to use four decimal places for unit amounts |

## PUT Prepayments

You can update prepayments by PUT to the prepayments endpoint.

## Prepayment Types

| Value | Description |
|-------|-------------|
| **RECEIVE-PREPAYMENT** | Receive Prepayment |
| **SPEND-PREPAYMENT** | Spend Prepayment |

## Prepayment Status Codes

| Value | Description |
|-------|-------------|
| **AUTHORISED** | Approved prepayments |
| **PAID** | Prepayments with payments applied |
| **VOIDED** | Prepayments with zero total |

## Allocations

| Field | Description |
|-------|-------------|
| **AllocationID** | Xero identifier |
| **Invoice** | See [Invoices](/documentation/api/accounting/invoices) |
| **Amount** | The amount of the allocation |
| **Date** | The date of the allocation |
| **AppliedAmount** | The amount of applied to an invoice |
| **StatementLineID** | The statement line ID for the allocation |