# Types

## Overview

This section contains reference information for various data types used throughout the Xero Accounting API.

## Line Amount Types

| Value | Description |
|-------|-------------|
| **Exclusive** | Line amounts are tax exclusive |
| **Inclusive** | Line amounts are tax inclusive |
| **NoTax** | Line amounts have no tax |

## Line Items

| Field | Description |
|-------|-------------|
| **LineItemID** | Xero identifier – only returned for ACCPAY and ACCREC invoice types |
| **Description** | Description needs to be at least 1 char long |
| **Quantity** | LineItem Quantity |
| **UnitAmount** | Lineitem unit amount |
| **ItemCode** | See [Items](/documentation/api/accounting/items) |
| **AccountCode** | See [Accounts](/documentation/api/accounting/accounts) |
| **TaxType** | The tax type applied to the line item |
| **TaxAmount** | The tax amount is auto calculated as a percentage of the line amount (see below) based on the tax rate |
| **LineAmount** | If you wish to omit either the Quantity or UnitAmount you can provide a LineAmount and Xero will calculate the missing amount |
| **TrackingCategories** | See [Tracking Categories](/documentation/api/accounting/trackingcategories) |
| **DiscountRate** | Percentage discount being applied to a line item (only supported on ACCREC invoices) |
| **DiscountAmount** | Discount amount being applied to a line item |
| **RepeatingInvoiceID** | Xero identifier for repeating invoice |

## Account Types

| Value | Description |
|-------|-------------|
| **BANK** | Bank account |
| **CURRENT** | Current asset |
| **CURRLIAB** | Current liability |
| **DEPRECIATN** | Depreciation |
| **DIRECTCOSTS** | Direct costs |
| **EQUITY** | Equity |
| **EXPENSE** | Expense |
| **FIXED** | Fixed asset |
| **INVENTORY** | Inventory |
| **LIABILITY** | Liability |
| **NONCURRENT** | Non-current asset |
| **OTHERINCOME** | Other income |
| **OVERHEADS** | Overheads |
| **PREPAYMENT** | Prepayment |
| **REVENUE** | Revenue |
| **SALES** | Sales |
| **TERMLIAB** | Term liability |
| **PAYGLIABILITY** | Payroll liability |
| **SUPERANNUATIONEXPENSE** | Superannuation expense |
| **SUPERANNUATIONLIABILITY** | Superannuation liability |
| **WAGESEXPENSE** | Wages expense |
| **WAGESPAYABLELIABILITY** | Wages payable liability |

## Account Status Codes

| Value | Description |
|-------|-------------|
| **ACTIVE** | Active account |
| **ARCHIVED** | Archived account |
| **DELETED** | Deleted account |

## Bank Account Types

| Value | Description |
|-------|-------------|
| **BANK** | Bank account |
| **CREDITCARD** | Credit card account |
| **PAYPAL** | PayPal account |

## System Account Types

| Value | Description |
|-------|-------------|
| **DEBTORS** | Accounts receivable |
| **CREDITORS** | Accounts payable |
| **BASECURRENCY** | Base currency gains/losses |
| **CURRENCYEXCHANGEDIFFERENCE** | Currency exchange difference |
| **GST** | GST account |
| **GSTONIMPORTS** | GST on imports |
| **HISTORIC** | Historical adjustment |
| **REALISEDCURRENCYGAIN** | Realised currency gain |
| **RETAINEDEARNINGS** | Retained earnings |
| **ROUNDING** | Rounding account |
| **TRACKINGTRANSFERS** | Tracking transfers |
| **UNPAIDEXPCLM** | Unpaid expense claims |
| **UNREALISEDCURRENCYGAIN** | Unrealised currency gain |
| **WAGEPAYABLES** | Wage payables |

## Account Class Types

| Value | Description |
|-------|-------------|
| **ASSET** | Asset |
| **EQUITY** | Equity |
| **EXPENSE** | Expense |
| **LIABILITY** | Liability |
| **REVENUE** | Revenue |

## Tax Rate Types

| Value | Description |
|-------|-------------|
| **INCLUSIVE** | Tax inclusive |
| **EXCLUSIVE** | Tax exclusive |
| **NONE** | No tax |
| **EXEMPTINPUT** | Exempt input |
| **EXEMPTOUTPUT** | Exempt output |
| **INPUTTAXED** | Input taxed |
| **BASEXCLUDED** | Base excluded |

## Currency Codes

The API supports ISO 4217 currency codes. Common examples:

| Code | Currency |
|------|----------|
| **AUD** | Australian Dollar |
| **CAD** | Canadian Dollar |
| **EUR** | Euro |
| **GBP** | British Pound |
| **JPY** | Japanese Yen |
| **NZD** | New Zealand Dollar |
| **SGD** | Singapore Dollar |
| **USD** | US Dollar |

## Date Formats

All dates in the API use the format: **YYYY-MM-DD**

Examples:
- `2023-12-25` (Christmas Day 2023)
- `2024-01-01` (New Year's Day 2024)

## Boolean Values

Boolean fields accept:
- `true` or `false`
- `1` or `0`
- Case insensitive

## Decimal Precision

- **Amounts**: Up to 4 decimal places
- **Quantities**: Up to 6 decimal places
- **Exchange Rates**: Up to 6 decimal places
- **Tax Rates**: Up to 4 decimal places

## String Lengths

| Field Type | Maximum Length |
|------------|----------------|
| **Names** | 255 characters |
| **Descriptions** | 4000 characters |
| **References** | 255 characters |
| **Codes** | 50 characters |

## Validation Rules

- All required fields must be provided
- String fields cannot exceed maximum lengths
- Numeric fields must be within valid ranges
- Date fields must be in correct format
- Boolean fields must be valid boolean values
- Currency codes must be valid ISO 4217 codes