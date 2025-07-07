# Invoices

[Try in API Explorer](https://api-explorer.xero.com/accounting/invoices)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/Invoices](https://api.xero.com/api.xro/2.0/Invoices) |
| **Methods Supported** | [GET](#get-invoices), [PUT](#put-invoices), [POST](#post-invoices) |
| **Description** | Allows you to create individual invoices in a Xero organisation<br/>Allows you to retrieve invoices<br/>Allows you to update details on an invoice<br/>Allows you to attach files to an invoice |

## GET Invoices

The following elements are returned in the Invoices response

| Field | Description |
|-------|-------------|
| **Type** | See [Invoice Types](#invoice-types) |
| **Contact** | See [Contacts](/documentation/api/accounting/contacts) |
| **Date** | The date of the invoice – YYYY-MM-DD |
| **DueDate** | The due date of the invoice – YYYY-MM-DD |
| **Status** | See [Invoice Status Codes](#invoice-status-codes) |
| **LineAmountTypes** | See [Line Amount Types](/documentation/api/accounting/types#line-amount-types) |
| **LineItems** | See [Line Items](/documentation/api/accounting/types#line-items) |
| **SubTotal** | The subtotal of the invoice |
| **TotalTax** | The total tax on the invoice |
| **Total** | The total of the invoice |
| **TotalDiscount** | The total discount on the invoice |
| **UpdatedDateUTC** | Last modified date UTC format |
| **CurrencyCode** | The currency that invoice has been raised in |
| **CurrencyRate** | The currency rate at the time of the invoice |
| **InvoiceID** | Xero identifier |
| **InvoiceNumber** | ACCREC – Unique alpha numeric code identifying invoice |
| **Reference** | ACCREC only – additional reference number |
| **BrandingThemeID** | See [Branding Themes](/documentation/api/accounting/brandingthemes) |
| **Url** | URL link to a source document – shown as "Go to [appName]" in the Xero app |
| **SentToContact** | Boolean to set whether the invoice in the Xero app should be marked as "sent" |
| **ExpectedPaymentDate** | The expected payment date for the invoice – YYYY-MM-DD |
| **PlannedPaymentDate** | The planned payment date for the invoice – YYYY-MM-DD |
| **CISDeduction** | CIS deduction for UK contractors |
| **HasAttachments** | Boolean to indicate if invoice has an attachment |
| **HasErrors** | Boolean to indicate if invoice has any validation errors |
| **ValidationErrors** | See [Validation Errors](#validation-errors) |
| **Warnings** | See [Warnings](#warnings) |
| **Payments** | See [Payments](/documentation/api/accounting/payments) |
| **Prepayments** | See [Prepayments](/documentation/api/accounting/prepayments) |
| **Overpayments** | See [Overpayments](/documentation/api/accounting/overpayments) |
| **AmountDue** | The amount due on the invoice |
| **AmountPaid** | The amount paid on the invoice |
| **FullyPaidOnDate** | The date the invoice was fully paid – YYYY-MM-DD |
| **AmountCredited** | The amount credited on the invoice |
| **StatusAttributeString** | A string to indicate if a invoice status |
| **RepeatingInvoiceID** | Xero identifier for repeating invoice |

### Optional parameters for GET Invoices

| Field | Description |
|-------|-------------|
| **InvoiceID** | The Xero identifier for an invoice – specified as a string following the endpoint name |
| **InvoiceNumber** | Filter by invoice number |
| **ContactIDs** | Filter by contact IDs |
| **Statuses** | Filter by invoice status |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |
| **page** | e.g. page=1 – Up to 100 invoices will be returned in a single API call |
| **unitdp** | e.g. unitdp=4 – You can opt in to use four decimal places for unit amounts |
| **summaryOnly** | e.g. summaryOnly=true – Returns only the InvoiceID and Status for each invoice |

## POST Invoices

You can create new invoices by POST to the invoices endpoint.

### Required fields for POST Invoices

| Field | Description |
|-------|-------------|
| **Type** | See [Invoice Types](#invoice-types) |
| **Contact** | See [Contacts](/documentation/api/accounting/contacts) |
| **Date** | The date of the invoice – YYYY-MM-DD |
| **DueDate** | The due date of the invoice – YYYY-MM-DD |
| **LineItems** | See [Line Items](/documentation/api/accounting/types#line-items) |

## PUT Invoices

You can update invoices by PUT to the invoices endpoint.

## Invoice Types

| Value | Description |
|-------|-------------|
| **ACCPAY** | Accounts Payable Invoice |
| **ACCREC** | Accounts Receivable Invoice |

## Invoice Status Codes

| Value | Description |
|-------|-------------|
| **DRAFT** | Draft status |
| **SUBMITTED** | Submitted for approval |
| **DELETED** | Invoice is deleted |
| **AUTHORISED** | Approved invoices awaiting payment |
| **PAID** | Invoices with payments applied |
| **VOIDED** | Invoices with zero total |

## Validation Errors

| Field | Description |
|-------|-------------|
| **Message** | Validation error message |

## Warnings

| Field | Description |
|-------|-------------|
| **Message** | Warning message |