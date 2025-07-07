# Employees

[Try in API Explorer](https://api-explorer.xero.com/accounting/employees)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/Employees](https://api.xero.com/api.xro/2.0/Employees) |
| **Methods Supported** | [GET](#get-employees), [PUT](#put-employees), [POST](#post-employees) |
| **Description** | Allows you to create individual employees in a Xero organisation<br/>Allows you to retrieve employees<br/>Allows you to update details on an employee |

## GET Employees

The following elements are returned in the Employees response

| Field | Description |
|-------|-------------|
| **EmployeeID** | Xero identifier |
| **Status** | See [Employee Status Codes](#employee-status-codes) |
| **FirstName** | First name of employee |
| **LastName** | Last name of employee |
| **ExternalLink** | See [External Links](#external-links) |
| **UpdatedDateUTC** | Last modified date UTC format |

### Optional parameters for GET Employees

| Field | Description |
|-------|-------------|
| **EmployeeID** | The Xero identifier for an employee – specified as a string following the endpoint name |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |

## POST Employees

You can create new employees by POST to the employees endpoint.

### Required fields for POST Employees

| Field | Description |
|-------|-------------|
| **FirstName** | First name of employee |
| **LastName** | Last name of employee |

## PUT Employees

You can update employees by PUT to the employees endpoint.

## Employee Status Codes

| Value | Description |
|-------|-------------|
| **ACTIVE** | Active employee |
| **DELETED** | Deleted employee |

## External Links

| Field | Description |
|-------|-------------|
| **LinkType** | See [Link Types](#link-types) |
| **Url** | URL link |
| **Description** | Description of the link |

## Link Types

| Value | Description |
|-------|-------------|
| **Website** | Website link |
| **Facebook** | Facebook link |
| **Twitter** | Twitter link |
| **GooglePlus** | Google+ link |
| **LinkedIn** | LinkedIn link |