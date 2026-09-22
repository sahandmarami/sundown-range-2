#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch v4.2: restore FULL visual quality (quality-first adaptive), move pause
button to top-left, warm pause-screen background like the game sky, black chest
box texts. Applies on top of v4.1 file."""
import sys, shutil

SRC = '/home/z/my-project/repo/game-src/index.html'
with open(SRC, 'r', encoding='utf-8') as f:
    html = f.read()

orig_len = len(html)
patches = []

def P(name, old, new, expect=1):
    patches.append((name, old, new, expect))

# ---------------------------------------------------------------
# Q1: renderer — antialias restored everywhere, native PR cap 2, start at FULL quality
# ---------------------------------------------------------------
P('renderer-quality',
"""var renderer=new THREE.WebGLRenderer({canvas:$('c'),antialias:!IS_MOBILE,stencil:false,powerPreference:'high-performance'});
var PR_CAP=IS_MOBILE?Math.min(window.devicePixelRatio||1,1.35):Math.min(window.devicePixelRatio||1,2);var PR_FLOOR=IS_MOBILE?.55:.8,curPR=IS_MOBILE?Math.min(window.devicePixelRatio||1,1.1):PR_CAP;
renderer.setPixelRatio(curPR);renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;renderer.shadowMap.type=IS_MOBILE?THREE.PCFShadowMap:THREE.PCFSoftShadowMap;""",
"""var renderer=new THREE.WebGLRenderer({canvas:$('c'),antialias:true,stencil:false,powerPreference:'high-performance'});
var PR_CAP=Math.min(window.devicePixelRatio||1,2);var PR_FLOOR=IS_MOBILE?1.1:.9,curPR=PR_CAP;
renderer.setPixelRatio(curPR);renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;""")

# Q2: shadows back to 2048 PCFSoft on every device
P('shadow-restore',
"sun.castShadow=true;sun.shadow.mapSize.set(IS_MOBILE?1024:2048,IS_MOBILE?1024:2048);",
"sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);")

# Q3: particles restored to original counts
P('smoke-restore', "var SMOKE_N=IS_MOBILE?12:20,", "var SMOKE_N=20,")
P('emb-restore',   "var EMB=IS_MOBILE?22:35,",     "var EMB=35,")
P('dust-restore',  "var DUST=IS_MOBILE?90:160,",   "var DUST=160,")

# Q4: adaptive tuner — quality-first: only eases down when device truly struggles (<36fps), floor much higher
P('adapt-gentle',
"""function adaptPR(rdt){ftAcc+=rdt;ftN++;ftWait-=rdt;if(ftWait>0||ftN<24)return;var fps=ftN/Math.max(.0001,ftAcc);ftAcc=0;ftN=0;var ch=false;
 if(fps<44){if(curPR>PR_FLOOR+.001){curPR=Math.max(PR_FLOOR,curPR-.12);ch=true;if(!prAnnounced){prAnnounced=true;announce('کیفیت گرافیک برای اجرای روان‌تر خودکار تنظیم شد');}}}
 else if(fps>57&&curPR<PR_CAP-.001){curPR=Math.min(PR_CAP,curPR+.06);ch=true;}
 if(ch){renderer.setPixelRatio(curPR);ftWait=2.4;}else ftWait=1.2;}""",
"""function adaptPR(rdt){ftAcc+=rdt;ftN++;ftWait-=rdt;if(ftWait>0||ftN<30)return;var fps=ftN/Math.max(.0001,ftAcc);ftAcc=0;ftN=0;var ch=false;
 if(fps<36){if(curPR>PR_FLOOR+.001){curPR=Math.max(PR_FLOOR,curPR-.2);ch=true;if(!prAnnounced){prAnnounced=true;announce('برای روان‌شدن، کیفیت چند لحظه‌ای تنظیم شد');}}}
 else if(fps>54&&curPR<PR_CAP-.001){curPR=Math.min(PR_CAP,curPR+.1);ch=true;}
 if(ch){renderer.setPixelRatio(curPR);ftWait=3;}else ftWait=1.5;}""")

# ---------------------------------------------------------------
# UI1: pause button -> top-left, comboBox avoids it
# ---------------------------------------------------------------
P('pausebtn-top',
"""#pauseBtn{position:absolute;bottom:calc(20px + env(safe-area-inset-bottom));right:calc(14px + env(safe-area-inset-right));z-index:26;width:52px;height:52px;border:1px solid rgba(255,176,84,.4);background:linear-gradient(180deg,rgba(15,16,22,.82),rgba(10,10,14,.92));clip-path:polygon(10px 0,100% 0,100% calc(100% - 10px),calc(100% - 10px) 100%,0 100%,0 10px);display:flex;align-items:center;justify-content:center;gap:5px;opacity:0;pointer-events:none;transition:opacity .3s,transform .08s;cursor:pointer}
#hud.on~#pauseBtn{opacity:1;pointer-events:auto}
#pauseBtn i{display:block;width:5px;height:17px;background:#ffd24a;border-radius:1px;box-shadow:0 0 8px rgba(255,210,74,.45)}
#pauseBtn:active{transform:scale(.93)}
#pauseMenu{z-index:90;gap:0}""",
"""#pauseBtn{position:absolute;top:calc(10px + env(safe-area-inset-top));left:calc(14px + env(safe-area-inset-left));z-index:26;width:46px;height:46px;border:1px solid rgba(255,176,84,.4);background:linear-gradient(180deg,rgba(15,16,22,.78),rgba(10,10,14,.88));clip-path:polygon(10px 0,100% 0,100% calc(100% - 10px),calc(100% - 10px) 100%,0 100%,0 10px);display:flex;align-items:center;justify-content:center;gap:5px;opacity:0;pointer-events:none;transition:opacity .3s,transform .08s;cursor:pointer}
#hud.on~#pauseBtn{opacity:1;pointer-events:auto}
#pauseBtn i{display:block;width:4.5px;height:15px;background:#ffd24a;border-radius:1px;box-shadow:0 0 8px rgba(255,210,74,.45)}
#pauseBtn:active{transform:scale(.93)}
#comboBox{left:calc(72px + env(safe-area-inset-left))}
@media(max-width:640px){#comboBox{left:calc(14px + env(safe-area-inset-left))!important;top:calc(64px + env(safe-area-inset-top))!important}}
#pauseMenu{z-index:90;gap:0;background:linear-gradient(180deg,rgba(224,160,115,.44),rgba(165,106,74,.55) 45%,rgba(64,43,31,.68))}""")

# UI2+UI3: fix mobile pause rule + chest box texts -> black on light background
P('chest-black',
"""@media(max-width:640px){#pauseBtn{width:48px;height:48px;bottom:calc(24px + env(safe-area-inset-bottom))}}
</style>""",
"""@media(max-width:640px){#pauseBtn{width:42px;height:42px}}
/* ================= متن سیاه جعبهٔ جایزه (خوانا روی کارت روشن) ================= */
#chestBox{background:linear-gradient(180deg,#fff3da,#ffe7c2)!important;border:1px solid rgba(203,133,53,.5)!important}
.chest-t{color:#1a1206!important}
.chest-c{color:#141210!important}
.chest-n{color:#1a1206!important}
.chest-d{color:#1a1206!important}
</style>""")

# ---------------------------------------------------------------
# V1: version strings 4.1 -> 4.2
# ---------------------------------------------------------------
P('title-ver', '<title>میدان غروب ۲ | نسخهٔ ۴٫۱ طلایی</title>', '<title>میدان غروب ۲ | نسخهٔ ۴٫۲ طلایی</title>')
P('foot-ver', '<span>V4.1 GOLD</span>', '<span>V4.2 GOLD</span>')

# ---------------- apply ----------------
fail = False
for name, old, new, expect in patches:
    cnt = html.count(old)
    if cnt != expect:
        print(f"FAIL [{name}] expected {expect}, found {cnt}")
        fail = True
if fail:
    sys.exit(1)

for name, old, new, expect in patches:
    html = html.replace(old, new)
    print(f"OK  [{name}]")

with open(SRC, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"size: {orig_len/1e6:.3f}MB -> {len(html)/1e6:.3f}MB")

for token in ['antialias:true,stencil:false', 'PR_FLOOR=IS_MOBILE?1.1:.9', 'mapSize.set(2048,2048)',
              'var SMOKE_N=20,', 'var EMB=35,', 'var DUST=160,', 'V4.2 GOLD', 'chest-n{color:#1a1206']:
    c = html.count(token)
    print(f"  sanity '{token}': {c}")
    if c == 0:
        print("MISSING TOKEN — aborting sync"); sys.exit(2)

# no leftovers from v4.1 quality settings
for bad in ['IS_MOBILE?1024:2048', 'PR_FLOOR=IS_MOBILE?.55', 'antialias:!IS_MOBILE', 'V4.1 GOLD']:
    if bad in html:
        print(f"LEFTOVER FOUND: {bad} — aborting"); sys.exit(3)

copies = [
    '/home/z/my-project/repo/docs/index.html',
    '/home/z/my-project/repo/apk-project/www/index.html',
    '/home/z/my-project/apk/www/index.html',
]
for dst in copies:
    shutil.copyfile(SRC, dst)
    print(f"synced -> {dst}")
print("ALL DONE")
