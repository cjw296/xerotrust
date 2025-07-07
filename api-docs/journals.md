# Journals

[Try in API Explorer](https://api-explorer.xero.com/accounting/journals)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/Journals](https://api.xero.com/api.xro/2.0/Journals) |
| **Methods Supported** | [GET](#get-journals) |
| **Description** | Allows you to retrieve journals for a Xero organisation |

## GET Journals

The following elements are returned in the Journals response

| Field | Description |
|-------|-------------|
| **JournalID** | Xero identifier |
| **JournalDate** | The date of the journal – YYYY-MM-DD |
| **JournalNumber** | Xero generated journal number |
| **CreatedDateUTC** | Date journal was created – UTC format |
| **Reference** | Reference for the journal |
| **SourceID** | The identifier for the source transaction |
| **SourceType** | See [Source Types](#source-types) |
| **JournalLines** | See [Journal Lines](#journal-lines) |

### Optional parameters for GET Journals

| Field | Description |
|-------|-------------|
| **JournalID** | The Xero identifier for a journal – specified as a string following the endpoint name |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |
| **offset** | Offset by a number of records |
| **paymentsOnly** | Filter to retrieve journals on a cash basis |

## Source Types

| Value | Description |
|-------|-------------|
| **ACCPAY** | Accounts Payable |
| **ACCREC** | Accounts Receivable |
| **CASHREC** | Cash Received |
| **CASHPAID** | Cash Paid |
| **TRANSFER** | Transfer |
| **ARPREPAYMENT** | Accounts Receivable Prepayment |
| **APPREPAYMENT** | Accounts Payable Prepayment |
| **AROVERPAYMENT** | Accounts Receivable Overpayment |
| **APOVERPAYMENT** | Accounts Payable Overpayment |
| **EXPCLAIM** | Expense Claim |
| **EXPPAYMENT** | Expense Payment |
| **MANJOURNAL** | Manual Journal |
| **PAYSLIP** | Payslip |
| **WAGEPAYABLES** | Wage Payables |
| **INTEGRATEDPAYROLLPE** | Integrated Payroll PE |
| **INTEGRATEDPAYROLLPT** | Integrated Payroll PT |
| **INTEGRATEDPAYROLLPTPAYMENT** | Integrated Payroll PT Payment |
| **SUPERPAYMENT** | Super Payment |
| **PAYMENTRUN** | Payment Run |
| **TRANSFER** | Transfer |

## Journal Lines

| Field | Description |
|-------|-------------|
| **JournalLineID** | Xero identifier for journal line |
| **AccountID** | See [Accounts](/documentation/api/accounting/accounts) |
| **AccountCode** | See [Accounts](/documentation/api/accounting/accounts) |
| **AccountType** | See [Account Types](/documentation/api/accounting/types#accounts) |
| **AccountName** | See [Accounts](/documentation/api/accounting/accounts) |
| **Description** | The description from the source transaction line item |
| **NetAmount** | Net amount of journal line |
| **GrossAmount** | Gross amount of journal line |
| **TaxAmount** | Total tax on a journal line |
| **TaxType** | See [Tax Types](/documentation/api/accounting/types#tax-rates) |
| **TaxName** | See [Tax Types](/documentation/api/accounting/types#tax-rates) |
| **TrackingCategories** | See [Tracking Categories](/documentation/api/accounting/trackingcategories) |