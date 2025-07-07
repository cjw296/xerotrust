# Budgets

[Try in API Explorer](https://api-explorer.xero.com/accounting/budgets)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/Budgets](https://api.xero.com/api.xro/2.0/Budgets) |
| **Methods Supported** | [GET](#get-budgets) |
| **Description** | Allows you to retrieve budgets for a Xero organisation |

## GET Budgets

The following elements are returned in the Budgets response

| Field | Description |
|-------|-------------|
| **BudgetID** | Xero identifier |
| **Type** | See [Budget Types](#budget-types) |
| **Description** | The description of the budget |
| **UpdatedDateUTC** | Last modified date UTC format |
| **BudgetLines** | See [Budget Lines](#budget-lines) |
| **Tracking** | See [Tracking Categories](/documentation/api/accounting/trackingcategories) |

### Optional parameters for GET Budgets

| Field | Description |
|-------|-------------|
| **BudgetID** | The Xero identifier for a budget – specified as a string following the endpoint name |
| **IDs** | Filter by a comma-separated list of BudgetIDs |
| **DateFrom** | Filter by start date |
| **DateTo** | Filter by end date |

## Budget Types

| Value | Description |
|-------|-------------|
| **OVERALL** | Overall budget |

## Budget Lines

| Field | Description |
|-------|-------------|
| **AccountID** | Xero identifier for Account |
| **AccountCode** | Account code |
| **BudgetBalances** | See [Budget Balances](#budget-balances) |

## Budget Balances

| Field | Description |
|-------|-------------|
| **Period** | The period of the budget balance |
| **Amount** | The amount of the budget balance |
| **UnitAmount** | The unit amount of the budget balance |
| **UnitType** | The unit type of the budget balance |