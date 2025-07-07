# Expense Claims

[Try in API Explorer](https://api-explorer.xero.com/accounting/expenseclaims)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/ExpenseClaims](https://api.xero.com/api.xro/2.0/ExpenseClaims) |
| **Methods Supported** | [GET](#get-expenseclaims), [PUT](#put-expenseclaims), [POST](#post-expenseclaims) |
| **Description** | Allows you to create individual expense claims in a Xero organisation<br/>Allows you to retrieve expense claims<br/>Allows you to update details on an expense claim |

## GET Expense Claims

The following elements are returned in the Expense Claims response

| Field | Description |
|-------|-------------|
| **ExpenseClaimID** | Xero identifier |
| **Status** | See [Expense Claim Status Codes](#expense-claim-status-codes) |
| **User** | See [Users](/documentation/api/accounting/users) |
| **Receipts** | See [Receipts](/documentation/api/accounting/receipts) |
| **UpdatedDateUTC** | Last modified date UTC format |
| **Total** | The total of the expense claim |
| **AmountDue** | The amount due on the expense claim |
| **AmountPaid** | The amount paid on the expense claim |
| **PaymentDueDate** | The date when the expense claim is due – YYYY-MM-DD |
| **ReportingDate** | The date the expense claim will be reported – YYYY-MM-DD |

### Optional parameters for GET Expense Claims

| Field | Description |
|-------|-------------|
| **ExpenseClaimID** | The Xero identifier for an expense claim – specified as a string following the endpoint name |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |

## POST Expense Claims

You can create new expense claims by POST to the expense claims endpoint.

### Required fields for POST Expense Claims

| Field | Description |
|-------|-------------|
| **User** | See [Users](/documentation/api/accounting/users) |
| **Receipts** | See [Receipts](/documentation/api/accounting/receipts) |

## PUT Expense Claims

You can update expense claims by PUT to the expense claims endpoint.

## Expense Claim Status Codes

| Value | Description |
|-------|-------------|
| **SUBMITTED** | Submitted for approval |
| **AUTHORISED** | Approved expense claims awaiting payment |
| **PAID** | Expense claims with payments applied |
| **DELETED** | Expense claims that are deleted |
| **VOIDED** | Expense claims that are voided |