# History and Notes

[Try in API Explorer](https://api-explorer.xero.com/accounting/historyandnotes)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/{Endpoint}/{Identifier}/History](https://api.xero.com/api.xro/2.0/{Endpoint}/{Identifier}/History) |
| **Methods Supported** | [GET](#get-historyandnotes), [PUT](#put-historyandnotes) |
| **Description** | Allows you to retrieve history and notes for various entities<br/>Allows you to create history and notes for various entities |

## GET History and Notes

The following elements are returned in the History and Notes response

| Field | Description |
|-------|-------------|
| **Changes** | Details of changes made to the entity |
| **DateUTC** | The date and time of the change in UTC format |
| **User** | The user who made the change |
| **Details** | Additional details about the change |

### Supported Endpoints

You can retrieve history and notes for the following endpoints:

| Endpoint | URL Pattern |
|----------|-------------|
| **Contacts** | `/Contacts/{ContactID}/History` |
| **Invoices** | `/Invoices/{InvoiceID}/History` |
| **CreditNotes** | `/CreditNotes/{CreditNoteID}/History` |
| **BankTransactions** | `/BankTransactions/{BankTransactionID}/History` |
| **BankTransfers** | `/BankTransfers/{BankTransferID}/History` |
| **Receipts** | `/Receipts/{ReceiptID}/History` |
| **PurchaseOrders** | `/PurchaseOrders/{PurchaseOrderID}/History` |
| **Quotes** | `/Quotes/{QuoteID}/History` |

### Optional parameters for GET History and Notes

| Field | Description |
|-------|-------------|
| **Identifier** | The Xero identifier for the entity |

## PUT History and Notes

You can create new history and notes by PUT to the history endpoint.

### Required fields for PUT History and Notes

| Field | Description |
|-------|-------------|
| **Details** | The details of the history note |

### Example Usage

To add a note to a contact:

```
PUT /api.xro/2.0/Contacts/{ContactID}/History
{
  "HistoryRecords": [
    {
      "Details": "This is a note about the contact"
    }
  ]
}
```

## History Record Types

| Type | Description |
|------|-------------|
| **Created** | Entity was created |
| **Updated** | Entity was updated |
| **Deleted** | Entity was deleted |
| **Emailed** | Entity was emailed |
| **Note** | Manual note added |
| **Attachment** | Attachment was added |