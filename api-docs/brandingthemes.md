# Branding Themes

[Try in API Explorer](https://api-explorer.xero.com/accounting/brandingthemes)

## Overview

| Property | Description |
|----------|-------------|
| **URL** | [https://api.xero.com/api.xro/2.0/BrandingThemes](https://api.xero.com/api.xro/2.0/BrandingThemes) |
| **Methods Supported** | [GET](#get-brandingthemes) |
| **Description** | Allows you to retrieve branding themes for a Xero organisation |

## GET Branding Themes

The following elements are returned in the Branding Themes response

| Field | Description |
|-------|-------------|
| **BrandingThemeID** | Xero identifier |
| **Name** | Name of the branding theme |
| **SortOrder** | Integer – ranked order of branding theme |
| **CreatedDateUTC** | UTC timestamp of creation date of branding theme |

### Optional parameters for GET Branding Themes

| Field | Description |
|-------|-------------|
| **BrandingThemeID** | The Xero identifier for a branding theme – specified as a string following the endpoint name |