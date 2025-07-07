# Purchase Orders

[Try in API Explorer](https://api-explorer.xero.com/accounting/purchaseorders)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/PurchaseOrders](https://api.xro.com/api.xro/2.0/PurchaseOrders) |
| **Methods Supported** | [GET](#get-purchaseorders), [PUT](#put-purchaseorders), [POST](#post-purchaseorders) |
| **Description** | Allows you to create individual purchase orders in a Xero organisation<br/>Allows you to retrieve purchase orders<br/>Allows you to update details on a purchase order |

## GET Purchase Orders

The following elements are returned in the Purchase Orders response

| Field | Description |
|-------|-------------|
| **Contact** | See [Contacts](/documentation/api/accounting/contacts) |
| **LineItems** | See [Line Items](/documentation/api/accounting/types#line-items) |
| **Date** | Date purchase order was issued – YYYY-MM-DD |
| **DeliveryDate** | Date the goods are to be delivered – YYYY-MM-DD |
| **LineAmountTypes** | See [Line Amount Types](/documentation/api/accounting/types#line-amount-types) |
| **PurchaseOrderNumber** | Unique alpha numeric code identifying purchase order |
| **Reference** | Additional reference number |
| **BrandingThemeID** | See [Branding Themes](/documentation/api/accounting/brandingthemes) |
| **CurrencyCode** | The currency that purchase order has been raised in |
| **CurrencyRate** | The currency rate for a multicurrency purchase order |
| **Status** | See [Purchase Order Status Codes](#purchase-order-status-codes) |
| **SentToContact** | Boolean to set whether the purchase order should be marked as "sent" |
| **DeliveryAddress** | The address the goods are to be delivered to |
| **AttentionTo** | The person that the delivery is going to |
| **Telephone** | The phone number for the person accepting the delivery |
| **DeliveryInstructions** | A free text feild for delivery instructions |
| **ExpectedArrivalDate** | The date the goods are expected to arrive |
| **PurchaseOrderID** | Xero identifier |
| **HasErrors** | Boolean to indicate if a purchase order has an validation errors |
| **IsDiscounted** | Boolean to indicate if a purchase order has a discount |
| **HasAttachments** | Boolean to indicate if purchase order has an attachment |
| **UpdatedDateUTC** | Last modified date UTC format |
| **StatusAttributeString** | A string to indicate if a invoice status |

### Optional parameters for GET Purchase Orders

| Field | Description |
|-------|-------------|
| **PurchaseOrderID** | The Xero identifier for a purchase order – specified as a string following the endpoint name |
| **PurchaseOrderNumber** | Filter by purchase order number |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |
| **page** | e.g. page=1 – Up to 100 purchase orders will be returned in a single API call |

## POST Purchase Orders

You can create new purchase orders by POST to the purchase orders endpoint.

### Required fields for POST Purchase Orders

| Field | Description |
|-------|-------------|
| **Contact** | See [Contacts](/documentation/api/accounting/contacts) |
| **LineItems** | See [Line Items](/documentation/api/accounting/types#line-items) |
| **Date** | Date purchase order was issued – YYYY-MM-DD |

## PUT Purchase Orders

You can update purchase orders by PUT to the purchase orders endpoint.

## Purchase Order Status Codes

| Value | Description |
|-------|-------------|
| **DRAFT** | Draft purchase order |
| **SUBMITTED** | Submitted purchase order |
| **AUTHORISED** | Authorised purchase order |
| **BILLED** | Billed purchase order |
| **DELETED** | Deleted purchase order |