# Linked Transactions

[Try in API Explorer](https://api-explorer.xero.com/accounting/linkedtransactions)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/LinkedTransactions](https://api.xero.com/api.xro/2.0/LinkedTransactions) |
| **Methods Supported** | [GET](#get-linkedtransactions), [PUT](#put-linkedtransactions), [POST](#post-linkedtransactions), [DELETE](#delete-linkedtransactions) |
| **Description** | Allows you to create individual linked transactions in a Xero organisation<br/>Allows you to retrieve linked transactions<br/>Allows you to update details on a linked transaction<br/>Allows you to delete a linked transaction |

## GET Linked Transactions

The following elements are returned in the Linked Transactions response

| Field | Description |
|-------|-------------|
| **LinkedTransactionID** | Xero identifier |
| **SourceTransactionID** | Filter by the SourceTransactionID |
| **SourceLineItemID** | Filter by the SourceLineItemID |
| **ContactID** | Filter by the ContactID |
| **TargetTransactionID** | Filter by the TargetTransactionID |
| **TargetLineItemID** | Filter by the TargetLineItemID |
| **Status** | Filter by the Status |
| **Type** | Filter by the Type |
| **UpdatedDateUTC** | Last modified date UTC format |

### Optional parameters for GET Linked Transactions

| Field | Description |
|-------|-------------|
| **LinkedTransactionID** | The Xero identifier for a linked transaction – specified as a string following the endpoint name |
| **SourceTransactionID** | Filter by the SourceTransactionID |
| **ContactID** | Filter by the ContactID |
| **TargetTransactionID** | Filter by the TargetTransactionID |
| **TargetLineItemID** | Filter by the TargetLineItemID |
| **Status** | Filter by the Status |
| **page** | e.g. page=1 – Up to 100 linked transactions will be returned in a single API call |

## POST Linked Transactions

You can create new linked transactions by POST to the linked transactions endpoint.

### Required fields for POST Linked Transactions

| Field | Description |
|-------|-------------|
| **SourceLineItemID** | The SourceLineItemID |
| **TargetTransactionID** | The TargetTransactionID |
| **TargetLineItemID** | The TargetLineItemID |

## PUT Linked Transactions

You can update linked transactions by PUT to the linked transactions endpoint.

## DELETE Linked Transactions

You can delete linked transactions by DELETE to the linked transactions endpoint.

## Linked Transaction Types

| Value | Description |
|-------|-------------|
| **BILLABLEEXPENSE** | Billable Expense |
| **PURCHASEORDER** | Purchase Order |
| **QUOTE** | Quote |

## Linked Transaction Status

| Value | Description |
|-------|-------------|
| **DRAFT** | Draft |
| **APPROVED** | Approved |
| **BILLED** | Billed |