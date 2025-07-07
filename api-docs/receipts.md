# Receipts

[Try in API Explorer](https://api-explorer.xero.com/accounting/receipts)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/Receipts](https://api.xero.com/api.xro/2.0/Receipts) |
| **Methods Supported** | [GET](#get-receipts), [PUT](#put-receipts), [POST](#post-receipts) |
| **Description** | Allows you to create individual receipts in a Xero organisation<br/>Allows you to retrieve receipts<br/>Allows you to update details on a receipt |

## GET Receipts

The following elements are returned in the Receipts response

| Field | Description |
|-------|-------------|
| **Date** | Date of receipt – YYYY-MM-DD |
| **Contact** | See [Contacts](/documentation/api/accounting/contacts) |
| **LineItems** | See [Line Items](/documentation/api/accounting/types#line-items) |
| **User** | See [Users](/documentation/api/accounting/users) |
| **Reference** | Additional reference number |
| **LineAmountTypes** | See [Line Amount Types](/documentation/api/accounting/types#line-amount-types) |
| **SubTotal** | The subtotal of the receipt |
| **TotalTax** | The total tax on the receipt |
| **Total** | The total of the receipt |
| **ReceiptID** | Xero identifier |
| **Status** | See [Receipt Status Codes](#receipt-status-codes) |
| **ReceiptNumber** | Xero generated unique identifier for receipt |
| **UpdatedDateUTC** | Last modified date UTC format |
| **HasAttachments** | Boolean to indicate if receipt has an attachment |
| **Url** | URL link to a source document – shown as "Go to [appName]" in the Xero app |

### Optional parameters for GET Receipts

| Field | Description |
|-------|-------------|
| **ReceiptID** | The Xero identifier for a receipt – specified as a string following the endpoint name |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |
| **unitdp** | e.g. unitdp=4 – You can opt in to use four decimal places for unit amounts |

## POST Receipts

You can create new receipts by POST to the receipts endpoint.

### Required fields for POST Receipts

| Field | Description |
|-------|-------------|
| **Date** | Date of receipt – YYYY-MM-DD |
| **Contact** | See [Contacts](/documentation/api/accounting/contacts) |
| **LineItems** | See [Line Items](/documentation/api/accounting/types#line-items) |
| **User** | See [Users](/documentation/api/accounting/users) |

## PUT Receipts

You can update receipts by PUT to the receipts endpoint.

## Receipt Status Codes

| Value | Description |
|-------|-------------|
| **DRAFT** | Draft receipt |
| **SUBMITTED** | Receipt is submitted |
| **AUTHORISED** | Receipt is authorised |
| **DELETED** | Receipt is deleted |