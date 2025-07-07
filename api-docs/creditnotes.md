# Credit Notes

[Try in API Explorer](https://api-explorer.xero.com/accounting/creditnotes)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/CreditNotes](https://api.xero.com/api.xro/2.0/CreditNotes) |
| **Methods Supported** | [GET](#get-creditnotes), [PUT](#put-creditnotes), [POST](#post-creditnotes) |
| **Description** | Allows you to create individual credit notes in a Xero organisation<br/>Allows you to retrieve credit notes<br/>Allows you to update details on a credit note<br/>Allows you to attach files to a credit note |

## GET Credit Notes

The following elements are returned in the Credit Notes response

| Field | Description |
|-------|-------------|
| **Type** | See [Credit Note Types](#credit-note-types) |
| **Contact** | See [Contacts](/documentation/api/accounting/contacts) |
| **Date** | The date of the credit note – YYYY-MM-DD |
| **Status** | See [Credit Note Status Codes](#credit-note-status-codes) |
| **LineAmountTypes** | See [Line Amount Types](/documentation/api/accounting/types#line-amount-types) |
| **LineItems** | See [Line Items](/documentation/api/accounting/types#line-items) |
| **SubTotal** | The subtotal of the credit note |
| **TotalTax** | The total tax on the credit note |
| **Total** | The total of the credit note |
| **UpdatedDateUTC** | Last modified date UTC format |
| **CurrencyCode** | The currency that credit note has been raised in |
| **CurrencyRate** | The currency rate for a multicurrency credit note |
| **CreditNoteID** | Xero identifier |
| **CreditNoteNumber** | ACCRECCREDIT – Unique alpha numeric code identifying credit note |
| **Reference** | ACCRECCREDIT only – additional reference number |
| **SentToContact** | Boolean to set whether the credit note in the Xero app should be marked as "sent" |
| **BrandingThemeID** | See [Branding Themes](/documentation/api/accounting/brandingthemes) |
| **HasAttachments** | Boolean to indicate if credit note has an attachment |
| **HasErrors** | Boolean to indicate if credit note has any validation errors |
| **ValidationErrors** | See [Validation Errors](#validation-errors) |
| **Warnings** | See [Warnings](#warnings) |
| **Payments** | See [Payments](/documentation/api/accounting/payments) |
| **Allocations** | See [Allocations](#allocations) |
| **RemainingCredit** | The remaining credit amount on the credit note |

### Optional parameters for GET Credit Notes

| Field | Description |
|-------|-------------|
| **CreditNoteID** | The Xero identifier for a credit note – specified as a string following the endpoint name |
| **CreditNoteNumber** | Filter by credit note number |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |
| **page** | e.g. page=1 – Up to 100 credit notes will be returned in a single API call |
| **unitdp** | e.g. unitdp=4 – You can opt in to use four decimal places for unit amounts |

## POST Credit Notes

You can create new credit notes by POST to the credit notes endpoint.

### Required fields for POST Credit Notes

| Field | Description |
|-------|-------------|
| **Type** | See [Credit Note Types](#credit-note-types) |
| **Contact** | See [Contacts](/documentation/api/accounting/contacts) |
| **Date** | The date of the credit note – YYYY-MM-DD |
| **LineItems** | See [Line Items](/documentation/api/accounting/types#line-items) |

## PUT Credit Notes

You can update credit notes by PUT to the credit notes endpoint.

## Credit Note Types

| Value | Description |
|-------|-------------|
| **ACCPAYCREDIT** | Accounts Payable Credit Note |
| **ACCRECCREDIT** | Accounts Receivable Credit Note |

## Credit Note Status Codes

| Value | Description |
|-------|-------------|
| **DRAFT** | Draft status |
| **SUBMITTED** | Submitted for approval |
| **DELETED** | Credit note is deleted |
| **AUTHORISED** | Approved credit notes |
| **PAID** | Credit notes with payments applied |
| **VOIDED** | Credit notes with zero total |

## Allocations

| Field | Description |
|-------|-------------|
| **AllocationID** | Xero identifier |
| **Invoice** | See [Invoices](/documentation/api/accounting/invoices) |
| **Amount** | The amount of the allocation |
| **Date** | The date of the allocation |

## Validation Errors

| Field | Description |
|-------|-------------|
| **Message** | Validation error message |

## Warnings

| Field | Description |
|-------|-------------|
| **Message** | Warning message |