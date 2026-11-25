# 桌序 Desk Order

面向美国市场的双语桌面用品商店。项目包含 Shopify 原生主题、可独立运行的本地模拟商店和商品上架资料。

## 本地运行

需要 Python 3.8 或以上版本，无第三方 Python 依赖。运行 `python store/launch.py`，或在 Windows 双击「启动桌序商店.cmd」。访问 [英文首页](http://127.0.0.1:18764/en/) 或 [中文首页](http://127.0.0.1:18764/)。

本地体验支持按规格加购、模拟支付、库存更新、发货和退货退款。在页脚进入商家工作台。该服务仅监听本机回环地址，订单和会话保存在本地 SQLite 数据库。运行 `python store/verify.py` 可在临时数据库中验证交易与 SEO 路由。

## Shopify 主题

`desk-order/` 包含基于 Dawn 的 Liquid 主题源码，其使用条件见 [Dawn 许可证](desk-order/LICENSE.md)。可将 `Desk-Order-Shopify.zip` 上传至主题库，并参考[店铺接入说明](店铺接入说明.md)配置。美国市场商品草稿及素材见「美国市场上架资料.zip」。商品图、售价及配送条款均用于模拟展示，正式销售前需核验。
