# Tax Rates

[Try in API Explorer](https://api-explorer.xero.com/accounting/taxrates)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/TaxRates](https://api.xero.com/api.xro/2.0/TaxRates) |
| **Methods Supported** | [GET](#get-taxrates), [PUT](#put-taxrates), [POST](#post-taxrates), [DELETE](#delete-taxrates) |
| **Description** | Allows you to create individual tax rates in a Xero organisation<br/>Allows you to retrieve tax rates<br/>Allows you to update details on a tax rate<br/>Allows you to delete a tax rate |

## GET Tax Rates

The following elements are returned in the Tax Rates response

| Field | Description |
|-------|-------------|
| **Name** | Name of tax rate |
| **TaxType** | See [Tax Types](#tax-types) |
| **TaxComponents** | See [Tax Components](#tax-components) |
| **Status** | See [Tax Rate Status Codes](#tax-rate-status-codes) |
| **ReportTaxType** | See [Report Tax Types](#report-tax-types) |
| **CanApplyToAssets** | Boolean to describe if tax rate can be used on asset accounts |
| **CanApplyToEquity** | Boolean to describe if tax rate can be used on equity accounts |
| **CanApplyToExpenses** | Boolean to describe if tax rate can be used on expense accounts |
| **CanApplyToLiabilities** | Boolean to describe if tax rate can be used on liability accounts |
| **CanApplyToRevenue** | Boolean to describe if tax rate can be used on revenue accounts |
| **DisplayTaxRate** | Tax Rate (decimal to 4dp) e.g 12.5000 |
| **EffectiveRate** | Effective Tax Rate (decimal to 4dp) e.g 12.5000 |
| **UpdatedDateUTC** | Last modified date UTC format |

### Optional parameters for GET Tax Rates

| Field | Description |
|-------|-------------|
| **TaxType** | Filter by tax type |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |

## POST Tax Rates

You can create new tax rates by POST to the tax rates endpoint.

### Required fields for POST Tax Rates

| Field | Description |
|-------|-------------|
| **Name** | Name of tax rate |
| **TaxComponents** | See [Tax Components](#tax-components) |

## PUT Tax Rates

You can update tax rates by PUT to the tax rates endpoint.

## DELETE Tax Rates

You can delete tax rates by DELETE to the tax rates endpoint.

## Tax Types

| Value | Description |
|-------|-------------|
| **INPUT** | Input tax |
| **OUTPUT** | Output tax |
| **CAPEXINPUT** | Capital expenditure input tax |
| **CAPEXOUTPUT** | Capital expenditure output tax |
| **CAPEXSRINPUT** | Capital expenditure single rate input tax |
| **CAPEXSROUTPUT** | Capital expenditure single rate output tax |
| **ECACQUISITIONS** | EC acquisitions |
| **ECZRINPUT** | EC zero rate input |
| **ECZROUTPUT** | EC zero rate output |
| **ECZROUTPUTSERVICES** | EC zero rate output services |
| **EXEMPTEXPENSES** | Exempt expenses |
| **EXEMPTINPUT** | Exempt input |
| **EXEMPTOUTPUT** | Exempt output |
| **INPUTTAXONCAPIMPORTS** | Input tax on capital imports |
| **MOSSSALES** | MOSS sales |
| **NONE** | None |
| **NONEOUTPUT** | None output |
| **OUTPUTY** | Output Y |
| **RRINPUT** | Reverse charge input |
| **RROUTPUT** | Reverse charge output |
| **SRINPUT** | Standard rate input |
| **SROUTPUT** | Standard rate output |
| **TXESSINPUT** | TXESS input |
| **TXESSOUTPUT** | TXESS output |
| **TXPETINPUT** | TXPET input |
| **TXPETOUTPUT** | TXPET output |
| **TXREINPUT** | TXRE input |
| **TXREOUTPUT** | TXRE output |
| **ZERORATEDINPUT** | Zero rated input |
| **ZERORATEDOUTPUT** | Zero rated output |

## Tax Rate Status Codes

| Value | Description |
|-------|-------------|
| **ACTIVE** | Active tax rate |
| **DELETED** | Deleted tax rate |
| **ARCHIVED** | Archived tax rate |

## Report Tax Types

| Value | Description |
|-------|-------------|
| **INPUT** | Input |
| **OUTPUT** | Output |
| **CAPEXINPUT** | Capex Input |
| **CAPEXOUTPUT** | Capex Output |
| **CAPEXSRINPUT** | Capex SR Input |
| **CAPEXSROUTPUT** | Capex SR Output |
| **ECACQUISITIONS** | EC Acquisitions |
| **ECZRINPUT** | EC Zero Rate Input |
| **ECZROUTPUT** | EC Zero Rate Output |
| **ECZROUTPUTSERVICES** | EC Zero Rate Output Services |
| **EXEMPTEXPENSES** | Exempt Expenses |
| **EXEMPTINPUT** | Exempt Input |
| **EXEMPTOUTPUT** | Exempt Output |
| **INPUTTAXONCAPIMPORTS** | Input Tax on Cap Imports |
| **MOSSSALES** | MOSS Sales |
| **NONE** | None |
| **NONEOUTPUT** | None Output |
| **RRINPUT** | RR Input |
| **RROUTPUT** | RR Output |
| **SRINPUT** | SR Input |
| **SROUTPUT** | SR Output |
| **ZERORATEDINPUT** | Zero Rated Input |
| **ZERORATEDOUTPUT** | Zero Rated Output |

## Tax Components

| Field | Description |
|-------|-------------|
| **Name** | Name of Tax Component |
| **Rate** | Tax Rate (decimal to 4dp) e.g 12.5000 |
| **IsCompound** | Boolean to describe if the tax component is applied on top of other tax components |
| **IsNonRecoverable** | Boolean to describe if the tax component is non-recoverable |