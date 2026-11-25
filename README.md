# Desk Order

**A bilingual Shopify brand storefront for the US desk accessories market, with a deployable theme, an importable product catalog, and international ecommerce SEO.**

![Desk Order desk accessories collection](store/assets/desk-editorial.jpg)

Desk Order is an English and Simplified Chinese storefront for desk accessories. Merchants can upload the theme to Shopify, import their catalog, and manage pricing, inventory, and publishing from Shopify Admin. A clean visual design brings together workspace imagery, close-up product views, and size comparisons in inches so shoppers can judge how each piece will fit their desk.

**International SEO shapes the catalog.** Collection pages serve shoppers looking for desk mats, organizers, or stands. Product pages address searches for specific models and sizes. The buying guide connects questions such as “What size desk mat fits my desk?” to the relevant product. Language-specific URLs, `hreflang`, and canonical links identify each page and its language alternatives. Structured data uses `ProductGroup` and `Offer` to describe variants, prices, and availability, giving search engines the information they need to distinguish sizes within a product family.

## Run locally

Requires Python 3.8 or later. The demo uses the Python standard library and SQLite.

```sh
python store/launch.py
```

The launcher opens the English storefront in your browser. Switch to Chinese from the navigation. Choose a product to try checkout, then open the merchant dashboard in the footer to fulfill the order or process a return. Payments and shipping are simulated.

## Project

| Directory | Contents |
| --- | --- |
| [desk-order/](desk-order/) | Shopify Liquid theme based on Dawn, with configurable storefront sections and a desk mat size guide |
| [store/](store/) | Local storefront, product photography concepts, checkout and order management |
| [catalog/](catalog/) | Six draft products with US pricing and Shopify import fields |

## Shopify setup

Set the store currency to USD before importing [the product catalog](catalog/products.csv). Upload the theme by archiving the **contents** of the `desk-order` directory with `layout/`, `templates/` and `assets/` at the archive root. Enable English and Simplified Chinese in Shopify, then add product translations and configure shipping for your market. The theme inherits the [Dawn license](desk-order/LICENSE.md).

## Verification

```sh
python store/verify.py
```

The checks run against a temporary database and cover catalog routes, language alternates, product metadata, checkout, inventory and order fulfillment.
