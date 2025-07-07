# Repeating Invoices

[Try in API Explorer](https://api-explorer.xero.com/accounting/repeatinginvoices)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/RepeatingInvoices](https://api.xero.com/api.xro/2.0/RepeatingInvoices) |
| **Methods Supported** | [GET](#get-repeatinginvoices), [PUT](#put-repeatinginvoices), [POST](#post-repeatinginvoices) |
| **Description** | Allows you to create individual repeating invoices in a Xero organisation<br/>Allows you to retrieve repeating invoices<br/>Allows you to update details on a repeating invoice |

## GET Repeating Invoices

The following elements are returned in the Repeating Invoices response

| Field | Description |
|-------|-------------|
| **Type** | See [Invoice Types](#invoice-types) |
| **Contact** | See [Contacts](/documentation/api/accounting/contacts) |
| **Schedule** | See [Schedule](#schedule) |
| **LineItems** | See [Line Items](/documentation/api/accounting/types#line-items) |
| **LineAmountTypes** | See [Line Amount Types](/documentation/api/accounting/types#line-amount-types) |
| **Reference** | ACCREC only – additional reference number |
| **BrandingThemeID** | See [Branding Themes](/documentation/api/accounting/brandingthemes) |
| **CurrencyCode** | The currency that invoice has been raised in |
| **Status** | See [Repeating Invoice Status Codes](#repeating-invoice-status-codes) |
| **SubTotal** | The subtotal of the repeating invoice |
| **TotalTax** | The total tax on the repeating invoice |
| **Total** | The total of the repeating invoice |
| **RepeatingInvoiceID** | Xero identifier |
| **ID** | See RepeatingInvoiceID |
| **HasAttachments** | Boolean to indicate if repeating invoice has an attachment |

### Optional parameters for GET Repeating Invoices

| Field | Description |
|-------|-------------|
| **RepeatingInvoiceID** | The Xero identifier for a repeating invoice – specified as a string following the endpoint name |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |

## POST Repeating Invoices

You can create new repeating invoices by POST to the repeating invoices endpoint.

### Required fields for POST Repeating Invoices

| Field | Description |
|-------|-------------|
| **Type** | See [Invoice Types](#invoice-types) |
| **Contact** | See [Contacts](/documentation/api/accounting/contacts) |
| **Schedule** | See [Schedule](#schedule) |
| **LineItems** | See [Line Items](/documentation/api/accounting/types#line-items) |

## PUT Repeating Invoices

You can update repeating invoices by PUT to the repeating invoices endpoint.

## Invoice Types

| Value | Description |
|-------|-------------|
| **ACCPAY** | Accounts Payable Invoice |
| **ACCREC** | Accounts Receivable Invoice |

## Repeating Invoice Status Codes

| Value | Description |
|-------|-------------|
| **DRAFT** | Draft repeating invoice |
| **AUTHORISED** | Authorised repeating invoice |
| **DELETED** | Deleted repeating invoice |

## Schedule

| Field | Description |
|-------|-------------|
| **Period** | See [Schedule Periods](#schedule-periods) |
| **Unit** | See [Schedule Units](#schedule-units) |
| **DueDate** | Integer used with the unit e.g. 1 (every 1 week), 2 (every 2 months) |
| **DueDateType** | See [Due Date Types](#due-date-types) |
| **StartDate** | Date the first invoice of the current version of the repeating schedule was generated – YYYY-MM-DD |
| **EndDate** | The calendar date of the last invoice in the repeating schedule – YYYY-MM-DD |
| **NextScheduledDate** | Invoice will be created on this date – YYYY-MM-DD |

## Schedule Periods

| Value | Description |
|-------|-------------|
| **1** | 1 |
| **2** | 2 |
| **3** | 3 |
| **4** | 4 |

## Schedule Units

| Value | Description |
|-------|-------------|
| **WEEKLY** | Weekly |
| **MONTHLY** | Monthly |

## Due Date Types

| Value | Description |
|-------|-------------|
| **DAYSAFTERBILLDATE** | Days after bill date |
| **DAYSAFTERBILLMONTH** | Days after bill month |
| **OFCURRENTMONTH** | Of current month |
| **OFFOLLOWINGMONTH** | Of following month |