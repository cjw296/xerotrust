# Manual Journals

[Try in API Explorer](https://api-explorer.xero.com/accounting/manualjournals)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/ManualJournals](https://api.xero.com/api.xro/2.0/ManualJournals) |
| **Methods Supported** | [GET](#get-manualjournals), [PUT](#put-manualjournals), [POST](#post-manualjournals) |
| **Description** | Allows you to create individual manual journals in a Xero organisation<br/>Allows you to retrieve manual journals<br/>Allows you to update details on a manual journal |

## GET Manual Journals

The following elements are returned in the Manual Journals response

| Field | Description |
|-------|-------------|
| **ManualJournalID** | Xero identifier |
| **Narration** | Description of journal being posted |
| **JournalLines** | See [Journal Lines](#journal-lines) |
| **Date** | Date journal was posted – YYYY-MM-DD |
| **Status** | See [Manual Journal Status Codes](#manual-journal-status-codes) |
| **Url** | Url link to a source document – shown as "Go to [appName]" in the Xero app |
| **ShowOnCashBasisReports** | Boolean – default is true if not specified |
| **HasAttachments** | Boolean to indicate if manual journal has an attachment |
| **UpdatedDateUTC** | Last modified date UTC format |

### Optional parameters for GET Manual Journals

| Field | Description |
|-------|-------------|
| **ManualJournalID** | The Xero identifier for a manual journal – specified as a string following the endpoint name |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |
| **page** | e.g. page=1 – Up to 100 manual journals will be returned in a single API call |

## POST Manual Journals

You can create new manual journals by POST to the manual journals endpoint.

### Required fields for POST Manual Journals

| Field | Description |
|-------|-------------|
| **Narration** | Description of journal being posted |
| **JournalLines** | See [Journal Lines](#journal-lines) |
| **Date** | Date journal was posted – YYYY-MM-DD |

## PUT Manual Journals

You can update manual journals by PUT to the manual journals endpoint.

## Manual Journal Status Codes

| Value | Description |
|-------|-------------|
| **DRAFT** | Draft manual journal |
| **POSTED** | Posted manual journal |
| **DELETED** | Deleted manual journal |
| **VOIDED** | Voided manual journal |

## Journal Lines

| Field | Description |
|-------|-------------|
| **Description** | Description for journal line |
| **AccountCode** | See [Accounts](/documentation/api/accounting/accounts) |
| **LineAmount** | Total for line |
| **TaxType** | See [Tax Types](/documentation/api/accounting/types#tax-rates) |
| **TaxAmount** | The tax amount is auto calculated as a percentage of the line amount |
| **TrackingCategories** | See [Tracking Categories](/documentation/api/accounting/trackingcategories) |