# Contact Groups

[Try in API Explorer](https://api-explorer.xero.com/accounting/contactgroups)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/ContactGroups](https://api.xero.com/api.xro/2.0/ContactGroups) |
| **Methods Supported** | [GET](#get-contactgroups), [PUT](#put-contactgroups), [POST](#post-contactgroups), [DELETE](#delete-contactgroups) |
| **Description** | Allows you to create individual contact groups in a Xero organisation<br/>Allows you to retrieve contact groups<br/>Allows you to update details on a contact group<br/>Allows you to delete a contact group |

## GET Contact Groups

The following elements are returned in the Contact Groups response

| Field | Description |
|-------|-------------|
| **ContactGroupID** | Xero identifier |
| **Name** | The name of the contact group |
| **Status** | See [Contact Group Status Codes](#contact-group-status-codes) |
| **Contacts** | See [Contacts](/documentation/api/accounting/contacts) |

### Optional parameters for GET Contact Groups

| Field | Description |
|-------|-------------|
| **ContactGroupID** | The Xero identifier for a contact group – specified as a string following the endpoint name |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |

## POST Contact Groups

You can create new contact groups by POST to the contact groups endpoint.

### Required fields for POST Contact Groups

| Field | Description |
|-------|-------------|
| **Name** | The name of the contact group |

## PUT Contact Groups

You can update contact groups by PUT to the contact groups endpoint.

### PUT Contact Groups - Add Contact to Group

You can add a contact to a contact group by PUT to the contact groups endpoint.

### PUT Contact Groups - Remove Contact from Group

You can remove a contact from a contact group by PUT to the contact groups endpoint.

## DELETE Contact Groups

You can delete contact groups by DELETE to the contact groups endpoint.

## Contact Group Status Codes

| Value | Description |
|-------|-------------|
| **ACTIVE** | Active contact group |
| **DELETED** | Deleted contact group |