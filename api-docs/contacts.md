# Contacts

[Try in API Explorer](https://api-explorer.xero.com/accounting/contacts)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/Contacts](https://api.xero.com/api.xro/2.0/Contacts) |
| **Methods Supported** | [GET](#get-contacts), [PUT](#put-contacts), [POST](#post-contacts) |
| **Description** | Allows you to create individual contacts in a Xero organisation<br/>Allows you to retrieve contacts<br/>Allows you to update details on a contact<br/>Allows you to attach files to a contact |

## GET Contacts

The following elements are returned in the Contacts response

| Field | Description |
|-------|-------------|
| **ContactID** | Xero identifier |
| **ContactNumber** | A user defined contact number |
| **AccountNumber** | A user defined account number |
| **ContactStatus** | See [Contact Status Codes](#contact-status-codes) |
| **Name** | Full name of contact/organisation |
| **FirstName** | First name of contact person |
| **LastName** | Last name of contact person |
| **CompanyNumber** | Company registration number |
| **EmailAddress** | Email address of contact person |
| **ContactPersons** | See [Contact Persons](#contact-persons) |
| **BankAccountDetails** | Bank account number of contact |
| **TaxNumber** | Tax number of contact |
| **AccountsReceivableTaxType** | See [Tax Types](/documentation/api/accounting/types#tax-rates) |
| **AccountsPayableTaxType** | See [Tax Types](/documentation/api/accounting/types#tax-rates) |
| **Addresses** | See [Addresses](#addresses) |
| **Phones** | See [Phones](#phones) |
| **IsSupplier** | Boolean to indicate if contact is supplier |
| **IsCustomer** | Boolean to indicate if contact is customer |
| **DefaultCurrency** | Default currency for the contact |
| **XeroNetworkKey** | Store XeroNetworkKey for contacts |
| **SalesDefaultAccountCode** | The default sales account code for contacts |
| **PurchasesDefaultAccountCode** | The default purchases account code for contacts |
| **SalesTrackingCategories** | See [Sales Tracking Categories](#sales-tracking-categories) |
| **PurchasesTrackingCategories** | See [Purchases Tracking Categories](#purchases-tracking-categories) |
| **TrackingCategoryName** | The name of the tracking category |
| **TrackingCategoryOption** | The option of the tracking category |
| **PaymentTerms** | See [Payment Terms](#payment-terms) |
| **UpdatedDateUTC** | Last modified date UTC format |
| **ContactGroups** | See [Contact Groups](/documentation/api/accounting/contactgroups) |
| **Website** | Website address for contact |
| **BrandingTheme** | See [Branding Themes](/documentation/api/accounting/brandingthemes) |
| **BatchPayments** | See [Batch Payments](/documentation/api/accounting/batchpayments) |
| **Discount** | The default discount rate for the contact |
| **Balances** | See [Balances](#balances) |
| **HasAttachments** | Boolean to indicate if contact has an attachment |
| **HasValidationErrors** | Boolean to indicate if contact has validation errors |
| **ValidationErrors** | See [Validation Errors](#validation-errors) |

### Optional parameters for GET Contacts

| Field | Description |
|-------|-------------|
| **ContactID** | The Xero identifier for a contact – specified as a string following the endpoint name |
| **Modified After** | The ModifiedAfter filter is actually an HTTP header: '**If-Modified-Since**'. A UTC timestamp (yyyy-mm-ddThh:mm:ss) |
| **Where** | Filter by an any element |
| **order** | Order by any element returned |
| **IDs** | Filter by a comma-separated list of ContactIDs |
| **page** | e.g. page=1 – Up to 100 contacts will be returned in a single API call |
| **includeArchived** | e.g. includeArchived=true – Contacts with a status of ARCHIVED will be included |

## POST Contacts

You can create new contacts by POST to the contacts endpoint.

### Required fields for POST Contacts

| Field | Description |
|-------|-------------|
| **Name** | Full name of contact/organisation |

## PUT Contacts

You can update contacts by PUT to the contacts endpoint.

## Contact Status Codes

| Value | Description |
|-------|-------------|
| **ACTIVE** | Active contact |
| **ARCHIVED** | Archived contact |
| **GDPRREQUEST** | GDPR request contact |

## Contact Persons

| Field | Description |
|-------|-------------|
| **FirstName** | First name of contact person |
| **LastName** | Last name of contact person |
| **EmailAddress** | Email address of contact person |
| **IncludeInEmails** | Boolean to indicate whether contact person should be included on emails |

## Addresses

| Field | Description |
|-------|-------------|
| **AddressType** | See [Address Types](#address-types) |
| **AddressLine1** | Address line 1 |
| **AddressLine2** | Address line 2 |
| **AddressLine3** | Address line 3 |
| **AddressLine4** | Address line 4 |
| **City** | City |
| **Region** | Region |
| **PostalCode** | Postal code |
| **Country** | Country |
| **AttentionTo** | Attention to |

## Phones

| Field | Description |
|-------|-------------|
| **PhoneType** | See [Phone Types](#phone-types) |
| **PhoneNumber** | Phone number |
| **PhoneAreaCode** | Phone area code |
| **PhoneCountryCode** | Phone country code |

## Address Types

| Value | Description |
|-------|-------------|
| **POBOX** | PO Box |
| **STREET** | Street |
| **DELIVERY** | Delivery |

## Phone Types

| Value | Description |
|-------|-------------|
| **DEFAULT** | Default |
| **DDI** | DDI |
| **MOBILE** | Mobile |
| **FAX** | Fax |

## Sales Tracking Categories

| Field | Description |
|-------|-------------|
| **TrackingCategoryName** | The name of the tracking category |
| **TrackingOptionName** | The name of the tracking option |

## Purchases Tracking Categories

| Field | Description |
|-------|-------------|
| **TrackingCategoryName** | The name of the tracking category |
| **TrackingOptionName** | The name of the tracking option |

## Payment Terms

| Field | Description |
|-------|-------------|
| **Bills** | See [Bills Payment Terms](#bills-payment-terms) |
| **Sales** | See [Sales Payment Terms](#sales-payment-terms) |

## Bills Payment Terms

| Field | Description |
|-------|-------------|
| **Day** | Day of the month |
| **Type** | See [Payment Term Types](#payment-term-types) |

## Sales Payment Terms

| Field | Description |
|-------|-------------|
| **Day** | Day of the month |
| **Type** | See [Payment Term Types](#payment-term-types) |

## Payment Term Types

| Value | Description |
|-------|-------------|
| **DAYSAFTERBILLDATE** | Days after bill date |
| **DAYSAFTERBILLMONTH** | Days after bill month |
| **OFCURRENTMONTH** | Of current month |
| **OFFOLLOWINGMONTH** | Of following month |

## Balances

| Field | Description |
|-------|-------------|
| **AccountsReceivable** | See [Accounts Receivable](#accounts-receivable) |
| **AccountsPayable** | See [Accounts Payable](#accounts-payable) |

## Accounts Receivable

| Field | Description |
|-------|-------------|
| **Outstanding** | Outstanding amount |
| **Overdue** | Overdue amount |

## Accounts Payable

| Field | Description |
|-------|-------------|
| **Outstanding** | Outstanding amount |
| **Overdue** | Overdue amount |

## Validation Errors

| Field | Description |
|-------|-------------|
| **Message** | Validation error message |