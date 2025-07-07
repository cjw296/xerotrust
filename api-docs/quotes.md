# Quotes

[Try in API Explorer](https://api-explorer.xero.com/accounting/quotes)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/Quotes](https://api.xero.com/api.xro/2.0/Quotes) |
| **Methods Supported** | [GET](#get-quotes), [PUT](#put-quotes), [POST](#post-quotes) |
| **Description** | Allows you to create individual quotes in a Xero organisation<br/>Allows you to retrieve quotes<br/>Allows you to update details on a quote |

## GET Quotes

The following elements are returned in the Quotes response

| Field | Description |
|-------|-------------|
| **QuoteID** | Xero identifier |
| **QuoteNumber** | Unique alpha numeric code identifying quote |
| **Reference** | Additional reference number |
| **Terms** | Terms of the quote |
| **Contact** | See [Contacts](/documentation/api/accounting/contacts) |
| **LineItems** | See [Line Items](/documentation/api/accounting/types#line-items) |
| **Date** | Date quote was issued – YYYY-MM-DD |
| **DateString** | Date quote was issued |
| **ExpiryDate** | Date quote expires – YYYY-MM-DD |
| **ExpiryDateString** | Date quote expires |
| **Status** | See [Quote Status Codes](#quote-status-codes) |
| **CurrencyCode** | The currency that quote has been raised in |
| **CurrencyRate** | The currency rate for a multicurrency quote |
| **SubTotal** | The subtotal of the quote |
| **TotalTax** | The total tax on the quote |
| **Total** | The total of the quote |
| **TotalDiscount** | The total discount on the quote |
| **Title** | Title text for the quote |
| **Summary** | Summary text for the quote |
| **BrandingThemeID** | See [Branding Themes](/documentation/api/accounting/brandingthemes) |
| **UpdatedDateUTC** | Last modified date UTC format |
| **LineAmountTypes** | See [Line Amount Types](/documentation/api/accounting/types#line-amount-types) |
| **StatusAttributeString** | A string to indicate if a quote status |
| **Validation Errors** | Displays array of validation error messages from the API |

### Optional parameters for GET Quotes

| Field | Description |
|-------|-------------|
| **QuoteID** | The Xero identifier for a quote – specified as a string following the endpoint name |
| **QuoteNumber** | Filter by quote number |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |
| **page** | e.g. page=1 – Up to 100 quotes will be returned in a single API call |

## POST Quotes

You can create new quotes by POST to the quotes endpoint.

### Required fields for POST Quotes

| Field | Description |
|-------|-------------|
| **Contact** | See [Contacts](/documentation/api/accounting/contacts) |
| **LineItems** | See [Line Items](/documentation/api/accounting/types#line-items) |
| **Date** | Date quote was issued – YYYY-MM-DD |

## PUT Quotes

You can update quotes by PUT to the quotes endpoint.

## Quote Status Codes

| Value | Description |
|-------|-------------|
| **DRAFT** | Draft quote |
| **SENT** | Quote has been sent |
| **DECLINED** | Quote has been declined |
| **ACCEPTED** | Quote has been accepted |
| **EXPIRED** | Quote has expired |
| **DELETED** | Quote has been deleted |
| **INVOICED** | Quote has been invoiced |