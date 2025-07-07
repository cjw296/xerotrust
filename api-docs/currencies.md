# Currencies

[Try in API Explorer](https://api-explorer.xero.com/accounting/currencies)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/Currencies](https://api.xero.com/api.xro/2.0/Currencies) |
| **Methods Supported** | [GET](#get-currencies), [PUT](#put-currencies) |
| **Description** | Allows you to retrieve currencies for a Xero organisation<br/>Allows you to update details on a currency |

## GET Currencies

The following elements are returned in the Currencies response

| Field | Description |
|-------|-------------|
| **Code** | 3 letter alpha code for the currency – see [list of currency codes](http://en.wikipedia.org/wiki/ISO_4217) |
| **Description** | Name of Currency |

### Optional parameters for GET Currencies

| Field | Description |
|-------|-------------|
| **Where** | Filter by an any element |
| **order** | Order by any element returned |

## PUT Currencies

You can update currencies by PUT to the currencies endpoint. Only the base currency can be updated.

### Required fields for PUT Currencies

| Field | Description |
|-------|-------------|
| **Code** | 3 letter alpha code for the currency |
| **Description** | Name of Currency |