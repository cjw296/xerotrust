# Organisation

[Try in API Explorer](https://api-explorer.xero.com/accounting/organisation)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/Organisation](https://api.xero.com/api.xro/2.0/Organisation) |
| **Methods Supported** | [GET](#get-organisation) |
| **Description** | Allows you to retrieve organisation details for a Xero organisation |

## GET Organisation

The following elements are returned in the Organisation response

| Field | Description |
|-------|-------------|
| **OrganisationID** | Xero identifier |
| **Name** | Display name of organisation shown in Xero |
| **LegalName** | Organisation name shown on reports |
| **PaysTax** | Boolean to describe if organisation is registered with a local tax authority |
| **Version** | See [Version Types](#version-types) |
| **OrganisationType** | See [Organisation Types](#organisation-types) |
| **BaseCurrency** | Default currency for organisation |
| **CountryCode** | Country code for organisation |
| **IsDemoCompany** | Boolean to describe if organisation is a demo company |
| **OrganisationStatus** | See [Organisation Status](#organisation-status) |
| **RegistrationNumber** | Registration number of the organisation |
| **TaxNumber** | Tax number of the organisation |
| **FinancialYearEndDay** | The day of the financial year end |
| **FinancialYearEndMonth** | The month of the financial year end |
| **SalesTaxBasis** | See [Sales Tax Basis](#sales-tax-basis) |
| **SalesTaxPeriod** | See [Sales Tax Period](#sales-tax-period) |
| **DefaultSalesTax** | Default sales tax type |
| **DefaultPurchasesTax** | Default purchases tax type |
| **PeriodLockDate** | Period lock date |
| **EndOfYearLockDate** | End of year lock date |
| **CreatedDateUTC** | Timestamp when the organisation was created in Xero |
| **Timezone** | Timezone for the organisation |
| **OrganisationEntityType** | See [Organisation Entity Types](#organisation-entity-types) |
| **ShortCode** | A unique identifier for the organisation |
| **Class** | See [Organisation Classes](#organisation-classes) |
| **Edition** | See [Organisation Editions](#organisation-editions) |
| **LineOfBusiness** | Description of the line of business |
| **Addresses** | See [Addresses](#addresses) |
| **Phones** | See [Phones](#phones) |
| **ExternalLinks** | See [External Links](#external-links) |
| **PaymentTerms** | See [Payment Terms](#payment-terms) |

## Version Types

| Value | Description |
|-------|-------------|
| **AU** | Australian version |
| **NZ** | New Zealand version |
| **GLOBAL** | Global version |
| **UK** | UK version |
| **US** | US version |

## Organisation Types

| Value | Description |
|-------|-------------|
| **COMPANY** | Company |
| **CHARITY** | Charity |
| **CLUBSOCIETY** | Club/Society |
| **PARTNERSHIP** | Partnership |
| **PRACTICE** | Practice |
| **PERSON** | Person |
| **SOLETRADER** | Sole Trader |
| **TRUST** | Trust |
| **OTHER** | Other |

## Organisation Status

| Value | Description |
|-------|-------------|
| **ACTIVE** | Active organisation |
| **INACTIVE** | Inactive organisation |

## Sales Tax Basis

| Value | Description |
|-------|-------------|
| **PAYMENTS** | Payments basis |
| **INVOICE** | Invoice basis |
| **NONE** | None |
| **CASH** | Cash basis |
| **ACCRUAL** | Accrual basis |

## Sales Tax Period

| Value | Description |
|-------|-------------|
| **MONTHLY** | Monthly |
| **QUARTERLY** | Quarterly |
| **ANNUALLY** | Annually |
| **ONEMONTHS** | One month |
| **TWOMONTHS** | Two months |
| **SIXMONTHS** | Six months |

## Organisation Entity Types

| Value | Description |
|-------|-------------|
| **COMPANY** | Company |
| **CHARITY** | Charity |
| **CLUBSOCIETY** | Club/Society |
| **PARTNERSHIP** | Partnership |
| **PRACTICE** | Practice |
| **PERSON** | Person |
| **SOLETRADER** | Sole Trader |
| **TRUST** | Trust |
| **OTHER** | Other |

## Organisation Classes

| Value | Description |
|-------|-------------|
| **DEMO** | Demo organisation |
| **TRIAL** | Trial organisation |
| **STARTER** | Starter organisation |
| **STANDARD** | Standard organisation |
| **PREMIUM** | Premium organisation |

## Organisation Editions

| Value | Description |
|-------|-------------|
| **BUSINESS** | Business edition |
| **PARTNER** | Partner edition |

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

## External Links

| Field | Description |
|-------|-------------|
| **LinkType** | See [Link Types](#link-types) |
| **Url** | URL link |
| **Description** | Description of the link |

## Payment Terms

| Field | Description |
|-------|-------------|
| **Bills** | See [Bills Payment Terms](#bills-payment-terms) |
| **Sales** | See [Sales Payment Terms](#sales-payment-terms) |

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

## Link Types

| Value | Description |
|-------|-------------|
| **Website** | Website link |
| **Facebook** | Facebook link |
| **Twitter** | Twitter link |
| **GooglePlus** | Google+ link |
| **LinkedIn** | LinkedIn link |

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