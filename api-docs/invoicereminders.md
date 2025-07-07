# Invoice Reminders

[Try in API Explorer](https://api-explorer.xero.com/accounting/invoicereminders)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/InvoiceReminders](https://api.xero.com/api.xro/2.0/InvoiceReminders) |
| **Methods Supported** | [GET](#get-invoicereminders) |
| **Description** | Allows you to retrieve invoice reminders for a Xero organisation |

## GET Invoice Reminders

The following elements are returned in the Invoice Reminders response

| Field | Description |
|-------|-------------|
| **Enabled** | Boolean to indicate if invoice reminders are enabled |

### Invoice Reminder Settings

| Field | Description |
|-------|-------------|
| **DefaultReminderSettings** | See [Default Reminder Settings](#default-reminder-settings) |

## Default Reminder Settings

| Field | Description |
|-------|-------------|
| **FirstReminderDays** | Number of days after due date for first reminder |
| **SecondReminderDays** | Number of days after due date for second reminder |
| **ThirdReminderDays** | Number of days after due date for third reminder |