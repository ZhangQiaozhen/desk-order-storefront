"""Localized HTML and discovery documents for the local storefront."""
import us_market as us
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EN = json.loads((ROOT / 'en.json').read_text(encoding='utf-8'))
PUBLIC = ('/', '/shop', '/story', '/support',us.GUIDE,*us.COLLECTIONS)
TITLES = {'/':'桌面用品','/shop':'全部商品','/story':'品牌手记','/support':'顾客服务','/cart':'购物袋','/orders':'我的订单','/checkout':'确认订单','/merchant':'商家工作台'}
DESCRIPTIONS = {
    '/': ('探索桌序的桌面用品系列，从桌垫到收纳盘与显示器支架。','Discover desk mats, organizers and monitor stands from Desk Order.'),
    '/shop': ('浏览桌垫、收纳用品和支架，比较规格与价格。','Compare desk mats, organizers and stands by size, color and price.'),
    '/story': ('了解桌序如何为日常工作挑选桌面用品。','Read how Desk Order selects accessories for everyday work.'),
    '/support': ('了解模拟支付、订单查询和发货流程。','Find answers about demo checkout, order tracking and fulfillment.')
}

def localized(path, english):
    return ('/en' if english else '') + path

def sitemap(origin, ids):
    paths=list(PUBLIC)+['/product/'+str(i) for i in ids]
    urls=['<url><loc>'+escape(origin+localized(p,e))+'</loc></url>' for p in paths for e in (False,True)]
    return '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(urls)+'</urlset>'

def render(db,path,english,query,origin):
    def t(s):return EN.get(s,s) if english else s
    def url(p):return localized(p,english)
    def anchor(p,label):return '<a href="'+url(p)+'">'+escape(t(label))+'</a>'
    products=list(db.execute('SELECT * FROM product ORDER BY id'))
    title=t(TITLES.get(path,'订单详情' if path.startswith('/orders/') else '商家工作台'))
    description=DESCRIPTIONS.get(path,('桌序商店体验。','Desk Order store experience.'))[int(english)]
    canonical=origin+url(path)
    public=path in PUBLIC or path.startswith('/product/')
    hero='/assets/desk-editorial.jpg'
    extra=""
    structured=None
    if path.startswith('/product/'):
        p=next(p for p in products if str(p['id'])==path.rsplit('/',1)[-1])
        title,description=t(p['name']),t(p['description'])
        pid=p['id']
        hero='/assets/desk-item-%s.jpg'%(pid-1) if pid<=3 else '/assets/product-%s-0.jpg'%pid
        variants=list(db.execute('SELECT id,name,price,stock FROM variant WHERE product=? ORDER BY id',(pid,)))
        body='<h1>'+escape(title)+'</h1><p>'+escape(description)+'</p><img class="cover" src="'+hero+'" alt="'+escape(title)+'"><ul>'+''.join('<li>'+escape(t(v['name']))+' · USD '+str(v['price'])+'</li>' for v in variants)+'</ul>'+anchor('/shop','全部商品')
        structured={'@context':'https://schema.org','@type':'Product','name':title,'description':description,'image':origin+hero,'url':canonical,'brand':{'@type':'Brand','name':'Desk Order'}}
        info=us.CATALOG[pid]
        description=(info[1]+'. '+info[3]+'. '+description) if english else (info[2]+'，'+info[4]+'。'+description)
        offers=[]
        for v in variants:
            offers.append({'@type':'Offer','priceCurrency':'USD','price':v['price'],'availability':'https://schema.org/'+('InStock' if v['stock'] else 'OutOfStock'),'url':canonical+'?variant='+str(v['id'])})
        if len(offers)==1:
            structured['offers']=offers[0]
        else:
            structured.update({'@type':'ProductGroup','productGroupID':'DO-'+str(pid),'variesBy':['https://schema.org/size'],'hasVariant':[{'@type':'Product','name':title+' '+v['name'],'size':v['name'],'sku':'DO-'+str(v['id']),'image':origin+hero,'offers':offer} for v,offer in zip(variants,offers)]})
        extra=us.detail(pid,english)+'<details open><summary>'+('US shipping & returns' if english else '美国配送与退换')+'</summary><p>'+us.POLICY[0 if english else 1]+'</p></details>'
        collection=next(c for c,val in us.COLLECTIONS.items() if pid in val[-1])
        extra+='<p>'+anchor(collection,us.COLLECTIONS[collection][0 if english else 1])+'</p>'
        if pid==1:extra+='<p>'+anchor(us.GUIDE,us.GUIDE_TITLE[0 if english else 1])+'</p>'
    elif path in us.COLLECTIONS:
        c=us.COLLECTIONS[path]
        title,description=(c[0],c[2]) if english else (c[1],c[3])
        body='<h1>'+title+'</h1><p>'+description+'</p><div class="grid section">'
        for pid in c[-1]:
            image='/assets/desk-item-%d.jpg'%(pid-1) if pid<=3 else '/assets/product-%d-0.jpg'%pid
            price=db.execute('SELECT MIN(price) FROM variant WHERE product=?',(pid,)).fetchone()[0]
            label=t(products[pid-1]['name'])
            body+='<a class="card" href="'+url('/product/'+str(pid))+'"><img src="'+image+'" alt="'+escape(label)+'"><h3>'+escape(label)+'</h3><strong>USD '+str(price)+'</strong></a>'
        body+='</div>'
        if c[-1]==[1]:body+=anchor(us.GUIDE,us.GUIDE_TITLE[0 if english else 1])
    elif path==us.GUIDE:
        title=us.GUIDE_TITLE[0 if english else 1]
        description='Measure your desk and compare 23.6 and 31.5 inch felt desk mats for a keyboard and mouse.' if english else '测量键盘和鼠标可用空间，对比两种毛毡桌垫规格。'
        body='<article class="long"><h1>'+title+'</h1><p>'+description+'</p><img class="cover" src="/assets/product-1-2.jpg" alt="'+title+'">'
        for step in us.GUIDE_STEPS:body+='<h2>'+step[0 if english else 1]+'</h2><p>'+step[2 if english else 3]+'</p>'
        body+=anchor('/product/1',products[0]['name'])+'</article>'
    else:
        body='<h1>'+escape(title)+'</h1><p>'+escape(description)+'</p>'
        if path in ('/','/shop'):
            body+='<ul>'+''.join('<li>'+anchor('/product/'+str(p['id']),p['name'])+'</li>' for p in products)+'</ul>'
    if path in ('/','/shop'):
        body+=''.join('<p>'+anchor(k,c[0 if english else 1])+'</p>' for k,c in us.COLLECTIONS.items())
    if path in ('/support','/checkout','/cart'):
        extra='<div class="panel"><h3>'+('US demo order terms' if english else '美国模拟订单条款')+'</h3><p>'+us.POLICY[0 if english else 1]+'</p></div>'
    lang='en'  if english else 'zh-CN'
    indexable=public and not (path=='/shop' and query)
    head=['<title>'+escape(title)+' · Desk Order</title>',
          '<meta name="description" content="'+escape(description)+'">',
          '<meta property="og:title" content="'+escape(title)+'">',
          '<meta property="og:description" content="'+escape(description)+'">',
          '<meta property="og:image" content="'+origin+hero+'">',
          '<meta property="og:url" content="'+canonical+'">',
          '<meta name="robots" content="'+('index,follow' if indexable else 'noindex,follow')+'">']
    if public:
        head.append('<link rel="canonical" href="'+canonical+'">')
        for code,target in [('en',True),('zh-CN',False),('x-default',False)]:
            head.append('<link rel="alternate" hreflang="'+code+'" href="'+origin+localized(path,target)+'">')
    if structured:head.append('<script type="application/ld+json">'+json.dumps(structured,ensure_ascii=False).replace('<','\\u003c')+'</script>')
    translations=json.dumps(EN if english else {},ensure_ascii=False).replace('<','\\u003c')
    head.append('<script type="application/json" id="translations">'+translations+'</script>')
    switch=localized(path,not english)+('?' + query if query else '')
    shell=(ROOT/'index.html').read_text(encoding='utf8')
    shell=shell.replace('lang="zh-CN"','lang="'+lang+'"').replace('<title>桌序 · Desk Order</title>',''.join(head))
    if english:
        shell=shell.replace('桌序 <span>Desk Order</span>','Desk Order').replace('桌序 Desk Order','Desk Order')
        shell=re.sub(r'href="(/(?!assets/)[^"]*)"',lambda m:'href="'+url(m.group(1))+'"',shell)
        for phrase in ['全部商品','品牌手记','我的订单','购物袋','顾客服务','商家工作台','桌面用品','模拟商店']:shell=shell.replace('>'+phrase,'>'+t(phrase)).replace(' · '+phrase+'</small>',' · '+t(phrase)+'</small>')
    return shell.replace('</nav>','<a class="language" hreflang="'+('zh-CN' if english else 'en')+'" href="'+escape(switch)+'">'+('简体中文' if english else 'English')+'</a></nav>').replace('正在载入商店…',body).replace('</main>','</main><section class="market-extra" id="market-extra">'+extra+'</section>')

