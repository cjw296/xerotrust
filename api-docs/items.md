# Items

[Try in API Explorer](https://api-explorer.xero.com/accounting/items)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/Items](https://api.xero.com/api.xro/2.0/Items) |
| **Methods Supported** | [GET](#get-items), [PUT](#put-items), [POST](#post-items), [DELETE](#delete-items) |
| **Description** | Allows you to create individual items in a Xero organisation<br/>Allows you to retrieve items<br/>Allows you to update details on an item<br/>Allows you to delete an item |

## GET Items

The following elements are returned in the Items response

| Field | Description |
|-------|-------------|
| **ItemID** | Xero identifier |
| **Code** | User defined item code |
| **Name** | The name of the item |
| **IsSold** | Boolean value – true for items that are sold |
| **IsPurchased** | Boolean value – true for items that are purchased |
| **Description** | The sales description of the item |
| **PurchaseDescription** | The purchase description of the item |
| **PurchaseDetails** | See [Purchase Details](#purchase-details) |
| **SalesDetails** | See [Sales Details](#sales-details) |
| **IsTrackedAsInventory** | Boolean value – true if the item is tracked as inventory |
| **InventoryAssetAccountCode** | The inventory asset account for the item |
| **TotalCostPool** | The total cost pool for the item |
| **QuantityOnHand** | The quantity on hand for the item |
| **UpdatedDateUTC** | Last modified date UTC format |

### Optional parameters for GET Items

| Field | Description |
|-------|-------------|
| **ItemID** | The Xero identifier for an item – specified as a string following the endpoint name |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |
| **unitdp** | e.g. unitdp=4 – You can opt in to use four decimal places for unit amounts |

## POST Items

You can create new items by POST to the items endpoint.

### Required fields for POST Items

| Field | Description |
|-------|-------------|
| **Code** | User defined item code |
| **Name** | The name of the item |

## PUT Items

You can update items by PUT to the items endpoint.

## DELETE Items

You can delete items by DELETE to the items endpoint.

## Purchase Details

| Field | Description |
|-------|-------------|
| **UnitPrice** | Unit price of the item when purchased |
| **AccountCode** | Default account code to be used when purchasing the item |
| **COGSAccountCode** | Cost of goods sold account code |
| **TaxType** | See [Tax Types](/documentation/api/accounting/types#tax-rates) |

## Sales Details

| Field | Description |
|-------|-------------|
| **UnitPrice** | Unit price of the item when sold |
| **AccountCode** | Default account code to be used when selling the item |
| **TaxType** | See [Tax Types](/documentation/api/accounting/types#tax-rates) |