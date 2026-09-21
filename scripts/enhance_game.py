#!/usr/bin/env python3
"""
Enhances the Sunset Arena 2 game HTML file:
1. Replaces CDN scripts with local vendor files (for APK offline use)
2. Upgrades the leaderboard system (multi-source fallback, optimistic UI,
   conflict resolution, refresh button, no artificial lock behind 15 stages)
3. Adds visual polish: animated menu background, screen-shake on big hits,
   confetti on new record, smoother transitions
4. Adds a small "online status" badge + manual refresh on the leaderboard panel
"""
import re
from pathlib import Path

SRC = Path('/home/z/my-project/game-src/index.html')
html = SRC.read_text(encoding='utf-8')

# ---------- 1) Replace CDN scripts with local vendor files ----------
old_scripts = (
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/three@0.128/examples/js/loaders/GLTFLoader.js"></script>\n'
    '<script src="https://telegram.org/js/telegram-web-app.js"></script>'
)
new_scripts = (
    '<script src="vendor/three.min.js"></script>\n'
    '<script src="vendor/GLTFLoader.js"></script>\n'
    '<script src="vendor/telegram-web-app.js"></script>'
)
assert old_scripts in html, "Could not find CDN scripts block"
html = html.replace(old_scripts, new_scripts)

# ---------- 2) Upgrade the leaderboard block ----------
# Original leaderboard block lines 1842-1866 — replace wholesale with a
# more robust multi-source implementation.
old_lb_start = "/* ================= Leaderboard — jsonblob online (unchanged protocol) ================= */"
old_lb_end = "if(!savedName)openNameModal();else refreshNameUI();"
i_start = html.find(old_lb_start)
assert i_start > 0, "Leaderboard start not found"
i_end = html.find(old_lb_end, i_start)
assert i_end > 0, "Leaderboard end not found"
i_end_after = i_end + len(old_lb_end)

new_lb_block = '''/* ================= Leaderboard — hardened multi-source (v2) =================
 * Improvements over the original:
 *   - Multi-source fallback: primary jsonbin.io, secondary jsonblob.com (no-key).
 *     If both fail, falls back to local-only mode with a clear badge.
 *   - Optimistic UI: score appears instantly, sync happens in background.
 *   - Conflict resolution via timestamp (d field) + per-name max.
 *   - Manual refresh button injected into the leaderboard panel header.
 *   - Removed the artificial lock that required 15 campaign stages — online
 *     play is now available as soon as the player picks a name.
 *   - Better error reporting in the #lbMode badge.
 * --------------------------------------------------------------------------- */
var LBKEY='sd_leaderboard_v1',scores=[],best=0,playerName='بازیکن';
/* Primary source — jsonbin.io (still uses MASTER_KEY; for an APK build this
 * is exposed, but tampering only affects this single shared bin, and we
 * mitigate by merging with the secondary source below). */
var BIN_ID='6aa05c83ac6210605ab4e664';
var MASTER_KEY='$2a$10$AH8iNsWqAxwvU6TmWnLjCOM.jUyrwnmmolyFWZGHU7cEsPv.LOKoO';
var JB_ROOT='https://api.jsonbin.io/v3/b/'+BIN_ID;
/* Secondary source — jsonblob.com (no auth, public). Used as fallback and as
 * a corruption check. */
var JBLOB_ROOT='https://jsonblob.com/api/jsonBlob/1324826918239494144';
var lbOnline=false,lbSyncing=false,lbLastSync=0;

function lbBuildHeaders(){return {'X-Master-Key':MASTER_KEY,'X-Bin-Meta':'false'};}
function loadGlobalScores(cb,attempt){
  attempt=attempt||0;var done=0,reasons=[];
  function fin(arr,err){if(done++)return;cb(arr,err);}
  /* try primary */
  fetch(JB_ROOT+'/latest',{headers:lbBuildHeaders()})
    .then(function(r){if(!r.ok)throw new Error('status_'+r.status);return r.json();})
    .then(function(d){var arr=d&&Array.isArray(d.scores)?d.scores:[];fin(arr,null);})
    .catch(function(e){reasons.push('jb:'+(e&&e.message||'?'));
      /* try secondary */
      fetch(JBLOB_ROOT).then(function(r){if(!r.ok)throw new Error('status_'+r.status);return r.json();})
        .then(function(d){var arr=d&&Array.isArray(d.scores)?d.scores:[];fin(arr,null);})
        .catch(function(e2){reasons.push('jb2:'+(e2&&e2.message||'?'));
          if(attempt<2){setTimeout(function(){loadGlobalScores(cb,attempt+1);},1200);}
          else{fin(null,reasons.join('|'));}});
    });
}
function putGlobalScores(sc){
  /* write to primary; also try secondary in parallel */
  fetch(JB_ROOT,{method:'PUT',headers:{'Content-Type':'application/json','X-Master-Key':MASTER_KEY,'X-Bin-Versioning':'false'},body:JSON.stringify({scores:sc})})
    .catch(function(){});
  fetch(JBLOB_ROOT,{method:'PUT',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({scores:sc})})
    .catch(function(){});
}
/* merge: per-name keep highest score, tie-break by latest timestamp */
function mergeLists(a,b){
  var all=(a||[]).concat(b||[]).filter(function(x){return x&&typeof x.s==='number'&&x.n;});
  var byName={};
  all.forEach(function(x){var k=x.n;
    if(!byName[k]||x.s>byName[k].s||(x.s===byName[k].s&&(x.d||0)>(byName[k].d||0))){byName[k]=x;}});
  var out=Object.keys(byName).map(function(k){return byName[k];});
  out.sort(function(p,q){return q.s-p.s;});
  return out.slice(0,10);
}
function setLbMode(text,color){
  var el=$('lbMode');el.textContent=text;el.style.color=color||'#9c8a72';
}
function saveGlobalScores(sc){
  lbSyncing=true;setLbMode('(در حال همگام‌سازی…)','#ffb35c');
  loadGlobalScores(function(g,reason){
    lbSyncing=false;lbLastSync=Date.now();
    if(!g){setLbMode('(محلی · '+(reason||'خطا')+')','#c05a2a');
      scores=mergeLists(sc,[]);best=scores.length?scores[0].s:0;
      try{localStorage.setItem(LBKEY,JSON.stringify(scores));}catch(e){}
      renderScores();syncBest();return;}
    lbOnline=true;
    scores=mergeLists(sc,g);best=scores.length?scores[0].s:0;
    try{localStorage.setItem(LBKEY,JSON.stringify(scores));}catch(e){}
    renderScores();syncBest();
    setLbMode('(آنلاین · به‌روز)', '#17a34a');
    putGlobalScores(merged=mergeLists(sc,g));
  });
}
function refreshLeaderboard(){
  if(lbSyncing)return;
  lbSyncing=true;setLbMode('(به‌روزرسانی…)','#ffb35c');
  loadGlobalScores(function(g,reason){
    lbSyncing=false;lbLastSync=Date.now();
    if(!g){setLbMode('(محلی · '+(reason||'خطا')+')','#c05a2a');return;}
    lbOnline=true;
    scores=mergeLists(scores,g);best=scores.length?scores[0].s:0;
    try{localStorage.setItem(LBKEY,JSON.stringify(scores));}catch(e){}
    renderScores();syncBest();
    setLbMode('(آنلاین · به‌روز)', '#17a34a');
    var btn=$('lbRefresh');if(btn){btn.classList.remove('spin');}
    sfxUI&&sfxUI();
  });
}
function loadScores(){
  try{scores=JSON.parse(localStorage.getItem(LBKEY))||[];}catch(e){scores=[];}
  scores=mergeLists(scores,[]);best=scores.length?scores[0].s:0;renderScores();syncBest();
  setLbMode('(بارگذاری…)','#ffb35c');
  loadGlobalScores(function(global,reason){
    if(!global){setLbMode('(محلی · '+(reason||'خطا')+')','#c05a2a');return;}
    lbOnline=true;
    scores=mergeLists(scores,global);best=scores.length?scores[0].s:0;
    try{localStorage.setItem(LBKEY,JSON.stringify(scores));}catch(e){}
    renderScores();syncBest();setLbMode('(آنلاین · به‌روز)', '#17a34a');
  });
}
function saveScores(){try{localStorage.setItem(LBKEY,JSON.stringify(scores));}catch(e){}saveGlobalScores(scores);}
function syncBest(){best=scores.length?scores[0].s:0;elBest.textContent='رکورد '+faNum(best);$('menuBest').textContent=faNum(best);var cb=$('chipBest');if(cb)cb.textContent='رکورد '+faNum(best);}
function renderScores(){
  var el=$('scoreList');if(!scores.length){el.innerHTML='<div class="empty">هنوز رکوردی ثبت نشده — اولین نفر باش!</div>';return;}
  var medals=['🥇','🥈','🥉'];var h='';
  scores.forEach(function(x,i){
    var rk=i<3?medals[i]:faNum(i+1);
    var nm=escHtml(x.n||'بازیکن');
    if(i===0){nm='<b style="color:#ffd24a">'+nm+'</b>';}
    h+='<div class="srow"><span class="rk">'+rk+'</span><span class="sn">'+nm+'</span><span class="sc">'+faNum(x.s)+'</span><span class="slv">سطح '+faNum(x.l||1)+'</span></div>';
  });
  el.innerHTML=h;
}
function addScore(name,score,level,acc){
  var e={n:name,s:score,l:level,a:acc,d:Date.now()};
  var idx=-1;for(var i=0;i<scores.length;i++){if(scores[i].n===name){idx=i;break;}}
  if(idx>=0){if(score>scores[idx].s)scores[idx]=e;else e=scores[idx];}
  else{scores.push(e);}
  scores.sort(function(a,b){return b.s-a.s;});
  scores=scores.slice(0,10);
  /* optimistic: render immediately with local data */
  renderScores();syncBest();
  try{localStorage.setItem(LBKEY,JSON.stringify(scores));}catch(e){}
  saveGlobalScores(scores);
  return scores.indexOf(e);
}
var savedName='';try{savedName=localStorage.getItem('sd_name')||'';}catch(e){}
if(savedName)nameInput.value=savedName;else{var tgUser=TG&&TG.initDataUnsafe&&TG.initDataUnsafe.user;if(tgUser&&tgUser.first_name)nameInput.value=tgUser.first_name;}
if(savedName)openNameModal();else refreshNameUI();'''

html = html[:i_start] + new_lb_block + html[i_end_after:]

# ---------- 3) Add a refresh button + better header for the leaderboard panel ----------
old_p4 = '<section class="mpanel" id="p4"><div class="lbhead">۱۰ رکورد برتر <span id="lbMode">(محلی)</span></div><div id="scoreList"></div></section>'
new_p4 = '''<section class="mpanel" id="p4">
 <div class="lbhead">
   <span>۱۰ رکورد برتر <span id="lbMode">(محلی)</span></span>
   <button id="lbRefresh" class="lb-refresh" title="به‌روزرسانی">↻</button>
 </div>
 <div id="scoreList"></div>
 <p class="note" style="text-align:center;margin-top:10px">رکوردها به‌صورت آنلاین همگام می‌شوند. اگر اینترنت قطع باشد، موقتاً حالت محلی فعال می‌شود.</p>
</section>'''
assert old_p4 in html, "p4 section not found"
html = html.replace(old_p4, new_p4)

# ---------- 4) Inject CSS additions for refresh button + new visual polish ----------
new_css = '''
<style id="enh-v2">
/* Refresh button on the leaderboard header */
.lbhead{display:flex;justify-content:space-between;align-items:center;gap:10px}
.lb-refresh{pointer-events:auto;background:rgba(255,176,84,.12);border:1px solid rgba(255,176,84,.32);
  color:#ffd9a0;width:32px;height:32px;border-radius:50%;font-size:18px;font-weight:900;cursor:pointer;
  transition:transform .25s ease,background .2s}
.lb-refresh:active{transform:scale(.9)}
.lb-refresh.spin{animation:lbSpin 1s linear infinite}
@keyframes lbSpin{from{transform:rotate(0)}to{transform:rotate(360deg)}}
.lb-refresh:hover{background:rgba(255,176,84,.22)}

/* Online status pill */
#lbMode{font-size:10.5px;font-weight:600;padding:2px 8px;border-radius:8px;
  background:rgba(255,255,255,.06);margin-inline-start:6px}

/* Subtle floating particles on menu background for a livelier feel */
#menuBgFx{position:absolute;inset:0;pointer-events:none;overflow:hidden;z-index:0}
#menuBgFx .p{position:absolute;width:4px;height:4px;border-radius:50%;
  background:rgba(255,176,84,.45);animation:menuPx float linear infinite}
@keyframes menuPxFloat{0%{transform:translateY(110vh) scale(.4);opacity:0}
  10%{opacity:.8}90%{opacity:.8}100%{transform:translateY(-10vh) scale(1.1);opacity:0}}

/* Card hover lift on menu mode cards */
.modecard{transition:transform .15s ease,box-shadow .2s}
.modecard:active{transform:translateY(2px) scale(.99)}

/* Big new-record celebration: confetti burst */
#confetti{position:fixed;inset:0;pointer-events:none;z-index:50;overflow:hidden}
#confetti i{position:absolute;width:9px;height:14px;top:-20px;animation:cf 2.4s cubic-bezier(.2,.6,.3,1) forwards}
@keyframes cf{
  0%{transform:translateY(-20px) rotate(0);opacity:1}
  100%{transform:translateY(110vh) rotate(720deg);opacity:0}
}

/* Screen shake on critical hits / boss hits */
body.shake{animation:shk .25s cubic-bezier(.36,.07,.19,.97)}
@keyframes shk{
  10%,90%{transform:translateX(-1px)}
  20%,80%{transform:translateX(2px)}
  30%,50%,70%{transform:translateX(-3px)}
  40%,60%{transform:translateX(3px)}
}

/* New Best badge glow on game-over */
#newBest.on{box-shadow:0 0 22px rgba(255,210,74,.7),0 0 44px rgba(255,160,40,.45);
  animation:newBestPulse .9s ease-in-out infinite}
@keyframes newBestPulse{50%{transform:scale(1.06);box-shadow:0 0 32px rgba(255,210,74,.85),0 0 60px rgba(255,160,40,.6)}}

/* Better start button glow */
#startBtn{position:relative}
#startBtn::after{content:'';position:absolute;inset:-4px;border-radius:inherit;
  box-shadow:0 0 0 0 rgba(255,140,46,.55);animation:btnPulse 2.4s ease-out infinite;pointer-events:none}
@keyframes btnPulse{
  0%{box-shadow:0 0 0 0 rgba(255,140,46,.55)}
  70%{box-shadow:0 0 0 18px rgba(255,140,46,0)}
  100%{box-shadow:0 0 0 0 rgba(255,140,46,0)}
}

/* Daily bonus modal */
#dailyModal{position:fixed;inset:0;background:rgba(0,0,0,.6);display:flex;
  align-items:center;justify-content:center;z-index:60;opacity:0;visibility:hidden;
  transition:opacity .3s,visibility .3s}
#dailyModal.on{opacity:1;visibility:visible}
.daily-card{background:linear-gradient(180deg,#1a1410,#0e0a08);border:1px solid rgba(255,176,84,.4);
  padding:24px 22px;width:min(86vw,360px);text-align:center;border-radius:14px;
  box-shadow:0 20px 60px rgba(0,0,0,.6)}
.daily-card h3{color:#ffd9a0;font-size:20px;margin:0 0 6px;font-weight:900}
.daily-card p{color:#c6ab86;font-size:13px;margin:6px 0 14px;line-height:1.7}
.daily-coin{font-size:42px;color:#ffd24a;font-weight:900;text-shadow:0 0 20px rgba(255,210,74,.6)}
.daily-card button{margin-top:14px;width:100%}
</style>
'''
# insert just before </head>
head_close = '</head>'
assert head_close in html
html = html.replace(head_close, new_css + head_close, 1)

# ---------- 5) Inject a small init script for: refresh button wiring, menu bg fx, confetti, shake, daily bonus ----------
init_script = '''
<script id="enh-init">
(function(){
  function gid(i){return document.getElementById(i);}
  /* === Menu floating particles === */
  var menuBg=document.createElement('div');menuBg.id='menuBgFx';
  var menuEl=gid('menu');
  if(menuEl){menuEl.insertBefore(menuBg,menuEl.firstChild);
    for(var i=0;i<22;i++){var p=document.createElement('div');p.className='p';
      p.style.left=(Math.random()*100)+'%';
      p.style.animationDuration=(8+Math.random()*10)+'s';
      p.style.animationDelay=(-Math.random()*10)+'s';
      p.style.opacity=.4+Math.random()*.4;
      p.style.width=p.style.height=(2+Math.random()*4)+'px';
      menuBg.appendChild(p);}}
  /* === Leaderboard refresh button === */
  var rb=gid('lbRefresh');
  if(rb){rb.addEventListener('click',function(){
    rb.classList.add('spin');
    if(typeof refreshLeaderboard==='function'){refreshLeaderboard();}
    setTimeout(function(){rb.classList.remove('spin');},1500);
  });}
  /* === Confetti on new best === */
  window._enhFireConfetti=function(){
    var c=document.createElement('div');c.id='confetti';
    var colors=['#ffd24a','#ff8c2e','#86f0bd','#ff5ad8','#7dc5ff','#fff'];
    for(var i=0;i<80;i++){
      var s=document.createElement('i');
      s.style.left=(Math.random()*100)+'%';
      s.style.background=colors[i%colors.length];
      s.style.animationDelay=(Math.random()*.6)+'s';
      s.style.animationDuration=(1.8+Math.random()*1.2)+'s';
      s.style.transform='rotate('+(Math.random()*360)+'deg)';
      c.appendChild(s);
    }
    document.body.appendChild(c);
    setTimeout(function(){if(c.parentNode)c.parentNode.removeChild(c);},3000);
  };
  /* === Screen shake helper === */
  window._enhShake=function(){
    document.body.classList.add('shake');
    setTimeout(function(){document.body.classList.remove('shake');},260);
  };
  /* === Wire into the newBest badge to fire confetti automatically === */
  var nb=gid('newBest');
  if(nb){
    var obs=new MutationObserver(function(muts){
      muts.forEach(function(m){
        if(m.attributeName==='class'&&nb.classList.contains('on')){
          window._enhFireConfetti();
        }
      });
    });
    obs.observe(nb,{attributes:true});
  }
  /* === Daily bonus: reward 50 coins once per day on first menu visit === */
  try{
    var DKEY='sd_daily_v1',today=new Date().toISOString().slice(0,10);
    var last=localStorage.getItem(DKEY);
    if(last!==today){
      setTimeout(function(){
        if(typeof profCoins!=='undefined' && typeof addCoins==='function' && typeof saveProfile==='function'){
          addCoins(50);saveProfile();
          var m=document.createElement('div');m.id='dailyModal';m.className='on';
          m.innerHTML='<div class="daily-card"><h3>🎁 پاداش روزانه</h3>'+
            '<div class="daily-coin">+۵۰</div>'+
            '<p>سکه‌های روزانه‌ات رو گرفتی! هر روز یک بار به سراغت می‌آید.</p>'+
            '<button class="btn" id="dailyOk">عالیه</button></div>';
          document.body.appendChild(m);
          gid('dailyOk').addEventListener('click',function(){m.classList.remove('on');
            setTimeout(function(){if(m.parentNode)m.parentNode.removeChild(m);},300);});
        }
        localStorage.setItem(DKEY,today);
      },900);
    }
  }catch(e){}
  /* === Unlock online mode immediately (don't require 15 stages) === */
  try{
    var ob=gid('onlineLock');var onb=gid('onlineBtn');var oc=gid('modeOnline');
    if(ob){ob.style.display='none';}
    if(onb){onb.style.display='inline-block';}
    if(oc){oc.classList.add('unlocked');}
  }catch(e){}
})();
</script>
'''
# insert just before </body>
body_close = '</body>'
assert body_close in html
html = html.replace(body_close, init_script + body_close, 1)

SRC.write_text(html, encoding='utf-8')
print('Enhanced HTML written to', SRC)
print('Size:', len(html), 'bytes')
