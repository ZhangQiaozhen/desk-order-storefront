const app = document.querySelector('#app');
const english = document.documentElement.lang === 'en';
const prefix = english ? '/en' : '';
const path = location.pathname.slice(prefix.length) || '/';
const translations = JSON.parse(document.querySelector('#translations').textContent);
function translate(text) {
  if (!english) return text;
  return text.replace(/[一-鿿]+(?:[，。；：？、（）][一-鿿]*)*/g, phrase => translations[phrase] || phrase);
}
function preparePage(html) {
  const view = document.createElement('template');
  view.innerHTML = html;
  if (english) {
    const walker = document.createTreeWalker(view.content, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) walker.currentNode.nodeValue = translate(walker.currentNode.nodeValue);
    for (const el of view.content.querySelectorAll('[aria-label],[alt],[placeholder]')) {
      for (const attr of ['aria-label','alt','placeholder']) {
        if (el.hasAttribute(attr)) el.setAttribute(attr,translate(el.getAttribute(attr)));
      }
    }
    for (const a of view.content.querySelectorAll('a[href^="/"]')) a.setAttribute('href',prefix+a.getAttribute('href'));
  }
  app.replaceChildren(view.content);
}
const params = new URLSearchParams(location.search);
const esc = value => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const money = value => new Intl.NumberFormat(english ? 'en-US' : 'zh-CN', {style:'currency',currency:'USD',minimumFractionDigits:0,maximumFractionDigits:0}).format(value);
const link = (url,label,style='button') => `<a class="${style}" href="${url}">${label}</a>`;
const collections=['/collections/felt-desk-mats','/collections/desk-organizers','/collections/laptop-monitor-stands'];
const categories = ['桌垫','收纳','支架'];
let state;
let busy = false;

function photo(id,view=0) {
  return view===0 && id<=3 ? '/assets/desk-item-'+(id-1)+'.jpg' : '/assets/product-'+id+'-'+view+'.jpg';
}
function img(id,view=0,cls='') {
  const p=state.products.find(item=>item.id===id);
  return `<img class="${cls}" src="${photo(id,view)}" alt="${esc(p.name)} · ${['商品图','细节或场景图','使用或细节图'][view]}">`;
}
function heading(title,parent='首页') {
  return `<div class="crumb"><a href="/">${parent}</a>　/　${title}</div><h1>${title}</h1>`;
}
function card(p) {
  return `<a class="card" href="/product/${p.id}">${img(p.id)}<h3>${esc(p.name)}</h3><div class="price-row"><small>${p.color}</small><strong>${money(Math.min(...p.variants.map(v=>v.price)))}${p.variants.length>1?' 起':''}</strong></div></a>`;
}
function tiles() {
  return categories.map((c,i)=>`<a class="tile" href="${collections[i]}">${img([1,2,4][i],2)}<h3>${c}</h3></a>`).join('');
}
function home() {
  return `<section class="hero"><img src="/assets/desk-editorial.jpg" alt="自然光下的桌面用品系列"><div><h1>给桌面，<br>留一点空间。</h1><p>两种尺寸，为键盘与鼠标留出连续的工作区。</p>${link('/product/1','选购毛毡桌垫','button pale')}</div></section><div class="section row"><h2>桌面选物</h2>${link('/shop','查看全部','muted')}</div><div class="grid">${[1,2,4].map(id=>card(state.products.find(p=>p.id===id))).join('')}</div><h2 class="section">按用途选购</h2><div class="grid">${tiles()}</div>`;
}
function shop() {
  const category=params.get('category')||'',q=params.get('q')||'',sort=params.get('sort')||'';
  const products=state.products.filter(p=>(!category||category===p.category)&&translate(p.name+' '+p.category+' '+p.color).toLocaleLowerCase().includes(q.toLocaleLowerCase()));
  const price=p=>Math.min(...p.variants.map(v=>v.price));
  if(sort==='low'||sort==='high')products.sort((a,b)=>(price(a)-price(b))*(sort==='low'?1:-1));
  return heading('全部商品')+`<div class="filters"><div class="tabs">${['',...categories].map(c=>link('/shop?'+new URLSearchParams({category:c,q,sort}),c||'全部','button tab '+(category===c?'active':''))).join('')}</div><form><input type="hidden" name="category" value="${esc(category)}"><input name="q" aria-label="搜索商品" placeholder="搜索商品" value="${esc(q)}"><select name="sort" aria-label="排序"><option value="">推荐顺序</option><option value="low" ${sort==='low'?'selected':''}>价格从低到高</option><option value="high" ${sort==='high'?'selected':''}>价格从高到低</option></select><button>筛选</button></form></div><p class="muted">${products.length} 件商品</p><div class="grid">${products.map(card).join('')||'<p>没有符合条件的商品。</p>'}</div>`;
}
function product(id) {
  const p=state.products.find(x=>x.id===id),v=p.variants.find(x=>x.id===Number(params.get("variant")))||p.variants[0];
  return `<div class="crumb"><a href="/shop">全部商品</a>　/　${p.category}</div><div class="split"><div>${img(id,0,'cover')}<div class="thumbs">${[0,1,2].map(n=>`<button class="${n?'':'chosen'}" data-view="${n}" aria-label="查看图片 ${n+1}">${img(id,n)}</button>`).join('')}</div></div><div class="info"><small>${p.category} / ${p.color}</small><h1>${p.name}</h1><p>${p.description}</p><strong id="price" class="money">${money(v.price)}</strong><h3>选择规格</h3><div class="sizes">${p.variants.map((x,i)=>`<button class="outline ${x.id===v.id?'chosen':''}" data-variant="${x.id}">${english && id===1?(i?'31.5 × 15.7 in':'23.6 × 11.8 in'):x.name}</button>`).join('')}</div><p id="stock">可用库存 ${v.stock} 件</p><button id="add" data-id="${v.id}" ${v.stock?'':'disabled'}>加入购物袋</button>　${link('/cart','查看购物袋','muted')}<details><summary>配送与支付</summary>本地体验使用模拟收件地址、免运费和模拟支付，可在订单中心查看履约状态。</details></div></div><h2 class="section">搭配选购</h2><div class="grid">${state.products.filter(x=>x.id!==id).slice(0,3).map(card).join('')}</div>`;
}
const total=()=>state.bag.reduce((sum,l)=>sum+l.price*l.qty,0);
function line(l,editable=false) {
  return `<div class="line">${img(l.product)}<div class="grow"><a href="/product/${l.product}"><strong>${esc(l.name)}</strong></a><div class="muted">${esc(l.spec)} · ${money(l.price)}</div></div>${editable?`<div class="actions"><button class="outline" aria-label="减少数量" data-qty="${l.qty-1}" data-id="${l.id}">−</button><span>${l.qty}</span><button class="outline" aria-label="增加数量" data-qty="${l.qty+1}" data-id="${l.id}" ${l.qty>=Math.min(99,l.stock)?'disabled':''}>+</button><button class="outline" data-qty="0" data-id="${l.id}">移除</button></div>`:'× '+l.qty}<b>${money(l.qty*l.price)}</b></div>`;
}
function empty(title,href='/shop',label='浏览商品') {return `<div class="empty"><h3>${title}</h3><p>${link(href,label)}</p></div>`;}
function cart(){return heading('购物袋')+(state.bag.length?`<div class="checkout"><div>${state.bag.map(l=>line(l,true)).join('')}</div><div class="panel"><h3>订单摘要</h3><p>商品小计　${money(total())}</p><p>模拟配送　免运费</p><p class="money">${money(total())}</p>${link('/checkout','去结算')}</div></div>`:empty('购物袋还是空的'));}
const paymentToken=crypto.randomUUID();
function checkout(){return heading('确认订单')+(state.bag.length?`<div class="checkout"><div><div class="panel"><h3>配送信息</h3><p>体验收件人 · 桌序演示收货点</p><small>使用模拟地址，无需填写个人资料。</small></div><div class="panel"><h3>支付方式</h3><p>模拟钱包 · 无真实扣款</p><label>模拟结果 <select id="result"><option value="success">支付成功</option><option value="declined">支付失败</option></select></label></div></div><div class="panel"><h3>订单明细</h3>${state.bag.map(l=>line(l)).join('')}<p class="row">应付合计 <b>${money(total())}</b></p><button id="pay">确认模拟支付</button><p class="error" id="failure" role="alert"></p></div></div>`:empty('暂无待结算商品'));}
function orderCard(o,manage=false){return `<article class="panel"><div class="row"><strong>订单 #${o.id}</strong><span class="tag">${o.status}</span></div><small>${o.created} UTC</small>${o.items.map(l=>line(l)).join('')}<div class="row"><b>已模拟支付　${money(o.amount)}</b>${manage&&o.status==='待发货'?`<button data-ship="${o.id}">确认模拟发货</button>`:manage&&o.status==='退货申请中'?`<button data-refund="${o.id}">确认模拟退款</button>`:!manage&&o.status==='已发货'?`<button data-return="${o.id}">申请退货</button>`:!manage&&path==='/orders'?link('/orders/'+o.id,'订单详情','button outline'):''}</div></article>`;}
function orders(){
  if(path==='/orders')return heading('我的订单')+(state.orders.map(o=>orderCard(o)).join('')||empty('还没有订单'));
  const o=state.orders.find(o=>path.endsWith('/'+o.id));
  return heading('订单详情')+(o?`<p class="stripe">模拟支付已完成 · ${o.status}</p>${orderCard(o)}${link('/orders','返回我的订单','button outline')}`:empty('找不到此订单','/orders','返回订单中心'));
}
function merchant(){
  const title=heading('商家工作台');
  if(!state.merchant)return title+`<div class="panel long"><h3>以体验商家身份进入</h3><p>管理本机模拟店铺的定价、库存和订单。修改会同步到顾客端。</p><button data-role="on">进入工作台</button></div>`;
  const tabs=`<div class="tabs">${[['/merchant','经营概览'],['/merchant/products','商品与库存'],['/merchant/orders','订单管理']].map(([u,l])=>link(u,l,'button tab '+(u===path?'active':''))).join('')}<button class="outline" data-role="off">退出商家身份</button></div>`;
  let body='';
  if(path==='/merchant/products'){
    body=`<div class="table"><table><thead><tr><th>商品</th><th>规格</th><th>售价（美元）</th><th>库存（件）</th><th>操作</th></tr></thead><tbody>${state.products.flatMap(p=>p.variants.map(v=>`<tr><td>${p.name}</td><td>${v.name}</td><td><input type="number" aria-label="售价" min="1" max="100000" value="${v.price}"></td><td><input type="number" aria-label="库存" min="0" max="100000" value="${v.stock}"></td><td><button data-save="${v.id}">保存</button></td></tr>`)).join('')}</tbody></table></div>`;
  }else if(path==='/merchant/orders'){
    body=state.allOrders.map(o=>orderCard(o,true)).join('')||empty('还没有收到订单');
  }else{
    const rows=state.allOrders;
    body=`<div class="kpis">${[['模拟成交额',money(rows.reduce((n,o)=>n+(o.status==='已模拟退款'?0:o.amount),0))],['订单数',rows.length],['待发货',rows.filter(o=>o.status==='待发货').length]].map(([k,v])=>`<div class="panel"><small>${k}</small><b>${v}</b></div>`).join('')}</div><h2 class="section">最近订单</h2>${rows.slice(0,3).map(o=>orderCard(o,true)).join('')||empty('等待第一笔订单')}`;
  }return title+tabs+body;
}
function story(){return heading('品牌手记')+`<div class="section split"><img src="/assets/desk-editorial.jpg" alt="桌序桌面系列场景"><div class="long"><h2>为每天伸手的地方。</h2><p>桌序围绕书桌上的三个动作选物：放下随身物件，展开工作，把东西收回原位。</p><p>桌垫给键盘留下边界，浅盘收住钥匙和耳机，支架把屏幕下方的空间还给桌面。</p>${link('/shop','浏览整个系列')}</div></div><div class="section grid">${tiles()}</div>`;}
function support(){return heading('顾客服务')+`<div class="long"><details open><summary>如何体验购买？</summary><p>在商品详情选择规格并加入购物袋，前往结算，选择模拟支付结果。支付成功后会生成订单并扣减库存。</p></details><details><summary>在哪里查看发货状态？</summary><p>在我的订单里查看。进入本机商家工作台确认模拟发货后，订单详情会显示已发货。</p></details><details><summary>商品和交易是真实的吗？</summary><p>图片为概念摄影，金额、库存、地址与物流均用于体验。本机商店不会收款或寄送商品。</p></details></div>`;}
async function refresh(){
  const response=await fetch('/api/state');
  if(!response.ok)throw Error('暂时无法加载商品，请刷新重试');
  state=await response.json();
  document.querySelector('#count').textContent=state.bag.reduce((n,l)=>n+l.qty,0);
  if(path.startsWith('/collections/')||path.startsWith('/guides/'))return;
  const markup=path==='/'?home():path==='/shop'?shop():path.startsWith('/product/')?product(Number(path.split('/').pop())):path==='/cart'?cart():path==='/checkout'?checkout():path.startsWith('/orders')?orders():path.startsWith('/merchant')?merchant():path==='/story'?story():support();
  preparePage(markup);
  const extra=document.querySelector('#market-extra');
  if(extra&&path.startsWith('/product/'))app.querySelector('.info').append(extra);
  if(extra&&path==='/checkout'&&app.querySelector('#pay'))app.querySelector('#pay').before(extra);
  if(path==='/shop'){
    const nav=document.createElement('div');nav.className='tabs';
    categories.forEach((c,i)=>{const a=document.createElement('a');a.className='tab button';a.href=prefix+collections[i];a.textContent=translate(c);nav.append(a);});
    app.append(nav);
  }
}
function notify(message){const box=document.querySelector('#notice');box.textContent=translate(message);clearTimeout(notify.timer);notify.timer=setTimeout(()=>box.textContent='',3500);}
async function post(route,data){const res=await fetch('/api/'+route,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});if(!res.ok)throw Error((await res.json()).error);}
app.addEventListener('click',async event=>{
  const b=event.target.closest('button');if(!b||busy)return;
  const d=b.dataset;
  if(d.view!==undefined){app.querySelector('.cover').src=b.querySelector('img').src;app.querySelector('.cover').alt=b.querySelector('img').alt;app.querySelectorAll('[data-view]').forEach(x=>x.classList.toggle('chosen',x===b));return;}
  if(d.variant){const v=state.products.flatMap(p=>p.variants).find(v=>v.id===Number(d.variant));app.querySelector('#price').textContent=money(v.price);app.querySelector('#stock').textContent=translate('可用库存 '+v.stock+' 件');const url=new URL(location.href);url.searchParams.set('variant',v.id);history.replaceState(null,'',url);const switcher=document.querySelector('.language');if(switcher)switcher.href=(english?'':'/en')+path+url.search;const add=app.querySelector('#add');add.dataset.id=v.id;add.disabled=!v.stock;app.querySelectorAll('[data-variant]').forEach(x=>x.classList.toggle('chosen',x===b));return;}
  busy=true;
  try{
    if(b.id==='add'){await post('bag',{id:d.id,delta:1});location.href=prefix+'/cart';}
    else if(d.qty!==undefined){await post('bag',{id:d.id,qty:d.qty});await refresh();}
    else if(b.id==='pay'){await post('pay',{token:paymentToken,result:app.querySelector('#result').value,quote:state.bag.map(x=>[x.id,x.qty,x.price])});location.href=prefix+'/orders';}
    else if(d.role){await post('role',{merchant:d.role==='on'});location.href=prefix+'/merchant';}
    else if(d.return||d.refund){await post(d.return?'return':'refund',{id:d.return||d.refund});await refresh();}
    else if(d.ship){await post('ship',{id:d.ship});await refresh();notify('已更新发货状态');}
    else if(d.save){const fields=[...b.closest('tr').querySelectorAll('input')];if(fields.some(f=>!f.value||!f.reportValidity()))return;const v=state.products.flatMap(p=>p.variants).find(v=>v.id===Number(d.save));await post('variant',{id:v.id,price:fields[0].value,stock:fields[1].value,wasPrice:v.price,wasStock:v.stock});await refresh();notify('价格与库存已保存');}
  }catch(e){const failure=app.querySelector('#failure');if(failure)failure.textContent=translate(e.message);else notify(e.message);}finally{busy=false;}
});
refresh().catch(e=>{app.textContent=translate(e.message);});
window.addEventListener('pageshow',e=>{if(e.persisted)location.reload();});
