"""Local commerce simulator. Run with Python 3.8+."""
import json
import os
import re
import secrets
import sqlite3
from contextlib import closing
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import storefront
import us_market as us

ROOT = Path(__file__).resolve().parent
DB = Path(os.environ.get("DESK_ORDER_DB", str(ROOT / "us-store.sqlite3")))
PORT = int(os.environ.get("DESK_ORDER_PORT", "18764"))
ORIGIN = "http://127.0.0.1:%d" % PORT
PRODUCTS = [
    ("原野毛毡桌垫","桌垫","石墨灰","给键盘和鼠标一块连续的操作区。两种尺寸，适配不同宽度的桌面。", [("60 × 30 cm",129),("80 × 40 cm",169)]),
    ("方隅收纳盘","收纳","胡桃棕","把每天随身带走的钥匙和耳机放在同一个地方。浅口盘沿，拿取一目了然。",[("长方形",99)]),
    ("线序理线座","收纳","炭黑","四道线槽分开收拢充电线，让线头留在伸手可及的桌边。",[("四槽",39)]),
    ("折面电脑支架","支架","雾青","斜面托起笔记本，为外接键盘腾出操作空间。",[("桌面款",199)]),
    ("素筒陶瓷笔杯","收纳","奶白","把最常用的几支笔集中放好，为手写留一个位置。",[("圆筒款",69)]),
    ("木屿显示器增高架","支架","胡桃棕","抬高屏幕，下方留出收纳键盘的空间。",[("标准款",259)])
]

def connect():
    db = sqlite3.connect(DB, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db

def initialize():
    with closing(connect()) as db, db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS product(id INTEGER PRIMARY KEY,name TEXT,category TEXT,color TEXT,description TEXT);
        CREATE TABLE IF NOT EXISTS variant(id INTEGER PRIMARY KEY,product INTEGER REFERENCES product(id),name TEXT,price INTEGER,stock INTEGER);
        CREATE TABLE IF NOT EXISTS visitor(id TEXT PRIMARY KEY, merchant INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS bag(owner TEXT,variant INTEGER REFERENCES variant(id),qty INTEGER,PRIMARY KEY(owner,variant));
        CREATE TABLE IF NOT EXISTS sale(id TEXT PRIMARY KEY,owner TEXT,token TEXT,created TEXT DEFAULT CURRENT_TIMESTAMP,status TEXT,amount INTEGER,items TEXT,UNIQUE(owner,token));
        """)
        if not db.execute("SELECT 1 FROM product").fetchone():
            for i,(name,category,color,desc,variants) in enumerate(PRODUCTS,1):
                db.execute("INSERT INTO product VALUES (?,?,?,?,?)",(i,name,category,color,desc))
                db.executemany("INSERT INTO variant(product,name,price,stock) VALUES (?,?,?,20)",[(i,n,p) for (n,_),p in zip(variants,us.CATALOG[i][-1])])

def records(db, sql, args=()):
    return [dict(r) for r in db.execute(sql,args)]

def bag(db,owner):
    return records(db,"SELECT v.id,v.product,p.name,v.name AS spec,v.price,v.stock,b.qty FROM bag b JOIN variant v ON v.id=b.variant JOIN product p ON p.id=v.product WHERE owner=? ORDER BY v.id",(owner,))

def sales(db, owner=None):
    rows=records(db,"SELECT id,created,status,amount,items FROM sale"+(" WHERE owner=?" if owner else "")+" ORDER BY created DESC,rowid DESC",(owner,) if owner else ())
    for row in rows: row["items"]=json.loads(row["items"])
    return rows

class Handler(BaseHTTPRequestHandler):
    def send(self, status, data, mime="application/json; charset=utf-8",cookie=None):
        if not isinstance(data,bytes): data=json.dumps(data,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type",mime)
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(data)))
        if cookie: self.send_header("Set-Cookie","desk_session="+cookie+"; HttpOnly; SameSite=Strict; Path=/")
        self.end_headers()
        self.wfile.write(data)

    def dispatch(self, write):
        if self.headers.get("Host")!=urlsplit(ORIGIN).netloc or (write and self.headers.get("Origin")!=ORIGIN):
            return self.send(403,{"error":"请求来源无效"})
        request=urlsplit(self.path)
        path=request.path
        english=path.startswith("/en/")
        if not write and path=="/en":
            self.send_response(308)
            self.send_header("Location","/en/"+("?"+request.query if request.query else ""))
            self.end_headers()
            return
        if english:path=path[3:]
        if not write and path=="/robots.txt" and not english:
            return self.send(200,("User-agent: *\nDisallow: /api/\nSitemap: "+ORIGIN+"/sitemap.xml\n").encode(),"text/plain; charset=utf-8")
        if not write and path=="/sitemap.xml" and not english:
            with closing(connect()) as db:
                xml=storefront.sitemap(ORIGIN,[r[0] for r in db.execute("SELECT id FROM product ORDER BY id")])
            return self.send(200,xml.encode(),"application/xml; charset=utf-8")
        if not write and not path.startswith("/api/"):
            file=ROOT/"index.html"
            if re.fullmatch(r"/assets/[A-Za-z0-9._-]+",path): file=ROOT/path[1:]
            elif path not in storefront.PUBLIC and not re.fullmatch(r"/(?:|shop|product/[1-6]|cart|checkout|orders(?:/[a-f0-9]{10})?|merchant(?:/products|/orders)?|story|support)",path):
                return self.send(404,{"error":"页面不存在"})
            if file==ROOT/"index.html":
                with closing(connect()) as db:
                    html=storefront.render(db,path,english,request.query,ORIGIN)
                return self.send(200,html.encode(),"text/html; charset=utf-8")
            if not file.is_file():return self.send(404,{"error":"文件不存在"})
            mime={".jpg":"image/jpeg",".js":"text/javascript",".css":"text/css",".html":"text/html; charset=utf-8"}[file.suffix]
            return self.send(200,file.read_bytes(),mime)
        with closing(connect()) as db, db:
            cookies=SimpleCookie(self.headers.get("Cookie",""))
            sid=cookies["desk_session"].value if "desk_session" in cookies else ""
            visitor=db.execute("SELECT * FROM visitor WHERE id=?",(sid,)).fetchone()
            if write and not visitor: return self.send(403,{"error":"请刷新页面后重试"})
            if not visitor:
                sid=secrets.token_hex(24)
                db.execute("INSERT INTO visitor(id) VALUES(?)",(sid,))
            if write:
                if int(self.headers.get("Content-Length",0))>8192:return self.send(413,{"error":"请求过大"})
                data=json.loads(self.rfile.read(int(self.headers.get("Content-Length",0))))
                db.execute("BEGIN IMMEDIATE")
                self.change(db,path,sid,data,visitor["merchant"])
                db.commit()
                return self.send(200,{"ok":True})
            if path!="/api/state":return self.send(404,{})
            products=records(db,"SELECT * FROM product ORDER BY id")
            for p in products:p["variants"]=records(db,"SELECT * FROM variant WHERE product=? ORDER BY id",(p["id"],))
            data=dict(products=products,bag=bag(db,sid),orders=sales(db,sid),merchant=bool(visitor and visitor["merchant"]))
            if data["merchant"]:data["allOrders"]=sales(db)
            db.commit()
            self.send(200,data,cookie=sid if not visitor else None)

    def change(self,db,path,sid,d,merchant):
        if path=="/api/role":
            db.execute("UPDATE visitor SET merchant=? WHERE id=?",(int(d["merchant"] is True),sid))
        elif path=="/api/bag":
            vid=int(d["id"])
            v=db.execute("SELECT stock FROM variant WHERE id=?",(vid,)).fetchone()
            if not v:raise ValueError("规格不存在")
            current=db.execute("SELECT qty FROM bag WHERE owner=? AND variant=?",(sid,vid)).fetchone()
            qty=int(d["delta"])+(current[0] if current else 0) if "delta" in d else int(d["qty"])
            if not 0<=qty<=min(99,v[0]):raise ValueError("数量超出当前可用库存，请调整数量")
            db.execute("DELETE FROM bag WHERE owner=? AND variant=?",(sid,vid))
            if qty:db.execute("INSERT INTO bag VALUES(?,?,?)",(sid,vid,qty))
        elif path=="/api/pay":
            token=d["token"]
            if not re.fullmatch("[a-zA-Z0-9-]{12,80}",token):raise ValueError("请刷新结算页")
            if db.execute("SELECT 1 FROM sale WHERE owner=? AND token=?",(sid,token)).fetchone():return
            if d["result"]!="success":raise ValueError("模拟支付被拒绝。购物袋已保留，可以重新支付。")
            items=bag(db,sid)
            if not items:raise ValueError("购物袋为空")
            if d["quote"]!=[[x["id"],x["qty"],x["price"]] for x in items]:raise ValueError("商品价格或数量已变更，请刷新并确认")
            for x in items:
                if not db.execute("UPDATE variant SET stock=stock-? WHERE id=? AND stock>=?",(x["qty"],x["id"],x["qty"])).rowcount:raise ValueError("库存不足，请返回购物袋调整")
            db.execute("INSERT INTO sale(id,owner,token,status,amount,items) VALUES (?,?,?,?,?,?)",(secrets.token_hex(5),sid,token,"待发货",sum(x["price"]*x["qty"] for x in items),json.dumps(items,ensure_ascii=False)))
            db.execute("DELETE FROM bag WHERE owner=?",(sid,))
        elif merchant and path=="/api/variant":
            price,stock=int(d["price"]),int(d["stock"])
            if not (1<=price<=100000 and 0<=stock<=100000):raise ValueError("请输入有效的价格和库存")
            if not db.execute("UPDATE variant SET price=?,stock=? WHERE id=? AND price=? AND stock=?",(price,stock,int(d["id"]),int(d["wasPrice"]),int(d["wasStock"]))).rowcount:raise ValueError("库存或价格已经变化，请刷新后重试")
        elif path=="/api/return":
            if not db.execute("UPDATE sale SET status='退货申请中' WHERE id=? AND owner=? AND status='已发货'",(d["id"],sid)).rowcount:raise ValueError("操作无效")
        elif merchant and path=="/api/refund":
            if not db.execute("UPDATE sale SET status='已模拟退款' WHERE id=? AND status='退货申请中'",(d["id"],)).rowcount:raise ValueError("操作无效")
        elif merchant and path=="/api/ship":
            if not db.execute("UPDATE sale SET status='已发货' WHERE id=? AND status='待发货'",(d["id"],)).rowcount:raise ValueError("订单状态已经变化，请刷新")
        else:raise ValueError("操作无效")

    def handle_request(self,write):
        try:self.dispatch(write)
        except (ValueError,KeyError,TypeError): 
            import sys
            exc=sys.exc_info()[1]
            self.send(400,{"error":str(exc) if type(exc) is ValueError else "提交的数据无效"})
        except sqlite3.Error:self.send(503,{"error":"数据库暂时不可用，请重试"})
    def do_GET(self):self.handle_request(False)
    def do_POST(self):self.handle_request(True)

if __name__=="__main__":
    initialize()
    print(ORIGIN,flush=True)
    ThreadingHTTPServer(("127.0.0.1",PORT),Handler).serve_forever()

