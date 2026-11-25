"""US assortment and bilingual purchase guidance for the simulation."""
from html import escape

# Proposed dimensions and pricing for the demo assortment; verify against samples before launch.
CATALOG = {
  1: ('field-felt-desk-mat', 'Felt Desk Mat for Keyboard & Mouse', '键鼠毛毡桌垫',
      '23.6 × 11.8 or 31.5 × 15.7 in', '60 × 30 或 80 × 40 cm',
      'For a compact keyboard, start with the smaller mat. Choose the wider mat if your mouse regularly reaches the edge. Measure the clear depth in front of your monitor base first.',
      '紧凑键盘可先考虑小号；如果鼠标经常滑出边缘，可选择大号。请先量显示器底座前方可用的深度。',
      'Lift dust with a soft brush. Blot spills and air-dry flat.', '用软刷除尘，液体用干布轻压吸走后平放晾干。', [29,39]),
  2: ('wood-catchall-tray','Wood Catchall Tray for Keys & Earbuds','钥匙耳机桌面收纳盘',
      '7.9 × 4.7 × 0.8 in','20 × 12 × 2 cm',
      'Trace the outside footprint on paper next to your monitor. The shallow rim is for pocket essentials; bulky chargers take up most of the tray.',
      '在显示器旁用纸比出外框尺寸。浅口适合钥匙与耳机，体积较大的充电器会占据大部分空间。',
      'Wipe with a barely damp cloth and dry promptly. Avoid soaking.', '用微湿布擦拭并及时擦干，避免浸泡。',[24]),
  3: ('four-slot-cable-holder','Four-Slot Desktop Cable Holder','四槽桌面理线座',
      '3.1 × 1 × 0.7 in','8 × 2.5 × 1.8 cm',
      'Route charging leads one per groove with the plugs resting outside. Leave enough slack to reach your device before placing the holder at the desk edge.',
      '每槽放一根充电线，接头留在槽外。放在桌边前，先确认预留线长足够连接设备。',
      'Remove cables before wiping. Keep the grooves free of lint.', '擦拭前先取出线材，清除槽内灰尘。',[12]),
  4: ('angled-laptop-stand','Angled Desktop Laptop Stand','桌面斜面电脑支架',
      '9.4 × 8.3 in base','底座 24 × 21 cm',
      'Mark the base footprint and leave room in front for an external keyboard. Check the underside vents and front lip clearance on your own laptop. Load capacity is pending sample testing.',
      '按底座占地在桌上比画，前方预留外接键盘空间。请核对笔记本散热口及前挡边位置，承重仍待样品验证。',
      'Dust the contact pads before placing a device on the stand.', '放置电脑前先擦净接触垫。',[49]),
  5: ('ceramic-pen-cup','Ceramic Desk Pen Cup','陶瓷桌面笔杯',
      '3.1 in across × 3.9 in high','直径 8 cm，高 10 cm',
      'Compare the cup height with your shortest pen. Leave enough barrel above the rim to pick it up easily. A narrow corner beside a notebook works well.',
      '用最短的一支笔对比杯高，留出足够露在杯口上方的握取空间。适合放在笔记本边的窄小空位。',
      'Empty the cup before cleaning; dry inside before returning pens.', '清洁前先取出笔，杯内干燥后再使用。',[18]),
  6: ('wood-monitor-riser','Wood Desktop Monitor Riser','木质显示器增高架',
      '19.7 × 7.9 × 3.5 in outside','外形 50 × 20 × 9 cm',
      'Measure the entire monitor base, including any projecting feet. It must sit fully on the shelf. Outside dimensions do not describe the opening between the legs. Load capacity is pending sample testing.',
      '测量显示器底座及所有突出支脚，底座应完全落在架面上。外部宽度不等于架腿之间的净宽；承重仍待样品验证。',
      'Dust with a soft cloth. Keep hot cups and standing water off the shelf.', '用软布除尘，避免积水及热杯直接接触。',[59])
}
COLLECTIONS = {
 '/collections/felt-desk-mats':('Felt Desk Mats','毛毡桌垫','Compare two footprints for a keyboard and mouse on compact or full-size desks.','为紧凑书桌或大桌面对比两种键鼠桌垫尺寸。',[1]),
 '/collections/desk-organizers':('Desk Organizers','桌面收纳','Keep pocket essentials, pens and loose charging cables within reach.','分别为随身物件、笔和充电线安排桌面位置。',[2,3,5]),
 '/collections/laptop-monitor-stands':('Laptop Stands & Monitor Risers','电脑与显示器支架','Compare an angled laptop stand with a shelf for an external monitor. Measure the base before choosing.','对比笔记本斜面支架与外接显示器增高架，选择前请测量底座。',[4,6])
}
GUIDE='/guides/desk-mat-size'
GUIDE_TITLE=('What Size Desk Mat Fits Your Desk?','如何选择桌垫尺寸？')
GUIDE_STEPS=[
 ('Measure usable space','测量可用空间','Measure the clear rectangle between the desk edge and the monitor base. Exclude lamp bases, cable outlets and curved corners.','从桌沿量到显示器底座，排除台灯、走线孔和圆角占用的区域。'),
 ('Compare two footprints','对比两种占地','Tape out 23.6 × 11.8 inches, then 31.5 × 15.7 inches. With a 12-inch keyboard, the smaller mat leaves 11.6 inches of total width to divide between the mouse and margins; the larger leaves 19.5 inches.','用纸比出 60 × 30 cm 和 80 × 40 cm。搭配约 30 cm 宽的键盘，两种桌垫分别留下约 30 cm 和 50 cm 横向空间，供鼠标与两侧留白分配。'),
 ('Try your normal mouse movement','试一次日常操作','Place the keyboard on the outline and move the mouse as you normally would. If it crosses the outline, choose the wider size if your desk has the depth.','把键盘放入轮廓，按平时习惯移动鼠标。如果越界且桌面深度足够，选择较大尺寸。')]
POLICY=('US demo terms: Free standard shipping to the contiguous 48 states. Estimated arrival in 4–8 business days. Request a return within 30 days of delivery for an unused item in its original packaging. No payment, tax or shipping label is issued in this preview.',
'美国模拟条款：美国本土相连 48 州标准配送免费，预计 4–8 个工作日送达。未使用且保留原包装的商品可在签收后 30 天内申请退货。此体验不收款、不计税、不生成物流面单。')
def detail(pid,en):
    v=CATALOG[pid]
    label=lambda a,b:a if en else b
    return '<section class="market-copy"><h2>'+label('Fit & care','适配与保养')+'</h2><p><b>'+label('Proposed dimensions','拟定尺寸')+'</b> · '+(v[3] if en else v[4]+' / '+v[3])+'</p><p>'+v[5 if en else 6]+'</p><p>'+v[7 if en else 8]+'</p><small>'+label('Concept photos and proposed specifications. Confirm final measurements before release.','概念图片与拟定规格，实物尺寸待上市前核验。')+'</small></section>'

