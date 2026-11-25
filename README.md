# Desk Order | 桌序

**A bilingual Shopify brand storefront for the US desk accessories market, with a deployable theme, an importable product catalog, and international ecommerce SEO.**

![Desk Order desk accessories collection](store/assets/desk-editorial.jpg)

## English

Desk Order is an English and Simplified Chinese storefront for desk accessories. Merchants can upload the theme to Shopify, import their catalog, and manage pricing, inventory, and publishing from Shopify Admin. A clean visual design brings together workspace imagery, close-up product views, and size comparisons in inches so shoppers can judge how each piece will fit their desk.

**International SEO shapes the catalog.** Collection pages serve shoppers looking for desk mats, organizers, or stands. Product pages address searches for specific models and sizes. The buying guide connects questions such as “What size desk mat fits my desk?” to the relevant product. Language-specific URLs, `hreflang`, and canonical links identify each page and its language alternatives. Structured data uses `ProductGroup` and `Offer` to describe variants, prices, and availability, giving search engines the information they need to distinguish sizes within a product family.

## 中文介绍

**面向美国市场的双语 Shopify 品牌店，集成可部署主题、商品目录与国际化电商 SEO，覆盖从商品搜索、规格比较到下单的完整购物路径。**

**Desk Order｜桌序** 是为美国桌面用品市场打造的中英双语 Shopify 品牌店。商家可将主题直接部署至 Shopify，导入商品目录，并在后台管理定价、库存与商品发布。店面采用简洁统一的视觉语言，通过场景摄影、产品细节图和英制尺寸对比，帮助买家判断一件商品放在自己的桌面上是否合适。

**国际化 SEO 贯穿商品目录的设计。** 品类页承接桌垫、收纳和支架等品类搜索，商品页承接具体款式与规格查询，选购指南则把“我的桌子适合多大的桌垫”这样的购买问题连接到对应商品。中英文独立 URL、`hreflang` 和规范网址明确页面的语言与索引关系；`ProductGroup` 与 `Offer` 结构化数据进一步标注型号、价格及库存，让搜索引擎能够识别同一商品下的不同规格。买家从搜索结果进入店铺，就能在与需求匹配的页面上继续比较和选购。

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
