#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch v4.1: performance optimization + pause/exit menu for Sundown Range II.
Each patch asserts exact-match uniqueness before applying."""
import sys, shutil

SRC = '/home/z/my-project/repo/game-src/index.html'

with open(SRC, 'r', encoding='utf-8') as f:
    html = f.read()

orig_len = len(html)
patches = []

def P(name, old, new, expect=1):
    patches.append((name, old, new, expect))

# ---------------------------------------------------------------
# P1: Mobile detection + adaptive-capable renderer init
# ---------------------------------------------------------------
P('renderer-init',
"""var renderer=new THREE.WebGLRenderer({canvas:$('c'),antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;""",
"""var IS_MOBILE=(/Android|iPhone|iPad|iPod|Mobile|Silk/i.test(navigator.userAgent||''))||(((navigator.maxTouchPoints||0)>1)&&Math.min(screen.width||9e9,screen.height||9e9)<820);if(IS_MOBILE)document.documentElement.classList.add('mob');
var renderer=new THREE.WebGLRenderer({canvas:$('c'),antialias:!IS_MOBILE,stencil:false,powerPreference:'high-performance'});
var PR_CAP=IS_MOBILE?Math.min(window.devicePixelRatio||1,1.35):Math.min(window.devicePixelRatio||1,2);var PR_FLOOR=IS_MOBILE?.55:.8,curPR=IS_MOBILE?Math.min(window.devicePixelRatio||1,1.1):PR_CAP;
renderer.setPixelRatio(curPR);renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;renderer.shadowMap.type=IS_MOBILE?THREE.PCFShadowMap:THREE.PCFSoftShadowMap;""")

# P2: shadow map resolution halved on mobile
P('shadow-mapsize',
"sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);",
"sun.castShadow=true;sun.shadow.mapSize.set(IS_MOBILE?1024:2048,IS_MOBILE?1024:2048);")

# P3: fewer ambient particles on mobile
P('smoke-count', "var SMOKE_N=20,", "var SMOKE_N=IS_MOBILE?12:20,")
P('emb-count',   "var EMB=35,",     "var EMB=IS_MOBILE?22:35,")
P('dust-count',  "var DUST=160,",   "var DUST=IS_MOBILE?90:160,")

# P4: adaptive resolution tuner (FPS-driven dynamic pixel ratio)
P('adapt-fns',
"/* ================= LOOP ================= */",
"""/* ================= ADAPTIVE RESOLUTION v4.1 ================= */
var ftAcc=0,ftN=0,ftWait=2.5,prAnnounced=false;
function adaptPR(rdt){ftAcc+=rdt;ftN++;ftWait-=rdt;if(ftWait>0||ftN<24)return;var fps=ftN/Math.max(.0001,ftAcc);ftAcc=0;ftN=0;var ch=false;
 if(fps<44){if(curPR>PR_FLOOR+.001){curPR=Math.max(PR_FLOOR,curPR-.12);ch=true;if(!prAnnounced){prAnnounced=true;announce('کیفیت گرافیک برای اجرای روان‌تر خودکار تنظیم شد');}}}
 else if(fps>57&&curPR<PR_CAP-.001){curPR=Math.min(PR_CAP,curPR+.06);ch=true;}
 if(ch){renderer.setPixelRatio(curPR);ftWait=2.4;}else ftWait=1.2;}
/* ================= LOOP ================= */""")

# P5: hook tuner into main loop
P('adapt-call',
"var rdt=Math.min(.05,(now-last)/1000)||.016;last=now;var t=now/1000;dawnPulse=.5+.5*Math.sin(t*.18);",
"var rdt=Math.min(.05,(now-last)/1000)||.016;last=now;var t=now/1000;dawnPulse=.5+.5*Math.sin(t*.18);if(!pauseGame)adaptPR(rdt);")

# P6: resize keeps current adaptive pixel ratio
P('resize-pr',
"function doResize(){camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.setSize(innerWidth,innerHeight);}",
"function doResize(){camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setPixelRatio(curPR);renderer.setSize(innerWidth,innerHeight);}")

# P7: HTML — pause button + pause overlay before ammoBox
P('html-pause',
'<div id="ammoBox"><span id="ammo">۱۰۰ / ۱۰۰</span></div>',
"""<button id="pauseBtn" aria-label="توقف بازی"><i></i><i></i></button>
<div id="pauseMenu" class="screen off">
<div class="pcard">
<div class="p-title">⏸ توقف</div>
<div class="p-sub" id="pauseInfo">بازی متوقف شد</div>
<button id="pauseResume" class="btn res">▶ ادامه بازی</button>
<button id="pauseRestart" class="btn again">↻ شروع دوبارهٔ مرحله</button>
<button id="pauseExit" class="btn quit">⏏ خروج به منو</button>
<div class="p-note">پیشرفت این راند ذخیره می‌ماند</div>
</div></div>
<div id="ammoBox"><span id="ammo">۱۰۰ / ۱۰۰</span></div>""")

# P8: CSS for pause button + menu (before final </style>)
P('css-pause',
"""#guideStart{background:linear-gradient(180deg,#fbbf24,#f97316)!important;border-color:rgba(255,255,255,.4)!important;color:#fff!important;text-shadow:0 1px 3px rgba(120,50,0,.45)!important;box-shadow:0 8px 22px rgba(234,88,12,.35)!important}
</style>""",
"""#guideStart{background:linear-gradient(180deg,#fbbf24,#f97316)!important;border-color:rgba(255,255,255,.4)!important;color:#fff!important;text-shadow:0 1px 3px rgba(120,50,0,.45)!important;box-shadow:0 8px 22px rgba(234,88,12,.35)!important}
</style>

<style id="pause-system-v41">
/* ================= دکمه توقف و منوی مکث v4.1 ================= */
#pauseBtn{position:absolute;bottom:calc(20px + env(safe-area-inset-bottom));right:calc(14px + env(safe-area-inset-right));z-index:26;width:52px;height:52px;border:1px solid rgba(255,176,84,.4);background:linear-gradient(180deg,rgba(15,16,22,.82),rgba(10,10,14,.92));clip-path:polygon(10px 0,100% 0,100% calc(100% - 10px),calc(100% - 10px) 100%,0 100%,0 10px);display:flex;align-items:center;justify-content:center;gap:5px;opacity:0;pointer-events:none;transition:opacity .3s,transform .08s;cursor:pointer}
#hud.on~#pauseBtn{opacity:1;pointer-events:auto}
#pauseBtn i{display:block;width:5px;height:17px;background:#ffd24a;border-radius:1px;box-shadow:0 0 8px rgba(255,210,74,.45)}
#pauseBtn:active{transform:scale(.93)}
#pauseMenu{z-index:90;gap:0}
#pauseMenu .pcard{display:flex;flex-direction:column;gap:12px;width:min(88vw,370px);padding:26px 24px 20px;background:linear-gradient(180deg,rgba(20,21,28,.98),rgba(10,11,15,.99));border:1px solid rgba(255,176,84,.4);border-radius:14px;box-shadow:0 18px 70px rgba(0,0,0,.7);text-align:center}
#pauseMenu .p-title{font-size:26px;font-weight:900;color:#ffd24a;letter-spacing:.5px}
#pauseMenu .p-sub{font-size:12.5px;font-weight:700;color:rgba(255,220,170,.78);margin:-4px 0 6px}
#pauseMenu .btn{width:100%;min-height:52px;padding:13px 18px;font-size:16px}
#pauseMenu .btn.res{background:linear-gradient(180deg,#ffc46a,#ff8c2e);color:#1c0f02}
#pauseMenu .btn.again{background:rgba(255,176,84,.1);color:#ffd8a0;border:1px solid rgba(255,176,84,.45);box-shadow:none}
#pauseMenu .btn.quit{background:rgba(255,83,72,.12);color:#ff9a8f;border:1px solid rgba(255,83,72,.5);box-shadow:none}
#pauseMenu .p-note{font-size:10.5px;font-weight:700;color:rgba(255,220,170,.45);margin-top:2px}
@media(max-width:640px){#pauseBtn{width:48px;height:48px;bottom:calc(24px + env(safe-area-inset-bottom))}}
</style>""")

# P9: JS — pause logic after retryBtn handler
P('js-pause',
"""else{retryBtn.dataset.armed='1';retryBtn.textContent='تأیید؟ ضربه دوم';retryBtn.classList.add('armed');clearTimeout(armTO);armTO=setTimeout(resetRetry,2500);}});""",
"""else{retryBtn.dataset.armed='1';retryBtn.textContent='تأیید؟ ضربه دوم';retryBtn.classList.add('armed');clearTimeout(armTO);armTO=setTimeout(resetRetry,2500);}});

/* ================= منوی توقف v4.1 ================= */
var elPauseMenu=$('pauseMenu'),pauseOpen=false;
function openPause(){if(state!==ST.PLAY||pauseGame||pauseOpen)return;pauseOpen=true;pauseGame=true;held=false;aimId=null;autoFired=false;saveRun();var pi=$('pauseInfo');if(pi)pi.textContent=(campStage?'مرحله '+faNum(campStage)+' · ':'')+'امتیاز '+faNum(score)+' · سطح '+faNum(level);musicSet(false);sfxUI();elPauseMenu.classList.remove('off');}
function closePause(){if(!pauseOpen)return;pauseOpen=false;pauseGame=false;elPauseMenu.classList.add('off');last=performance.now();if(state===ST.PLAY)musicSet(true);sfxUI();}
function pauseRestart(){if(!pauseOpen)return;pauseOpen=false;pauseGame=false;elPauseMenu.classList.add('off');resetRetry();lastStart=0;if(campStage)startCampaign(campStage-1);else start();}
function pauseExit(){if(!pauseOpen)return;pauseOpen=false;pauseGame=false;elPauseMenu.classList.add('off');toMenu();}
$('pauseBtn').addEventListener('pointerdown',function(e){e.stopPropagation();});
$('pauseBtn').addEventListener('click',function(e){e.stopPropagation();initAudio();openPause();});
$('pauseResume').addEventListener('click',function(e){e.stopPropagation();closePause();});
$('pauseRestart').addEventListener('click',function(e){e.stopPropagation();initAudio();sfxUI();pauseRestart();});
$('pauseExit').addEventListener('click',function(e){e.stopPropagation();pauseExit();});
elPauseMenu.addEventListener('click',function(e){if(e.target===elPauseMenu)closePause();});
addEventListener('keydown',function(e){if(e.key==='Escape'){if(pauseOpen)closePause();else if(state===ST.PLAY&&!pauseGame)openPause();}});""")

# P10: version strings
P('title-ver', '<title>میدان غروب ۲ | نسخهٔ ۴ طلایی</title>', '<title>میدان غروب ۲ | نسخهٔ ۴٫۱ طلایی</title>')
P('foot-ver', '<span>V4 GOLD</span>', '<span>V4.1 GOLD</span>')

# ---------------- apply ----------------
fail = False
for name, old, new, expect in patches:
    cnt = html.count(old)
    if cnt != expect:
        print(f"❌ [{name}] expected {expect} occurrence(s), found {cnt} — ABORT")
        fail = True
if fail:
    sys.exit(1)

for name, old, new, expect in patches:
    html = html.replace(old, new)
    print(f"✅ [{name}] applied")

with open(SRC, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nsize: {orig_len/1e6:.3f}MB -> {len(html)/1e6:.3f}MB")

# sanity checks
for token in ['IS_MOBILE', 'adaptPR', 'pauseBtn', 'pauseMenu', 'openPause', 'V4.1 GOLD', 'id="pause-system-v41"']:
    c = html.count(token)
    print(f"  sanity '{token}': {c}")
    if c == 0:
        print("❌ MISSING TOKEN — aborting sync"); sys.exit(2)

# sync copies
copies = [
    '/home/z/my-project/repo/docs/index.html',
    '/home/z/my-project/repo/apk-project/www/index.html',
    '/home/z/my-project/apk/www/index.html',
]
for dst in copies:
    shutil.copyfile(SRC, dst)
    print(f"📦 synced -> {dst}")
print("\nALL DONE ✓")
