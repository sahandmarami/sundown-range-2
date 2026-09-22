#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sundown Range II — v4 upgrade patcher
Applies all v4 enhancements to the original game_raw.html → index.html
Each patch asserts exact-match count; aborts loudly on any mismatch.
"""
import sys, urllib.request, ssl

SRC = '/home/z/my-project/game/game_raw.html'
OUT = '/home/z/my-project/game/index.html'
html = open(SRC, encoding='utf-8').read()
applied = []

def rep(old, new, label, count=1):
    global html
    n = html.count(old)
    if n != count:
        print(f'FAIL [{label}]: expected {count} occurrence(s), found {n}')
        sys.exit(1)
    html = html.replace(old, new)
    applied.append(label)
    print(f'OK   [{label}]')

def insert_before(marker, block, label):
    global html
    i = html.find(marker)
    if i < 0 or html.count(marker) != 1:
        print(f'FAIL [{label}]: marker not unique/found')
        sys.exit(1)
    html = html[:i] + block + html[i:]
    applied.append(label)
    print(f'OK   [{label}]')

# ============================================================
# 1) NEW LEADERBOARD v4 MODULE (replaces whole old LB section)
# ============================================================
LB_START = "/* ================= Leaderboard — jsonblob online (unchanged protocol) ================= */"
LB_END = "var savedName='';"
i = html.find(LB_START); j = html.find(LB_END)
if i < 0 or j <= i:
    print('FAIL [LB block markers]'); sys.exit(1)

LB_NEW = r"""/* ================= Leaderboard v4 — سرویس ابری امن با اعتبارسنجی ================= */
var LBKEY='sd_leaderboard_v1',scores=[],best=0,playerName='بازیکن';
var BIN_ID='6ab1a019ac6210605ae72028'; /* bin نسخهٔ ۴ */
var OLD_BIN='6aa05c83ac6210605ab4e664'; /* bin قدیمی — فقط برای انتقال داده (خواندنی) */
var MASTER_KEY='$2a$10$AH8iNsWqAxwvU6TmWnLjCOM.jUyrwnmmolyFWZGHU7cEsPv.LOKoO';
var JB_ROOT='https://api.jsonbin.io/v3/b/'+BIN_ID;
var LB_MAX=10,LB_SANITY=5000000,LB_PUSH_CD=25000;
var LB_NAME_BLOCK=['http','www.','.ru','.xyz','admin','mod ','fuck','sex','porn','nigg','کیر','جنده','کونی'];
var lbOnline=false,lbTriedOld=false,lastPushT=0,pushTO=0,pushPending=null;
function lbCleanName(n){n=String(n||'').replace(/[<>&"']/g,'').trim().slice(0,16);if(!n)n='بازیکن';var low=n.toLowerCase();for(var i=0;i<LB_NAME_BLOCK.length;i++){if(low.indexOf(LB_NAME_BLOCK[i])>=0){n='بازیکن';break;}}return n;}
function lbCleanScore(s){s=+s;if(!isFinite(s)||s<0)s=0;return Math.min(LB_SANITY,Math.round(s));}
function mergeLists(a,b){var all=(a||[]).concat(b||[]).filter(function(x){return x&&typeof x.s==='number'&&x.n;});var byName={};all.forEach(function(x){x.n=lbCleanName(x.n);x.s=lbCleanScore(x.s);if(!byName[x.n]||x.s>byName[x.n].s)byName[x.n]=x;});var out=Object.keys(byName).map(function(k){return byName[k];});out.sort(function(p,q){return q.s-p.s;});return out.slice(0,LB_MAX);}
function lbStatus(mode,reason){var el=$('lbMode');if(el){if(mode==='online'){el.textContent='(آنلاین · v4)';el.style.color='#17a34a';}else if(mode==='local'){el.textContent='(محلی · '+reason+')';el.style.color='#c05a2a';}else{el.textContent='(در حال دریافت…)';el.style.color='#b8a88a';}}}
function lbMyRank(){if(!playerName)return null;for(var i=0;i<scores.length;i++){if(scores[i].n===playerName)return i+1;}return null;}
function lbRenderRank(){var mr=$('myRank');if(!mr)return;var r=lbMyRank();if(r===null){mr.textContent=lbOnline?'رتبهٔ جهانی تو: بیرون از ده برتر — وارد شو!':'';}else{mr.textContent='رتبهٔ جهانی تو: '+faNum(r);}}
function loadGlobalScores(cb,attempt){attempt=attempt||0;var reason='neterr';
 fetch(JB_ROOT+'/latest',{headers:{'X-Master-Key':MASTER_KEY,'X-Bin-Meta':'false'}}).then(function(r){if(!r.ok){reason='status_'+r.status;throw 0;}return r.json();}).then(function(d){var rec=d&&d.record?d.record:d;var arr=rec&&Array.isArray(rec.scores)?rec.scores:[];cb(arr,null);}).catch(function(){
  if(attempt<2){setTimeout(function(){loadGlobalScores(cb,attempt+1);},1200+attempt*900);return;}
  if(!lbTriedOld){lbTriedOld=true;fetch('https://api.jsonbin.io/v3/b/'+OLD_BIN+'/latest',{headers:{'X-Master-Key':MASTER_KEY,'X-Bin-Meta':'false'}}).then(function(r){return r.ok?r.json():null;}).then(function(d2){var rec2=d2&&d2.record?d2.record:d2;var arr2=rec2&&Array.isArray(rec2.scores)?rec2.scores:[];if(arr2.length)cb(arr2,'old');else cb(null,reason);}).catch(function(){cb(null,reason);});return;}
  cb(null,reason);});}
function putGlobalScores(sc){var now=Date.now();
 if(now-lastPushT<LB_PUSH_CD){pushPending=sc;clearTimeout(pushTO);pushTO=setTimeout(function(){var p=pushPending;pushPending=null;if(p)putGlobalScores(p);},LB_PUSH_CD-(now-lastPushT)+600);return;}
 lastPushT=Date.now();
 fetch(JB_ROOT,{method:'PUT',headers:{'Content-Type':'application/json','X-Master-Key':MASTER_KEY,'X-Bin-Versioning':'false'},body:JSON.stringify({v:2,scores:sc,ts:Date.now()})}).then(function(r){if(!r.ok)throw 0;}).catch(function(){lastPushT=0;});}
function saveGlobalScores(sc){loadGlobalScores(function(g){if(g){var merged=mergeLists(sc,g);scores=merged;best=scores.length?scores[0].s:0;try{localStorage.setItem(LBKEY,JSON.stringify(scores));}catch(e){}renderScores();syncBest();lbRenderRank();putGlobalScores(merged);}});}
function loadScores(){try{scores=JSON.parse(localStorage.getItem(LBKEY))||[];}catch(e){scores=[];}
 scores=mergeLists(scores,[]);best=scores.length?scores[0].s:0;renderScores();syncBest();
 loadGlobalScores(function(global,reason){
  if(!global){lbStatus('local',reason||'neterr');lbRenderRank();return;}
  scores=mergeLists(scores,global);best=scores.length?scores[0].s:0;
  try{localStorage.setItem(LBKEY,JSON.stringify(scores));}catch(e){}
  lbOnline=true;renderScores();syncBest();lbStatus('online');lbRenderRank();});}
function saveScores(){try{localStorage.setItem(LBKEY,JSON.stringify(scores));}catch(e){}saveGlobalScores(scores);}
function syncBest(){best=scores.length?scores[0].s:0;elBest.textContent='رکورد '+faNum(best);$('menuBest').textContent=faNum(best);var cb=$('chipBest');if(cb)cb.textContent='رکورد '+faNum(best);}
function renderScores(){var el=$('scoreList');if(!scores.length){el.innerHTML='<div class="empty">هنوز رکوردی ثبت نشده — اولین نفر باش!</div>';return;}
 var medals=['🥇','🥈','🥉'];var h='';scores.forEach(function(x,i){var rk=i<3?medals[i]:faNum(i+1);var me=x.n===playerName?' me':'';
  h+='<div class="srow'+me+'"><span class="rk">'+rk+'</span><span class="sn">'+escHtml(x.n||'بازیکن')+'</span><span class="sc">'+faNum(x.s)+'</span><span class="slv">سطح '+faNum(x.l||1)+'</span></div>';});el.innerHTML=h;}
function addScore(name,score,level,acc){name=lbCleanName(name);score=lbCleanScore(score);var e={n:name,s:score,l:level,a:acc,d:Date.now()};var idx=-1;for(var i=0;i<scores.length;i++){if(scores[i].n===name){idx=i;break;}}if(idx>=0){if(score>scores[idx].s)scores[idx]=e;else e=scores[idx];}else{scores.push(e);}scores.sort(function(a,b){return b.s-a.s;});scores=scores.slice(0,LB_MAX);saveScores();renderScores();syncBest();return scores.indexOf(e);}
"""
html = html[:i] + LB_NEW + html[j:]
applied.append('LB v4 module')
print('OK   [LB v4 module]')

# ============================================================
# 2) QUEST + new SFX + helper functions (before campaign section)
# ============================================================
QUEST_BLOCK = r"""/* ================= چالش روزانه + جلوه‌های نسخهٔ ۴ ================= */
function sfxHeadGold(){tone({type:'sine',f0:2093,dur:.14,vol:.1,echo:true});tone({type:'sine',f0:2637,dur:.16,vol:.07,at:.04,echo:true});}
function sfxFeverRiser(){nz({type:'bandpass',f0:300,f1:3800,q:1.6,dur:.7,vol:.16,echo:true});tone({type:'sawtooth',f0:220,f1:880,dur:.6,vol:.08,echo:true});}
function sfxRecord(){[523,659,784,1046,1318].forEach(function(f,i){tone({type:'triangle',f0:f,dur:.4,vol:.15,at:i*.11,echo:true});});tone({type:'sine',f0:1046,f1:2093,dur:.7,vol:.09,at:.55,echo:true});nz({type:'highpass',f0:5000,dur:.5,vol:.05,at:.55});}
function sfxChest(){tone({type:'triangle',f0:392,dur:.12,vol:.18});tone({type:'triangle',f0:523,dur:.12,vol:.18,at:.1});tone({type:'sine',f0:1046,f1:1568,dur:.3,vol:.14,at:.2,echo:true});}
function sfxQuest(){[659,784,988].forEach(function(f,i){tone({type:'sine',f0:f,dur:.25,vol:.15,at:i*.09,echo:true});});}
function goldFlash(){var g=$('gflash');if(!g)return;g.classList.remove('go');void g.offsetWidth;g.classList.add('go');}
function encMsg(sc,bst,acc,mc){if(bst>0&&sc>bst)return 'رکورد جدید — تو افسانه‌ای!';if(bst>0&&sc>=bst*.85)return 'فقط یک قدم تا رکورد — یک راند دیگر!';if(acc>=70)return 'دقتت عالی بود؛ حالا سریع‌تر بزن!';if(mc>=10)return 'زنجیرهٔ '+faNum(mc)+'تایی — تکان‌دهنده بود!';return 'هر ثانیه می‌ارزد — نشانه بگیر و دوباره تلاش کن!';}
var DKEY='sd_daily_v1',quest=null;
var QTYPES=[
 {k:'head',verb:'هدشات بزن',unit:'هدشات',base:6,add:7,rw:120},
 {k:'score',verb:'به امتیاز برس',unit:'امتیاز',base:1200,add:10,rw:150},
 {k:'combo',verb:'زنجیره بساز',unit:'ضرب',base:5,add:6,rw:130},
 {k:'kills',verb:'هدف حذف کن',unit:'حذف',base:10,add:16,rw:120}];
function todayStr(){var d=new Date();return d.getFullYear()+'-'+(d.getMonth()+1)+'-'+d.getDate();}
function questInit(){var s=todayStr(),h=0;for(var i=0;i<s.length;i++)h=((h*31+s.charCodeAt(i))>>>0);
 var q=QTYPES[h%QTYPES.length],goal=q.base+((h>>4)%q.add);
 quest={d:s,k:q.k,goal:goal,prog:0,done:false,claimed:false,unit:q.unit,rw:q.rw,verb:q.verb};questSave();}
function questLoad(){var ok=false;try{var q=JSON.parse(localStorage.getItem(DKEY)||'null');if(q&&q.d===todayStr()){quest=q;ok=true;}}catch(e){}
 if(!ok)questInit();questRender();}
function questSave(){try{localStorage.setItem(DKEY,JSON.stringify(quest));}catch(e){}}
function questRoundStart(){if(!quest)return;if(!quest.done){quest.prog=0;questSave();}questRender();}
function questProg(kind,n,set){if(!quest||quest.done)return;if(kind!==quest.k)return;
 quest.prog=set?Math.max(quest.prog,n):(quest.prog+n);
 if(quest.prog>=quest.goal){quest.prog=quest.goal;quest.done=true;announce('چالش روزانه کامل شد!');sfxQuest();hap('n','success');}
 questSave();questRender();}
function questRender(){var d=$('questDesc'),f=$('questFill'),t=$('questProgTxt'),b=$('questClaim'),r=$('questReward');if(!d)return;
 d.innerHTML='<b>'+escHtml(quest.verb)+'</b> '+faNum(quest.goal)+(quest.unit?' '+escHtml(quest.unit):'')+' — در یک راند';
 if(r)r.innerHTML='<span class="coin-icon coin-xs" aria-hidden="true"></span>'+faNum(quest.rw);
 var pc=quest.goal?Math.min(100,Math.round(quest.prog/quest.goal*100)):0;
 if(f)f.style.width=pc+'%';
 if(t)t.textContent=faNum(quest.prog)+' / '+faNum(quest.goal);
 if(b){if(quest.done&&!quest.claimed){b.style.display='inline-block';b.textContent='دریافت '+faNum(quest.rw)+' سکه ◀';}else b.style.display='none';}
 var card=$('questCard');if(card)card.classList.toggle('qdone',!!quest.done);}
$('questClaim').addEventListener('click',function(e){e.stopPropagation();initAudio();sfxUI();questClaim();});
function questClaim(){if(!quest||!quest.done||quest.claimed)return;quest.claimed=true;addCoins(quest.rw);sfxChest();announce('+'+faNum(quest.rw)+' سکه از چالش روزانه!');hap('n','success');questSave();questRender();}

"""
insert_before('/* ================= کمپین آموزشی ۱۵ مرحله‌ای ================= */', QUEST_BLOCK, 'quest+sfx module')

# ============================================================
# 3) GAMEPLAY JUICE
# ============================================================
rep("else if(res.head){hitmark('head');sfxHead();sfxPaper();addShake(.14);burst(pt,{color:0xffb0f0,count:22,speed:8,size:.06});}",
    "else if(res.head){hitmark('head');sfxHead();sfxPaper();sfxHeadGold();addShake(.2);slowmo(.09,.55);burst(pt,{color:0xffd24a,count:26,speed:10,size:.07,life:.8});burst(pt,{color:0xfff0b8,count:12,speed:4,size:.05});}",
    'headshot juice')

rep("if(res.kind==='kill'){kills++;if(res.head)heads++;lvProg+=.5;}",
    "if(res.kind==='kill'){kills++;if(res.head)heads++;lvProg+=.5;questProg('kills',1);if(res.head)questProg('head',1);}",
    'quest hooks kill/head')

rep("if(builds){combo++;maxCombo=Math.max(maxCombo,combo);sfxComboHit(combo);}",
    "if(builds){combo++;maxCombo=Math.max(maxCombo,combo);sfxComboHit(combo);questProg('combo',maxCombo,true);}",
    'quest hook combo')

rep("if(f!==feverOn){feverOn=f;if(f){announce('حالت آتش!');sfxStreak();}}",
    "if(f!==feverOn){feverOn=f;if(f){announce('حالت آتش!');sfxStreak();sfxFeverRiser();}}",
    'fever riser')

rep("(feverOn?16:0)", "(feverOn?28:0)", 'fever bpm boost')

# ============================================================
# 4) GAME OVER UPGRADES
# ============================================================
rep("function gameOver(){if(state!==ST.PLAY)return;state=ST.OVER;pauseGame=false;clearRun();",
    "function gameOver(){if(state!==ST.PLAY)return;state=ST.OVER;pauseGame=false;clearRun();var prevBest=best;",
    'gameOver prevBest capture')

rep("var acc=shots?Math.round(hits/shots*100):0;var rank=addScore(playerName,score,level,acc);",
    "var acc=shots?Math.round(hits/shots*100):0;questProg('score',score,true);var rank=addScore(playerName,score,level,acc);",
    'quest hook score')

rep("$('stWep').textContent=TIERS[runTier].name;$('stTime').textContent=faNum(Math.max(1,Math.round(elapsed)))+' ث';",
    "$('stWep').textContent=TIERS[runTier].name;$('stTime').textContent=faNum(Math.max(1,Math.round(elapsed)))+' ث';" +
    "var chest=Math.max(5,Math.round(score/300));addCoins(chest);saveProfile();" +
    "$('chestCoins').textContent='+'+faNum(chest);" +
    "var cbx=$('chestBox');cbx.classList.remove('open');void cbx.offsetWidth;cbx.classList.add('open');sfxChest();" +
    "$('encMsg').textContent=encMsg(score,best,acc,maxCombo);" +
    "var dm=$('diffMsg');if(score>prevBest&&prevBest>0){dm.textContent='بهبود '+faNum(Math.round((score-prevBest)/prevBest*100))+'٪ نسبت به رکورد قبلی';dm.style.display='block';}else dm.style.display='none';",
    'chest + encouragement + diff')

rep("var nb=$('newBest');if(rank===0&&score>0){nb.textContent='★ رکورد جدید ★';nb.classList.add('on');}else nb.classList.remove('on');",
    "var nb=$('newBest');if(rank===0&&score>0){nb.textContent='★ رکورد جدید ★';nb.classList.add('on');goldFlash();sfxRecord();}else nb.classList.remove('on');",
    'new record flash+fanfare')

rep("'رتبه تو در برترین‌ها: '+faNum(rank+1)",
    "(lbOnline?'رتبهٔ جهانی تو: ':'رتبه تو در برترین‌ها: ')+faNum(rank+1)",
    'global rank label')

# ============================================================
# 5) START & BOOT HOOKS
# ============================================================
rep("nameInput.blur();initAudio();resetRound();state=ST.PLAY;",
    "nameInput.blur();initAudio();resetRound();questRoundStart();state=ST.PLAY;",
    'start quest reset')

rep("loadScores();$('wep').textContent=TIERS[eqGun].name;",
    "questLoad();loadScores();$('wep').textContent=TIERS[eqGun].name;",
    'boot quest load')

# ============================================================
# 6) HTML ADDITIONS
# ============================================================
rep('<div id="vig2"></div><div id="vig"></div><div id="flash"></div><div id="fever"></div>',
    '<div id="vig2"></div><div id="vig"></div><div id="flash"></div><div id="fever"></div><div id="gflash"></div>',
    'gflash overlay div')

rep('<div class="modecard" id="modeOnline">',
    '''<div class="modecard" id="questCard">
  <div class="mc-head"><span class="mc-t">📅 چالش روزانه</span><span class="mc-lock" id="questReward"></span></div>
  <div class="mc-d" id="questDesc">در حال بارگذاری…</div>
  <div class="qbar"><i id="questFill"></i></div>
  <div class="qfoot"><span id="questProgTxt">۰ / ۰</span><button id="questClaim" class="btn" style="display:none">دریافت</button></div>
 </div>
 <div class="modecard" id="modeOnline">''',
    'daily quest card')

rep('<div class="finalLabel">امتیاز نهایی</div>',
    '''<div class="finalLabel">امتیاز نهایی</div>
 <div id="chestBox"><div class="chest-row"><div class="chest-lid">🎁</div><div class="chest-info"><div class="chest-t">جعبهٔ جایزه</div><div class="chest-c"><span class="coin-icon coin-xs" aria-hidden="true"></span><b id="chestCoins">+۰</b></div></div><div id="encMsg" class="chest-n"></div></div><div id="diffMsg" class="chest-d"></div></div>''',
    'chest box html')

rep('<div class="lbhead">۱۰ رکورد برتر <span id="lbMode">(محلی)</span></div>',
    '<div class="lbhead">۱۰ رکورد برتر <span id="lbMode">(محلی)</span><span id="myRank" class="myrank"></span></div>',
    'myRank chip')

# ============================================================
# 7) CSS ADDITIONS
# ============================================================
CSS_BLOCK = r"""
/* ===== نسخهٔ ۴ — جلوه‌های ارتقایافته ===== */
#gflash{position:fixed;inset:0;pointer-events:none;z-index:60;opacity:0;background:radial-gradient(circle at 50% 40%,rgba(255,214,90,.55),rgba(255,150,40,.2) 45%,transparent 72%)}
#gflash.go{animation:gfl 1.5s ease-out}
@keyframes gfl{0%{opacity:0}15%{opacity:1}100%{opacity:0}}
.float.head b{color:#ffd24a}.float.head i{color:#ffe9a8}
#newBest.on{animation:nbPulse 1.2s ease-in-out infinite}
@keyframes nbPulse{0%,100%{transform:scale(1);filter:drop-shadow(0 0 6px rgba(255,210,74,.45))}50%{transform:scale(1.06);filter:drop-shadow(0 0 18px rgba(255,210,74,.9))}}
.srow.me{background:linear-gradient(90deg,rgba(255,210,74,.14),rgba(255,210,74,.03));outline:1px solid rgba(255,210,74,.35);border-radius:8px}
.myrank{display:inline-block;margin-inline-start:10px;color:#ffd24a;font-weight:700;font-size:10.5px}
@keyframes menin{0%{opacity:0;transform:translateY(14px)}100%{opacity:1;transform:none}}
#menu .mwrap>*{animation:menin .5s cubic-bezier(.2,.7,.3,1) both}
#menu .mwrap>:nth-child(2){animation-delay:.06s}#menu .mwrap>:nth-child(3){animation-delay:.12s}#menu .mwrap>:nth-child(4){animation-delay:.18s}#menu .mwrap>:nth-child(5){animation-delay:.24s}#menu .mwrap>:nth-child(6){animation-delay:.3s}#menu .mwrap>:nth-child(7){animation-delay:.36s}#menu .mwrap>:nth-child(8){animation-delay:.42s}#menu .mwrap>:nth-child(9){animation-delay:.48s}
.qbar{height:8px;background:rgba(255,255,255,.1);border-radius:99px;overflow:hidden;margin:10px 0 6px}
.qbar i{display:block;height:100%;width:0;background:linear-gradient(90deg,#e8a552,#ffd24a);border-radius:99px;transition:width .4s}
.qfoot{display:flex;justify-content:space-between;align-items:center;font-size:11px;color:#b8a88a}
.qfoot .btn{padding:6px 14px;font-size:12px}
#questCard.qdone .mc-t{color:#ffd24a}
#chestBox{background:linear-gradient(180deg,rgba(232,165,82,.12),rgba(232,165,82,.04));border:1px solid rgba(255,176,84,.3);border-radius:12px;padding:10px 12px;margin:12px 0 4px}
.chest-row{display:flex;align-items:center;gap:10px;text-align:right}
.chest-lid{font-size:26px;filter:drop-shadow(0 2px 6px rgba(255,180,60,.4))}
#chestBox.open .chest-lid{animation:chestPop .6s cubic-bezier(.2,1.4,.4,1)}
@keyframes chestPop{0%{transform:scale(.4) rotate(-14deg);opacity:0}60%{transform:scale(1.2) rotate(4deg)}100%{transform:scale(1)}}
.chest-t{font-size:11px;color:#ffb35c;font-weight:700}
.chest-c{font-size:15px;font-weight:800;color:#ffd24a;display:flex;align-items:center;gap:4px}
.chest-n{flex:1;font-size:11.5px;color:#e8e2d4;line-height:1.5}
.chest-d{margin-top:6px;text-align:center;font-size:11px;color:#8fd18f;font-weight:700}
"""
ci = html.find('</style>')
if ci < 0:
    print('FAIL [style tag]'); sys.exit(1)
html = html[:ci] + CSS_BLOCK + html[ci:]
applied.append('CSS v4')
print('OK   [CSS v4]')

# ============================================================
# 8) VERSION + TITLE
# ============================================================
rep('<title>میدان غروب ۲ | نسخه نهایی و بهینه</title>',
    '<title>میدان غروب ۲ | نسخهٔ ۴ طلایی</title>', 'title v4')
rep('<span>SUNDOWN RANGE II</span><i>·</i><span>V3</span>',
    '<span>SUNDOWN RANGE II</span><i>·</i><span>V4 GOLD</span>', 'footer v4')

# ============================================================
# 9) INLINE EXTERNAL LIBS (offline-capable)
# ============================================================
LIBS = [
    ('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>',
     'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'),
    ('<script src="https://cdn.jsdelivr.net/npm/three@0.128/examples/js/loaders/GLTFLoader.js"></script>',
     'https://cdn.jsdelivr.net/npm/three@0.128/examples/js/loaders/GLTFLoader.js'),
    ('<script src="https://telegram.org/js/telegram-web-app.js"></script>',
     'https://telegram.org/js/telegram-web-app.js'),
]
ctx = ssl.create_default_context()
for tag, url in LIBS:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=30, context=ctx).read().decode('utf-8')
        if '</script' in data.lower():
            print(f'WARN: {url} contains </script — keeping CDN tag')
            continue
        if html.count(tag) == 1:
            html = html.replace(tag, '<script>\n/* inlined for offline: ' + url + ' */\n' + data + '\n</script>')
            applied.append('inline ' + url.rsplit('/', 1)[-1])
            print(f'OK   [inline {url.rsplit("/", 1)[-1]} — {len(data)//1024}KB]')
        else:
            print(f'WARN: tag not found once for {url}')
    except Exception as e:
        print(f'WARN: download failed {url}: {e} — keeping CDN tag')

open(OUT, 'w', encoding='utf-8').write(html)
print(f'\n=== DONE: {len(applied)} patches applied → {OUT} ({len(html)//1024}KB) ===')
