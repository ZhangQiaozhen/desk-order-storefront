"""Exercise the store through HTTP against an isolated temporary database."""
import http.cookiejar
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

with tempfile.TemporaryDirectory() as folder:
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0))
        port=sock.getsockname()[1]
    origin='http://127.0.0.1:'+str(port)
    env=dict(os.environ, DESK_ORDER_DB=str(Path(folder)/'test.sqlite3'),DESK_ORDER_PORT=str(port))
    server=subprocess.Popen([sys.executable,str(Path(__file__).with_name('server.py'))],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    def client():
        return urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    buyer,merchant=client(),client()
    def call(user,path,payload=None,status=200):
        body=None if payload is None else json.dumps(payload).encode()
        req=urllib.request.Request(origin+path,data=body,headers={'Origin':origin,'Content-Type':'application/json'})
        try: res=user.open(req,timeout=5)
        except urllib.error.HTTPError as exc:res=exc
        with res:
            assert res.status==status,(path,res.status,status)
            return json.load(res) if path.startswith('/api/') else res.read()
    try:
        for i in range(60):
            try:
                state=call(buyer,'/api/state')
                break
            except urllib.error.URLError:time.sleep(.1)
        assert len(state['products'])==6
        for path in ('/','/shop','/cart','/checkout','/orders','/merchant','/merchant/products','/merchant/orders','/story','/support'):
            assert b'shop.js' in call(buyer,path)
        from xml.etree import ElementTree as ET
        from html.parser import HTMLParser
        class Metadata(HTMLParser):
            def __init__(self, raw):
                super().__init__()
                self.tags=[]
                self.feed(raw.decode())
            def handle_starttag(self, tag, attrs):
                self.tags.append((tag,dict(attrs)))
            def has(self, tag, **attrs):
                return any(t==tag and attrs.items()<=a.items() for t,a in self.tags)
        sitemap=ET.fromstring(call(buyer,'/sitemap.xml'))
        urls=[n.text for n in sitemap.findall('.//{*}loc')]
        assert len(set(urls))==28
        for address in urls:
            public_path=address[len(origin):]
            english=public_path.startswith('/en/')
            plain=public_path[3:] if english else public_path
            raw=call(buyer,public_path)
            meta=Metadata(raw)
            assert meta.has('html',lang='en' if english else 'zh-CN')
            assert meta.has('link',rel='canonical',href=address)
            for code,prefix in [('en','/en'),('zh-CN',''),('x-default','')]:
                assert meta.has('link',rel='alternate',hreflang=code,href=origin+prefix+plain)
            if plain.startswith('/product/'):
                assert meta.has('script',type='application/ld+json')
        assert b'<h1>Field Felt Desk Mat</h1>' in call(buyer,'/en/product/1')
        for route in ['/en/checkout','/merchant','/en/orders','/shop?q=test']:
            assert Metadata(call(buyer,route)).has('meta',name='robots',content='noindex,follow')
        filtered=Metadata(call(buyer,'/shop?category=%E6%94%AF%E6%9E%B6&q=&sort='))
        assert filtered.has('a',href='/en/shop?category=%E6%94%AF%E6%9E%B6&q=&sort=')
        assert (origin+'/sitemap.xml').encode() in call(buyer,'/robots.txt')
        for product in state['products']:
            pid=product['id']
            call(buyer,'/product/'+str(pid))
            for view in range(3):
                f='desk-item-%d.jpg'%(pid-1) if view==0 and pid<=3 else 'product-%d-%d.jpg'%(pid,view)
                assert call(buyer,'/assets/'+f).startswith(b'\xff\xd8')
        call(merchant,'/api/state')
        call(merchant,'/api/role',{'merchant':True})
        vid=state['products'][0]['variants'][0]['id']
        edit={'id':vid,'price':130,'stock':2,'wasPrice':29,'wasStock':20}
        call(merchant,'/api/variant',edit)
        call(merchant,'/api/variant',edit,400)
        call(buyer,'/api/bag',{'id':vid,'qty':3},400)
        call(buyer,'/api/bag',{'id':vid,'qty':2})
        payment=dict(token='test-payment-token',quote=[[vid,2,130]],result='declined')
        call(buyer,'/api/pay',payment,400)
        assert call(buyer,'/api/state')['bag'][0]['qty']==2
        payment['result']='success'
        call(buyer,'/api/pay',dict(payment,quote=[[vid,2,129]]),400)
        call(buyer,'/api/pay',payment)
        call(buyer,'/api/pay',payment)
        state=call(buyer,'/api/state')
        assert len(state['orders'])==1 and not state['bag'] and state['orders'][0]['amount']==260
        assert state['products'][0]['variants'][0]['stock']==0
        order=state['orders'][0]['id']
        assert not call(merchant,'/api/state')['orders']
        call(buyer,'/api/ship',{'id':order},400)
        call(merchant,'/api/ship',{'id':order})
        assert call(buyer,'/api/state')['orders'][0]['status']=='已发货'
        call(buyer,'/api/return',{'id':order})
        call(merchant,'/api/refund',{'id':order})
        assert call(buyer,'/api/state')['orders'][0]['status']=='已模拟退款'
        assert b'priceCurrency' in call(buyer,'/en/product/1?variant=2')
        assert b'23.6' in call(buyer,'/en/guides/desk-mat-size')
        print('PASS: store routes, 18 photos, price and stock sync, rejected payment, stale quote, retry, ownership and shipping.')
    finally:
        server.terminate()
        server.wait()

