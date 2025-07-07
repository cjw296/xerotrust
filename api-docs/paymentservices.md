# Payment Services

[Try in API Explorer](https://api-explorer.xero.com/accounting/paymentservices)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/PaymentServices](https://api.xero.com/api.xro/2.0/PaymentServices) |
| **Methods Supported** | [GET](#get-paymentservices), [POST](#post-paymentservices) |
| **Description** | Allows you to retrieve payment services for a Xero organisation<br/>Allows you to create payment services |

## GET Payment Services

The following elements are returned in the Payment Services response

| Field | Description |
|-------|-------------|
| **PaymentServiceID** | Xero identifier |
| **PaymentServiceName** | Name of the payment service |
| **PaymentServiceUrl** | URL of the payment service |
| **PayNowText** | The text displayed on the Pay Now button in invoices |
| **PaymentServiceType** | See [Payment Service Types](#payment-service-types) |

### Optional parameters for GET Payment Services

| Field | Description |
|-------|-------------|
| **PaymentServiceID** | The Xero identifier for a payment service – specified as a string following the endpoint name |

## POST Payment Services

You can create new payment services by POST to the payment services endpoint.

### Required fields for POST Payment Services

| Field | Description |
|-------|-------------|
| **PaymentServiceName** | Name of the payment service |
| **PaymentServiceUrl** | URL of the payment service |
| **PayNowText** | The text displayed on the Pay Now button in invoices |

## Payment Service Types

| Value | Description |
|-------|-------------|
| **PAYNOWBUTTON** | Pay Now Button |
| **CUSTOM** | Custom |