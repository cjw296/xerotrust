# Overpayments

[Try in API Explorer](https://api-explorer.xero.com/accounting/overpayments)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/Overpayments](https://api.xero.com/api.xro/2.0/Overpayments) |
| **Methods Supported** | [GET](#get-overpayments), [PUT](#put-overpayments) |
| **Description** | Allows you to retrieve overpayments for a Xero organisation<br/>Allows you to update details on an overpayment |

## GET Overpayments

The following elements are returned in the Overpayments response

| Field | Description |
|-------|-------------|
| **Type** | See [Overpayment Types](#overpayment-types) |
| **Contact** | See [Contacts](/documentation/api/accounting/contacts) |
| **Date** | The date of the overpayment – YYYY-MM-DD |
| **Status** | See [Overpayment Status Codes](#overpayment-status-codes) |
| **LineAmountTypes** | See [Line Amount Types](/documentation/api/accounting/types#line-amount-types) |
| **LineItems** | See [Line Items](/documentation/api/accounting/types#line-items) |
| **SubTotal** | The subtotal of the overpayment |
| **TotalTax** | The total tax on the overpayment |
| **Total** | The total of the overpayment |
| **UpdatedDateUTC** | Last modified date UTC format |
| **CurrencyCode** | The currency that overpayment has been raised in |
| **CurrencyRate** | The currency rate for a multicurrency overpayment |
| **OverpaymentID** | Xero identifier |
| **HasAttachments** | Boolean to indicate if overpayment has an attachment |
| **Allocations** | See [Allocations](#allocations) |
| **Payments** | See [Payments](/documentation/api/accounting/payments) |
| **AppliedAmount** | The amount of applied to an invoice |
| **RemainingCredit** | The remaining credit balance on the overpayment |

### Optional parameters for GET Overpayments

| Field | Description |
|-------|-------------|
| **OverpaymentID** | The Xero identifier for an overpayment – specified as a string following the endpoint name |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |
| **page** | e.g. page=1 – Up to 100 overpayments will be returned in a single API call |
| **unitdp** | e.g. unitdp=4 – You can opt in to use four decimal places for unit amounts |

## PUT Overpayments

You can update overpayments by PUT to the overpayments endpoint.

## Overpayment Types

| Value | Description |
|-------|-------------|
| **RECEIVE-OVERPAYMENT** | Receive Overpayment |
| **SPEND-OVERPAYMENT** | Spend Overpayment |

## Overpayment Status Codes

| Value | Description |
|-------|-------------|
| **AUTHORISED** | Approved overpayments |
| **PAID** | Overpayments with payments applied |
| **VOIDED** | Overpayments with zero total |

## Allocations

| Field | Description |
|-------|-------------|
| **AllocationID** | Xero identifier |
| **Invoice** | See [Invoices](/documentation/api/accounting/invoices) |
| **Amount** | The amount of the allocation |
| **Date** | The date of the allocation |
| **AppliedAmount** | The amount of applied to an invoice |
| **StatementLineID** | The statement line ID for the allocation |