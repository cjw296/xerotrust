# Tracking Categories

[Try in API Explorer](https://api-explorer.xero.com/accounting/trackingcategories)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/TrackingCategories](https://api.xero.com/api.xro/2.0/TrackingCategories) |
| **Methods Supported** | [GET](#get-trackingcategories), [PUT](#put-trackingcategories), [POST](#post-trackingcategories), [DELETE](#delete-trackingcategories) |
| **Description** | Allows you to create individual tracking categories in a Xero organisation<br/>Allows you to retrieve tracking categories<br/>Allows you to update details on a tracking category<br/>Allows you to delete a tracking category |

## GET Tracking Categories

The following elements are returned in the Tracking Categories response

| Field | Description |
|-------|-------------|
| **TrackingCategoryID** | Xero identifier |
| **Name** | The name of the tracking category |
| **Status** | See [Tracking Category Status Codes](#tracking-category-status-codes) |
| **Options** | See [Tracking Options](#tracking-options) |

### Optional parameters for GET Tracking Categories

| Field | Description |
|-------|-------------|
| **TrackingCategoryID** | The Xero identifier for a tracking category – specified as a string following the endpoint name |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |
| **includeArchived** | e.g. includeArchived=true – Categories and options with a status of ARCHIVED will be included |

## POST Tracking Categories

You can create new tracking categories by POST to the tracking categories endpoint.

### Required fields for POST Tracking Categories

| Field | Description |
|-------|-------------|
| **Name** | The name of the tracking category |

## PUT Tracking Categories

You can update tracking categories by PUT to the tracking categories endpoint.

## DELETE Tracking Categories

You can delete tracking categories by DELETE to the tracking categories endpoint.

## Tracking Category Status Codes

| Value | Description |
|-------|-------------|
| **ACTIVE** | Active tracking category |
| **ARCHIVED** | Archived tracking category |
| **DELETED** | Deleted tracking category |

## Tracking Options

The tracking options endpoint allows you to manage individual options within a tracking category.

### GET Tracking Options

| Field | Description |
|-------|-------------|
| **TrackingOptionID** | Xero identifier |
| **Name** | The name of the tracking option |
| **Status** | See [Tracking Option Status Codes](#tracking-option-status-codes) |

### POST Tracking Options

You can create new tracking options by POST to the tracking options endpoint:

**URL**: `/TrackingCategories/{TrackingCategoryID}/Options`

### PUT Tracking Options

You can update tracking options by PUT to the tracking options endpoint:

**URL**: `/TrackingCategories/{TrackingCategoryID}/Options/{TrackingOptionID}`

### DELETE Tracking Options

You can delete tracking options by DELETE to the tracking options endpoint:

**URL**: `/TrackingCategories/{TrackingCategoryID}/Options/{TrackingOptionID}`

## Tracking Option Status Codes

| Value | Description |
|-------|-------------|
| **ACTIVE** | Active tracking option |
| **ARCHIVED** | Archived tracking option |
| **DELETED** | Deleted tracking option |

## Usage in Line Items

Tracking categories can be applied to line items in various transactions:

```json
{
  "TrackingCategories": [
    {
      "TrackingCategoryID": "tracking-category-id",
      "Name": "Department",
      "Option": "Sales"
    }
  ]
}
```

## Limitations

- Maximum of 2 tracking categories per organisation
- Maximum of 1000 tracking options per tracking category
- Tracking categories cannot be renamed once created
- Deleted tracking categories cannot be restored