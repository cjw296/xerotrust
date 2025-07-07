# Reports

[Try in API Explorer](https://api-explorer.xero.com/accounting/reports)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/Reports](https://api.xero.com/api.xro/2.0/Reports) |
| **Methods Supported** | [GET](#get-reports) |
| **Description** | Allows you to retrieve reports for a Xero organisation |

## GET Reports

The following reports are available in the Xero API:

### Financial Reports

| Report | URL | Description |
|--------|-----|-------------|
| **Profit and Loss** | `/Reports/ProfitAndLoss` | Profit and Loss report |
| **Balance Sheet** | `/Reports/BalanceSheet` | Balance Sheet report |
| **Trial Balance** | `/Reports/TrialBalance` | Trial Balance report |
| **Bank Summary** | `/Reports/BankSummary` | Bank Summary report |
| **Executive Summary** | `/Reports/ExecutiveSummary` | Executive Summary report |

### Activity Reports

| Report | URL | Description |
|--------|-----|-------------|
| **Aged Receivables by Contact** | `/Reports/AgedReceivablesByContact` | Aged Receivables by Contact report |
| **Aged Payables by Contact** | `/Reports/AgedPayablesByContact` | Aged Payables by Contact report |
| **Budget Summary** | `/Reports/BudgetSummary` | Budget Summary report |
| **Bank Statement** | `/Reports/BankStatement` | Bank Statement report |

### Tax Reports

| Report | URL | Description |
|--------|-----|-------------|
| **GST Report** | `/Reports/TaxReport` | GST/Tax report |

### Optional parameters for GET Reports

| Field | Description |
|-------|-------------|
| **date** | The date for the report – YYYY-MM-DD |
| **fromDate** | The from date for the report – YYYY-MM-DD |
| **toDate** | The to date for the report – YYYY-MM-DD |
| **periods** | The number of periods for the report |
| **timeframe** | The timeframe for the report |
| **trackingCategoryID** | The tracking category ID for the report |
| **trackingCategoryID2** | The second tracking category ID for the report |
| **trackingOptionID** | The tracking option ID for the report |
| **trackingOptionID2** | The second tracking option ID for the report |
| **standardLayout** | Return the standard layout for the report |
| **paymentsOnly** | Return cash only data for the report |

## Report Structure

All reports return data in the following structure:

| Field | Description |
|-------|-------------|
| **ReportID** | The ID of the report |
| **ReportName** | The name of the report |
| **ReportType** | The type of the report |
| **ReportTitles** | Array of report titles |
| **ReportDate** | The date the report was generated |
| **UpdatedDateUTC** | The date the report was last updated |
| **Rows** | Array of report rows containing the data |

## Report Row Types

| Type | Description |
|------|-------------|
| **Header** | Header row |
| **Section** | Section divider |
| **Row** | Data row |
| **SummaryRow** | Summary row |

## Timeframe Options

| Value | Description |
|-------|-------------|
| **MONTH** | Monthly |
| **QUARTER** | Quarterly |
| **YEAR** | Yearly |