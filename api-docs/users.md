# Users

[Try in API Explorer](https://api-explorer.xero.com/accounting/users)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/Users](https://api.xero.com/api.xro/2.0/Users) |
| **Methods Supported** | [GET](#get-users) |
| **Description** | Allows you to retrieve users for a Xero organisation |

## GET Users

The following elements are returned in the Users response

| Field | Description |
|-------|-------------|
| **UserID** | Xero identifier |
| **EmailAddress** | Email address of user |
| **FirstName** | First name of user |
| **LastName** | Last name of user |
| **UpdatedDateUTC** | Last modified date UTC format |
| **IsSubscriber** | Boolean to indicate if user is the subscriber |
| **OrganisationRole** | See [Organisation Roles](#organisation-roles) |

### Optional parameters for GET Users

| Field | Description |
|-------|-------------|
| **UserID** | The Xero identifier for a user – specified as a string following the endpoint name |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |

## Organisation Roles

| Value | Description |
|-------|-------------|
| **READONLY** | Read only access |
| **INVOICEONLY** | Invoice only access |
| **STANDARD** | Standard access |
| **FINANCIALADVISOR** | Financial advisor access |
| **MANAGEDCLIENT** | Managed client access |
| **CASHBOOKONLY** | Cashbook only access |

## User Permissions

Users have different levels of access based on their organisation role:

### Read Only
- View all data
- Cannot create, edit, or delete any records

### Invoice Only
- Create and edit invoices
- View contacts and items
- Cannot access financial reports

### Standard
- Full access to most features
- Cannot access organisation settings
- Cannot manage users

### Financial Advisor
- Full access to client data
- Can view financial reports
- Cannot access organisation settings

### Managed Client
- Limited access for client organisations
- View-only access to most data

### Cashbook Only
- Access to bank transactions only
- Cannot access invoices or other features

## User Status

| Value | Description |
|-------|-------------|
| **ACTIVE** | Active user |
| **ARCHIVED** | Archived user |

Note: User management (creating, updating, deleting users) is handled through the Xero web application and cannot be performed via the API.