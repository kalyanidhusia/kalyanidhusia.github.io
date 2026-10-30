#!/usr/bin/env python3
"""Builds the four biology arcade modules from shared blocks."""
import json, os, re, subprocess

SHARED_CSS = """
/* THEME — swap these tokens when the custom theme arrives. Mobile-first. */
:root{
  --bg:#FAFAF7; --surface:#FFFFFF; --ink:#1F2933; --muted:#52606D;
  --line:rgba(0,0,0,.10); --accent:#B04A2F; --accent-soft:#F4E4DD;
  --good:#2F7D52; --bad:#A83E32; --violet:#8A4BD9;
  --font:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --mono:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#17191D; --surface:#1F2228; --ink:#E8EAED; --muted:#9AA5B1;
    --line:rgba(255,255,255,.14); --accent:#D68264; --accent-soft:#3A251D;
    --good:#5FB084; --bad:#D98378; --violet:#B08CE8; color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --bg:#17191D; --surface:#1F2228; --ink:#E8EAED; --muted:#9AA5B1;
  --line:rgba(255,255,255,.14); --accent:#D68264; --accent-soft:#3A251D;
  --good:#5FB084; --bad:#D98378; --violet:#B08CE8; color-scheme:dark;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--font);
  font-size:1.1rem;line-height:1.55;
  padding-left:max(16px,env(safe-area-inset-left,0px));
  padding-right:max(16px,env(safe-area-inset-right,0px));
  padding-block:0 40px}
button{font-family:inherit;cursor:pointer}
:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
@media (prefers-reduced-motion: reduce){*{transition:none!important;animation:none!important}}
.wrap{max-width:560px;margin:0 auto}
header{padding-block:18px 10px}
header h1{font-size:1.5rem;font-weight:700;margin:0}
header .tag{color:var(--muted);font-size:.9rem}
.eyebrow{font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);font-weight:700;margin:0}

.statbar{display:flex;gap:8px;margin:10px 0 8px;flex-wrap:wrap}
.stat{background:var(--surface);border:1.5px solid var(--line);border-radius:12px;padding:8px 14px;min-width:0}
.stat .lbl{font-size:.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;font-weight:700}
.stat .val{font-family:var(--mono);font-size:1.25rem;font-weight:600;line-height:1.3}
.stat.grow{flex:1}
.hearts .val{letter-spacing:2px}
.hearts .off{opacity:.2}

.stage{position:relative;display:grid;border-radius:14px;overflow:hidden;border:1.5px solid var(--line);background:var(--surface)}
.stage>*{grid-area:1/1}
#board{display:block;width:100%;touch-action:none;align-self:start}
.overlay{position:relative;min-height:100%;background:var(--bg);opacity:.97;display:flex;flex-direction:column;justify-content:flex-start;gap:12px;padding:20px}
.overlay h2{font-size:1.35rem;margin:0;line-height:1.25}
.overlay p{margin:0;font-size:1rem}
.overlay .muted{color:var(--muted);font-size:.9rem}
.overlay .learn{background:var(--surface);border:1.5px solid var(--line);border-radius:12px;padding:12px 14px;font-size:.95rem}
.overlay .learn b{display:block;margin-bottom:6px}
.overlay .learn ul{margin:0;padding-left:20px}
.overlay .learn li{margin:.25em 0}
.overlay ol{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:7px;font-size:1rem}
.overlay ol li{display:flex;gap:10px}
.overlay ol .n{color:var(--accent);font-weight:700;flex:none}
.facts{display:flex;flex-direction:column;gap:8px;font-size:.93rem}
.facts div{padding-left:12px;border-left:3px solid var(--accent-soft)}
.btn{border:none;border-radius:999px;padding:13px 26px;font-weight:700;font-size:1.05rem;background:var(--accent);color:#fff;align-self:flex-start}
.btn.sm{padding:9px 18px;font-size:.92rem}
.banner{min-height:1.6em;text-align:center;font-weight:700;font-size:1rem;margin-top:10px}
.banner.ok{color:var(--good)} .banner.no{color:var(--bad)} .banner.vi{color:var(--violet)}

.pad{display:grid;grid-template-columns:repeat(3,76px);grid-template-rows:repeat(2,58px);gap:8px;justify-content:center;margin-top:14px}
.pad button{border:2px solid var(--line);background:var(--surface);color:var(--ink);border-radius:14px;font-size:1.5rem;line-height:1;padding:0}
.pad button:active{background:var(--accent-soft);border-color:var(--accent)}
.pad .up{grid-column:2}
.ctrl-note{text-align:center;color:var(--muted);font-size:.85rem;margin-top:8px}
@media (min-width:700px){.pad{display:none}.ctrl-note.hide-desktop{display:none}}

.quiz{background:var(--surface);border:1.5px solid var(--line);border-radius:14px;padding:20px;margin-top:28px}
.quiz h2{font-size:1.25rem;margin:0 0 4px}
.quiz .meta{font-size:.85rem;color:var(--muted)}
.q-dots{display:flex;gap:6px;margin:14px 0}
.q-dots span{width:10px;height:10px;border-radius:50%;background:var(--line)}
.q-dots span.cur{background:var(--accent)}
.q-dots span.ok{background:var(--good)}
.q-dots span.no{background:var(--bad)}
.q .stem{font-weight:700;margin-bottom:12px}
.q label{display:flex;gap:10px;border:1.5px solid var(--line);border-radius:12px;padding:12px 14px;margin-bottom:8px;font-size:1rem;cursor:pointer;align-items:flex-start}
.q input{margin-top:4px;accent-color:var(--accent)}
.q.graded label.right{border-color:var(--good);background:var(--accent-soft)}
.q.graded label.wrong-pick{border-color:var(--bad)}
.q .verdict{font-weight:700;margin-top:6px}
.q .verdict.ok{color:var(--good)} .q .verdict.no{color:var(--bad)}
.q .explain{color:var(--muted);font-size:.92rem;border-left:3px solid var(--line);padding:2px 12px;margin-top:8px}
.qbtn{border:none;border-radius:999px;padding:12px 22px;font-weight:700;background:var(--accent);color:#fff;margin-top:10px}
.score-final{background:var(--accent-soft);border-radius:12px;padding:14px 16px;margin-top:12px;font-size:1rem}
.score-final .code{font-family:var(--mono);display:block;margin-top:6px}
footer{margin-top:30px;color:var(--muted);font-size:.82rem;max-width:60ch}
"""

QUIZ_JS = """
/* ---------- shared quiz engine ---------- */
var qi=0,qres=[];
function qDots(){
  var d=$("#q-dots");d.innerHTML="";
  QUIZ.forEach(function(_,i){
    var s=document.createElement("span");
    if(i<qres.length)s.className=qres[i]?"ok":"no";
    else if(i===qi)s.className="cur";
    d.appendChild(s);
  });
}
function qRender(){
  var q=QUIZ[qi],st=$("#q-stage");
  st.innerHTML='<div class="q"><div class="stem">Q'+(qi+1)+'. '+q.stem+'</div>'+
    q.opts.map(function(o,i){return '<label><input type="radio" name="qq" value="'+i+'" id="qq'+qi+'o'+i+'"><span>'+o+'</span></label>';}).join("")+
    '<div class="fb"></div><button class="qbtn" id="q-check">Check answer</button></div>';
  $("#q-check").addEventListener("click",qCheck);
  qDots();
}
function qCheck(){
  var q=QUIZ[qi],sel=document.querySelector('input[name="qq"]:checked');
  var el=$("#q-stage .q"),fb=el.querySelector(".fb");
  if(!sel){fb.innerHTML='<div class="verdict no">Pick an answer first.</div>';return;}
  var pick=+sel.value,ok=pick===q.a;
  qres.push(ok);el.classList.add("graded");
  el.querySelectorAll("label").forEach(function(l,i){
    l.querySelector("input").disabled=true;
    if(i===q.a)l.classList.add("right");else if(i===pick)l.classList.add("wrong-pick");
  });
  fb.innerHTML='<div class="verdict '+(ok?"ok":"no")+'">'+(ok?"Correct.":"Not quite — see the highlighted answer.")+'</div><div class="explain">'+q.explain+'</div>';
  var btn=el.querySelector(".qbtn");
  btn.textContent=qi===QUIZ.length-1?"See my score":"Next question";
  btn.removeEventListener("click",qCheck);
  btn.addEventListener("click",function(){
    if(qi===QUIZ.length-1)qFinish();else{qi++;qRender();}
  });
  qDots();
}
function qFinish(){
  var score=qres.filter(Boolean).length,pass=score>=5;
  var s=(CODEP+"|"+score+"|"+new Date().toISOString().slice(0,10));
  var h=5381;for(var i=0;i<s.length;i++)h=((h<<5)+h+s.charCodeAt(i))>>>0;
  $("#q-stage").innerHTML="";
  $("#q-final").innerHTML='<div class="score-final"><strong>'+score+' / 6'+(pass?' — passed':'')+'</strong>'+
    (pass?' Concept locked in.':' Replay the game, reread the win-screen facts, and try again — attempts are unlimited.')+
    '<span class="code">verification code: '+CODEP+'-'+score+'-'+h.toString(36).toUpperCase()+'</span>'+
    '<button class="qbtn" id="q-retry">Try again</button></div>';
  $("#q-retry").addEventListener("click",function(){qi=0;qres=[];$("#q-final").innerHTML="";qRender();});
  qDots();
}
"""

SHARED_JS_TOP = """
var $=function(s){return document.querySelector(s);};
var bannerTimer=null;
function setBanner(msg,cls){
  var b=$("#banner");b.textContent=msg;b.className="banner "+(cls||"");
  clearTimeout(bannerTimer);bannerTimer=setTimeout(function(){b.textContent="";},2800);
}
function reducedMotion(){try{return matchMedia("(prefers-reduced-motion: reduce)").matches;}catch(e){return false;}}
function isDark(){try{return (document.documentElement.dataset.theme==="dark")||(!document.documentElement.dataset.theme&&matchMedia("(prefers-color-scheme: dark)").matches);}catch(e){return false;}}
function makeConfetti(W,H){
  var pal=["#2F8C72","#C98F2C","#4A69C4","#B05A92","#8A4BD9","#B04A2F"],out=[];
  for(var i=0;i<110;i++)out.push({x:Math.random()*W,y:-10-Math.random()*80,
    vx:(Math.random()-0.5)*60,vy:60+Math.random()*110,rot:Math.random()*6.3,vr:(Math.random()-0.5)*8,c:pal[i%6]});
  return out;
}
function stepConfetti(list,H,dt){
  list.forEach(function(p){p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=240*dt;p.rot+=p.vr*dt;});
  return list.filter(function(p){return p.y<H+40;});
}
function drawConfetti(ctx,list){
  list.forEach(function(p){ctx.save();ctx.translate(p.x,p.y);ctx.rotate(p.rot);
    ctx.fillStyle=p.c;ctx.fillRect(-4,-2.5,8,5);ctx.restore();});
}
function rrp(ctx,x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath();}
"""

FOOTER = """<footer>Part of the AI in Biomedicine student training pathway · AR INBRE, supported
by NIGMS of the NIH under award P20 GM103429. Educational content, not medical advice.
{SIMPLIFICATION}</footer>"""

def flashcard(eyebrow, head, concept, objectives, howto, note, btn):
    obj = "".join("<li>%s</li>" % o for o in objectives)
    steps = "".join('<li><span class="n">%d</span><span>%s</span></li>' % (i+1, s) for i, s in enumerate(howto))
    return ('<div class="overlay" id="overlay">'
            '<p class="eyebrow">%s</p><h2>%s</h2><p>%s</p>'
            '<div class="learn"><b>After playing you can…</b><ul>%s</ul></div>'
            '<ol>%s</ol><p class="muted">%s</p>'
            '<button class="btn" id="start-btn">%s</button></div>') % (eyebrow, head, concept, obj, steps, note, btn)

def page(title, tag, extra_css, hud_html, stage_inner, controls_html, game_js, quiz, codep, simplification):
    quiz_json = json.dumps(quiz, ensure_ascii=False)
    return ("<title>%s</title>\n" % title +
      '<meta name="claude:viewport-fit-sides" content="cover">\n' +
      "<style>" + SHARED_CSS + extra_css + "</style>\n" +
      '<div class="wrap">\n<header><h1>%s</h1> <span class="tag">%s</span></header>\n' % (title, tag) +
      hud_html +
      '<div class="stage"><canvas id="board" aria-label="%s board"></canvas>\n%s</div>\n' % (title, stage_inner) +
      '<div class="banner" id="banner"></div>\n' + controls_html +
      '<div class="quiz" id="quiz"><h2>Check what you learned</h2>'
      '<p class="meta">6 questions · pass at 5 · retakes allowed</p>'
      '<div class="q-dots" id="q-dots"></div><div id="q-stage"></div><div id="q-final"></div></div>\n' +
      FOOTER.replace("{SIMPLIFICATION}", simplification) + "\n" +
      "<script>\n(function(){\n\"use strict\";\n" + SHARED_JS_TOP +
      "var QUIZ=" + quiz_json + ";var CODEP=" + json.dumps(codep) + ";\n" +
      game_js + QUIZ_JS +
      "\nqRender();\n})();\n</script>\n")

STD_HUD = """<div class="statbar">
  <div class="stat grow"><div class="lbl">{L1}</div><div class="val" id="s1">{V1}</div></div>
  <div class="stat"><div class="lbl">{L2}</div><div class="val" id="s2">{V2}</div></div>
  <div class="stat hearts"><div class="lbl">{L3}</div><div class="val" id="hearts">●●●</div></div>
</div>
"""

PAD = """<div class="pad" id="pad">
  <button class="up" data-k="up" aria-label="Up">↑</button>
  <button data-k="left" aria-label="Left">←</button>
  <button data-k="down" aria-label="Down">↓</button>
  <button data-k="right" aria-label="Right">→</button>
</div>
"""

GAMES = {}

# ============================================================ POLYMERASE RUNNER
GAMES["poly"] = dict(
  title="Polymerase Runner", tag="Read the template, build the mRNA",
  codep="PR",
  extra_css="""
.basepad{display:flex;gap:8px;justify-content:center;margin-top:14px;flex-wrap:wrap}
.basepad button{border:2px solid var(--line);background:var(--surface);color:var(--ink);border-radius:14px;font-size:1.3rem;font-weight:700;min-width:58px;padding:12px 0}
.basepad button:active{background:var(--accent-soft);border-color:var(--accent)}
.basepad .jumpb{min-width:96px;border-color:var(--accent);color:var(--accent);font-size:1rem}
.basepad #tu-btn.u{border-color:var(--violet);color:var(--violet)}
.pairkey{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px;font-size:.88rem;color:var(--muted);justify-content:center}
.pairkey b{color:var(--ink)}
""",
  hud=STD_HUD.replace("{L1}","Strand built").replace("{V1}","0 / 20")
            .replace("{L2}","Score").replace("{V2}","0")
            .replace("{L3}","Slips"),
  stage_inner=flashcard(
    "Transcription · DNA → mRNA",
    "You are RNA polymerase — read the DNA, write the message.",
    "Genes are instructions stored in DNA, written in four bases: A, T, G, C. To use a gene, the enzyme <strong>RNA polymerase</strong> slides along the DNA template and builds a matching strand letter by letter, using the pairing rules <strong>A–T</strong> (2 hydrogen bonds) and <strong>G–C</strong> (3). RNA has one twist: <strong>uracil (U) takes thymine's place</strong>, so A pairs with U. The strand you build is <strong>mRNA</strong> — the message the ribosome will read next.",
    ["Pair any base correctly and say how many hydrogen bonds hold it (A–T/U: 2, G–C: 3).",
     "Explain what changes in RNA: uracil replaces thymine, so A pairs with U.",
     "Describe RNA polymerase's job and what the finished mRNA is for."],
    ["A template base slides into your clamp — <strong>tap the base that pairs with it</strong>.",
     "After 10 pairs you cross into the <strong>transcription zone</strong>: your T shatters into violet <strong>U</strong>, and A pairs with U from then on.",
     "<strong>Jump</strong> the 5 protein roadblocks on the template. Your first 2 wrong picks are free practice; after that, 3 slips end the run."],
    "Real polymerases hit roadblocks too — DNA-binding proteins stall them, and they really do pause and restart.",
    "Start transcribing"),
  controls="""<div class="basepad" id="basepad">
  <button data-b="A" aria-label="Pair A">A</button>
  <button data-b="T" id="tu-btn" aria-label="Pair T or U">T</button>
  <button data-b="G" aria-label="Pair G">G</button>
  <button data-b="C" aria-label="Pair C">C</button>
  <button data-b="jump" class="jumpb" aria-label="Jump">Jump</button>
</div>
<div class="pairkey"><span><b>A–T</b> / <b>A–U</b> · 2 H-bonds</span><span><b>G–C</b> · 3 H-bonds</span></div>
<p class="ctrl-note">Tap the pairing base · desktop: A T G C (or U) keys, space = jump</p>""",
  js=r"""
/* Speed — tunable without editing code:
   URL params  ?speed=60&accel=2&max=120   or console: PRspeed({speed:60,accel:2,max:120})
   speed = starting scroll px/s, accel = px/s gained per correct pair, max = speed cap */
var qs=new URLSearchParams(location.search);
function qn(name,def,min){var v=parseInt(qs.get(name),10);return isNaN(v)?def:Math.max(min,v);}
var V0=qn("speed",70,30),VACC=qn("accel",3,0),VMAX=Math.max(V0,qn("max",140,40));
var W=360,H=240,dpr=1,clampX=120;
var GAP=64,N=20,RNA_AT=10;
/* strand layout: a gap that holds a roadblock is double width, so the
   obstacle sits a full GAP from the base before it and after it */
var OBS_AFTER=[4,7,11,14,17],BX=[],OBX={},ZONEX=0;
(function(){var x=0;
  for(var i=0;i<N;i++){BX[i]=x;x+=GAP;
    if(OBS_AFTER.indexOf(i)>=0){OBX[i]=BX[i]+GAP;x+=GAP;}}
  ZONEX=(BX[RNA_AT-1]+BX[RNA_AT])/2;})();
var canvas=$("#board"),ctx=canvas.getContext("2d");
var g=null,raf=null,last=0;
var PCOL={A:"#2F8C72",T:"#C98F2C",G:"#4A69C4",C:"#B05A92",U:"#8A4BD9"};
function makeGene(){
  var pool=["A","A","T","G","C","A","G","C","T","G"],out=[];
  for(var i=0;i<N;i++)out.push(pool[Math.floor(Math.random()*pool.length)]);
  if(out.slice(0,RNA_AT).indexOf("A")<0)out[3]="A";
  var c=0;for(i=RNA_AT;i<N;i++)if(out[i]==="A")c++;
  if(c<2){out[RNA_AT+1]="A";out[RNA_AT+5]="A";}
  return out;
}
function wantFor(b,rna){
  if(b==="A")return rna?"U":"T";
  if(b==="T")return "A";
  if(b==="G")return "C";
  return "G";
}
function reset(){
  g={gene:makeGene(),pairs:[],n:0,x:-GAP*2.2,v:V0,phase:"scroll",score:0,
     hearts:3,practice:2,rna:false,jumpT:-9,running:false,over:false,
     obstacles:OBS_AFTER.map(function(i){return {i:i,done:false,cleared:false};}),
     shards:[],confetti:null,hintShown:0};
  var tb=$("#tu-btn");tb.textContent="T";tb.classList.remove("u");
  renderHUD();
}
function renderHUD(){
  $("#s1").textContent=g.n+" / "+N;
  $("#s2").textContent=g.score;
  var h="";for(var i=0;i<3;i++)h+='<span class="'+(i<(3-g.hearts)?"":"off")+'" style="color:var(--bad)">●</span>';
  $("#hearts").innerHTML=h;
}
function airborne(now){return (now-g.jumpT)<520;}
function mistake(msg){
  if(g.practice>0){g.practice--;setBanner(msg+" · practice, no heart lost ("+g.practice+" left)","no");return;}
  g.hearts--;renderHUD();setBanner(msg,"no");
  if(g.hearts<=0)endGame(false,"Three slips — transcription aborted. That happens in real cells too. Check the table before you tap: A pairs with T in DNA and U in RNA (2 hydrogen bonds); G pairs with C (3 bonds).");
}
function pick(b){
  if(!g.running||g.phase!=="await")return;
  var tb=g.gene[g.n],want=wantFor(tb,g.rna&&g.n>=RNA_AT);
  var chosen=(g.rna&&b==="T")?"U":b;
  if(chosen===want){
    g.pairs.push(want);g.n++;
    var bonds=(tb==="G"||tb==="C")?3:2;
    g.score+=50;setBanner(tb+"–"+want+" · "+bonds+" hydrogen bonds ✓","ok");
    renderHUD();
    if(g.n>=N)return endGame(true,null);
    g.phase="scroll";g.v=Math.min(VMAX,g.v+VACC);
  }else{
    mistake(chosen+" doesn’t pair with "+tb+" — "+tb+" pairs with "+want);
  }
}
function jump(){
  if(!g.running||g.phase!=="scroll")return;
  var now=performance.now();
  if(!airborne(now))g.jumpT=now;
}
function makeShards(x,y){
  var out=[];
  for(var i=0;i<26;i++)out.push({x:x,y:y,vx:(Math.random()-0.5)*220,vy:-60-Math.random()*160,life:0.9});
  return out;
}
function endGame(won,msg){
  g.over=true;g.running=false;g.phase="done";renderHUD();
  if(won&&!reducedMotion()){
    g.confetti=makeConfetti(W,H);
    cancelAnimationFrame(raf);raf=requestAnimationFrame(loop);
  }
  var ov=$("#overlay");
  setTimeout(function(){
    ov.hidden=false;
    ov.innerHTML= won?
      '<h2>mRNA complete!</h2>'+
      '<p><strong>'+g.score+' points</strong> · your transcript, 5′→3′:</p>'+
      '<p style="font-family:var(--mono);font-size:1.05rem;letter-spacing:2px;color:var(--violet);margin:0">'+g.pairs.slice(RNA_AT).join("")+'</p>'+
      '<div class="facts">'+
      '<div>You just did what <strong>RNA polymerase</strong> does: read the DNA template and write a complementary strand, letter by letter.</div>'+
      '<div><strong>U replaced T</strong> the moment you entered the transcription zone — RNA’s signature move. A–U still uses 2 hydrogen bonds; G–C uses 3.</div>'+
      '<div>If your transcript encoded a viral protein, it could be the starting blueprint for a <strong>hypothetical vaccine candidate</strong>. A real one also needs a cap, a tail, and years of engineering and testing — that part is the career.</div>'+
      '<div>Simplification to know: a real polymerase uses RNA rules (U, not T) from the very first base — the DNA warm-up zone exists so you learn both pairing tables.</div>'+
      '</div><button class="btn" id="start-btn">Transcribe another gene</button>'
      :
      '<h2>The polymerase fell off the template</h2><p>'+msg+'</p>'+
      '<p class="muted">Score: '+g.score+' · '+g.n+' of '+N+' bases paired. Every run uses a new gene — try again.</p>'+
      '<button class="btn" id="start-btn">Try again</button>';
    $("#start-btn").addEventListener("click",start);
  },won&&!reducedMotion()?2000:600);
}
function start(){
  reset();$("#overlay").hidden=true;
  g.running=true;last=performance.now();
  cancelAnimationFrame(raf);raf=requestAnimationFrame(loop);
}
function loop(now){
  var dt=Math.min(0.05,(now-last)/1000);last=now;
  if(g.running&&g.phase==="scroll"){
    g.x+=g.v*dt;
    if(!g.rna&&g.x>ZONEX){
      g.rna=true;
      var tb=$("#tu-btn");tb.textContent="U";tb.classList.add("u");
      g.shards=makeShards(clampX,H-110);
      setBanner("TRANSCRIPTION ZONE — uracil (U) replaces thymine (T)","vi");
    }
    for(var k=0;k<g.obstacles.length;k++){
      var o=g.obstacles[k],ox=OBX[o.i];
      if(o.done)continue;
      if(g.x>ox-14&&g.x<ox+16){
        if(airborne(now)){o.done=true;o.cleared=true;g.score+=25;setBanner("Roadblock cleared +25","ok");renderHUD();}
        else{o.done=true;mistake("A protein roadblock stalled you — jump next time");}
      }else if(g.x>=ox+16){o.done=true;o.cleared=true;}
    }
    if(g.x>=BX[g.n]){g.x=BX[g.n];g.phase="await";}
  }
  if(g.shards.length){
    g.shards.forEach(function(p){p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=420*dt;p.life-=dt;});
    g.shards=g.shards.filter(function(p){return p.life>0;});
  }
  if(g.confetti&&g.confetti.length)g.confetti=stepConfetti(g.confetti,H,dt);
  draw(now);
  if(g.running||g.shards.length||(g.confetti&&g.confetti.length))raf=requestAnimationFrame(loop);
}
function tile(x,y,letter,alpha){
  ctx.globalAlpha=alpha==null?1:alpha;
  ctx.fillStyle=PCOL[letter]||"#9AA5B1";
  rrp(ctx,x-16,y-16,32,32,8);ctx.fill();
  ctx.fillStyle="#fff";ctx.font="700 17px ui-sans-serif,system-ui";ctx.textAlign="center";
  ctx.fillText(letter,x,y+6);
  ctx.globalAlpha=1;
}
function draw(now){
  now=now||performance.now();
  var dark=isDark();
  ctx.fillStyle=dark?"#1F2228":"#FFFFFF";ctx.fillRect(0,0,W+4,H+4);
  var strandY=H-52;
  // RNA zone tint + divider
  var zx=clampX+(ZONEX-g.x);
  if(zx<W){
    ctx.fillStyle=dark?"rgba(176,140,232,.08)":"rgba(138,75,217,.06)";
    ctx.fillRect(Math.max(0,zx),0,W-Math.max(0,zx),H);
  }
  if(zx>-60&&zx<W+60){
    ctx.strokeStyle=dark?"#B08CE8":"#8A4BD9";ctx.setLineDash([6,5]);ctx.lineWidth=2;
    ctx.beginPath();ctx.moveTo(zx,10);ctx.lineTo(zx,H-16);ctx.stroke();ctx.setLineDash([]);
    ctx.fillStyle=dark?"#B08CE8":"#8A4BD9";ctx.font="700 11px ui-sans-serif,system-ui";ctx.textAlign="left";
    ctx.fillText("TRANSCRIPTION ZONE · RNA rules",zx+7,20);
  }
  // template backbone
  ctx.strokeStyle=dark?"rgba(232,234,237,.35)":"rgba(31,41,51,.3)";ctx.lineWidth=3;
  ctx.beginPath();ctx.moveTo(0,strandY+30);ctx.lineTo(W,strandY+30);ctx.stroke();
  // bases + pairs
  for(var i=0;i<N;i++){
    var sx=clampX+(BX[i]-g.x);
    if(sx<-44||sx>W+44)continue;
    tile(sx,strandY+6,g.gene[i]);
    if(i<g.n){
      var pl=g.pairs[i],bonds=(g.gene[i]==="G"||g.gene[i]==="C")?3:2;
      tile(sx,strandY-52,pl);
      ctx.strokeStyle=dark?"rgba(232,234,237,.5)":"rgba(31,41,51,.4)";ctx.lineWidth=2;
      for(var b=0;b<bonds;b++){
        var bx=sx-8+b*(bonds===2?16:8);
        ctx.beginPath();ctx.moveTo(bx,strandY-34);ctx.lineTo(bx,strandY-12);ctx.stroke();
      }
    }
  }
  // obstacles
  g.obstacles.forEach(function(o){
    if(o.done&&o.cleared)return;
    var ox=clampX+(OBX[o.i]-g.x);
    if(ox<-40||ox>W+40)return;
    ctx.fillStyle=dark?"#5A646E":"#9AA5B1";
    rrp(ctx,ox-15,strandY+2,30,22,8);ctx.fill();
    ctx.fillStyle=dark?"#1F2228":"#FFFFFF";ctx.font="700 12px ui-sans-serif,system-ui";ctx.textAlign="center";
    ctx.fillText("!",ox,strandY+18);
    if(!o.done&&ox>clampX&&ox<clampX+130&&g.phase==="scroll"){
      ctx.fillStyle=dark?"#D98378":"#A83E32";ctx.font="700 12px ui-sans-serif,system-ui";
      ctx.fillText("JUMP!",ox,strandY-10);
    }
  });
  // player clamp
  var p=Math.max(0,Math.min(1,(now-g.jumpT)/520));
  var hop=(p>0&&p<1)?Math.sin(Math.PI*p)*46:0;
  var cy=-hop;
  ctx.strokeStyle=dark?"#D68264":"#B04A2F";ctx.lineWidth=3;
  ctx.fillStyle=dark?"rgba(214,130,100,.12)":"rgba(176,74,47,.07)";
  rrp(ctx,clampX-24,strandY-76+cy,48,110,12);ctx.fill();ctx.stroke();
  ctx.fillStyle=dark?"#D68264":"#B04A2F";ctx.font="700 12px ui-sans-serif,system-ui";ctx.textAlign="center";
  ctx.fillText("YOU",clampX,strandY-84+cy);
  // dashed slot when waiting
  if(g.phase==="await"){
    ctx.strokeStyle=dark?"#D68264":"#B04A2F";ctx.setLineDash([5,4]);ctx.lineWidth=2;
    rrp(ctx,clampX-18,strandY-70,36,36,8);ctx.stroke();ctx.setLineDash([]);
    if(g.n<2){
      var want=wantFor(g.gene[g.n],g.rna&&g.n>=RNA_AT);
      ctx.fillStyle=dark?"rgba(232,234,237,.55)":"rgba(31,41,51,.45)";
      ctx.font="700 12px ui-sans-serif,system-ui";
      ctx.fillText("tap "+want,clampX,strandY-78);
    }
  }
  // shatter shards
  if(g.shards.length){
    ctx.fillStyle=dark?"#B08CE8":"#8A4BD9";
    g.shards.forEach(function(p){ctx.globalAlpha=Math.max(0,p.life);ctx.fillRect(p.x-3,p.y-3,6,6);});
    ctx.globalAlpha=1;
  }
  if(g.confetti)drawConfetti(ctx,g.confetti);
}
function sizeCanvas(){
  var w=canvas.parentElement.clientWidth;
  W=w;H=Math.max(215,Math.min(290,Math.round(w*0.6)));
  clampX=Math.max(90,Math.min(150,Math.round(w*0.3)));
  dpr=Math.min(window.devicePixelRatio||1,3);
  canvas.style.height=H+"px";
  canvas.width=Math.round(W*dpr);canvas.height=Math.round(H*dpr);
  ctx.setTransform(dpr,0,0,dpr,0,0);
}
document.getElementById("basepad").addEventListener("click",function(e){
  var b=e.target.closest("[data-b]");if(!b)return;
  if(b.dataset.b==="jump")jump();else pick(b.dataset.b);
});
document.addEventListener("keydown",function(e){
  if(!g||!g.running)return;
  var k=e.key.toLowerCase();
  if(k===" "){e.preventDefault();jump();}
  else if(k==="a")pick("A");
  else if(k==="t"||k==="u")pick("T");
  else if(k==="g")pick("G");
  else if(k==="c")pick("C");
});
document.addEventListener("visibilitychange",function(){
  if(document.hidden&&g&&g.running){g.running=false;
    var ov=$("#overlay");ov.hidden=false;
    ov.innerHTML='<h2>Paused</h2><button class="btn" id="start-btn">Restart</button>';
    $("#start-btn").addEventListener("click",start);}
});
window.addEventListener("resize",function(){sizeCanvas();draw();});
window.PRspeed=function(o){o=o||{};
  if(o.speed)V0=Math.max(30,o.speed);
  if(o.accel!=null)VACC=Math.max(0,o.accel);
  if(o.max)VMAX=Math.max(V0,o.max);
  if(g){g.v=Math.min(Math.max(V0,g.v),VMAX);}
  return {speed:V0,accel:VACC,max:VMAX,current:g?Math.round(g.v):V0};
};
window.PRstate=function(){
  var nd=null;
  g.obstacles.forEach(function(o){if(!o.done){var d=OBX[o.i]-g.x;if(nd===null||d<nd)nd=d;}});
  return {n:g.n,phase:g.phase,rna:g.rna,next:g.gene[g.n]||null,hearts:g.hearts,
          score:g.score,over:g.over,won:g.n>=N,nextObs:nd};
};
sizeCanvas();reset();draw();
$("#start-btn").addEventListener("click",start);
""",
  quiz=[
   dict(stem="Transcription copies information from:",opts=["DNA into mRNA","Protein into DNA","Sugar into fat"],a=0,
        explain="Transcription is the first step of the central dogma: DNA → RNA → protein. You played the DNA → RNA step."),
   dict(stem="Which base appears in RNA but not in DNA?",opts=["Uracil (U)","Thymine (T)","Guanine (G)"],a=0,
        explain="RNA swaps thymine for uracil — the moment your T button shattered into violet U."),
   dict(stem="In DNA, A pairs with T. In RNA, A pairs with:",opts=["U","G","C"],a=0,
        explain="Same partner slot, new letter: adenine pairs with uracil in RNA, still held by 2 hydrogen bonds."),
   dict(stem="Which enzyme builds mRNA from a DNA template?",opts=["RNA polymerase","Ribosome","β-lactamase"],a=0,
        explain="RNA polymerase is the runner you played. The ribosome comes next (Ribosome Snake!) — it reads the mRNA to build protein."),
   dict(stem="Which base pair is held together by 3 hydrogen bonds?",opts=["G–C","A–T","A–U"],a=0,
        explain="G–C pairs use 3 hydrogen bonds; A–T and A–U use 2. That's why G–C-rich DNA is harder to pull apart."),
   dict(stem="What is the finished mRNA for?",opts=["It carries the gene's message to the ribosome, which builds the protein","It becomes part of the cell wall","It stores fat"],a=0,
        explain="mRNA is the working copy of a gene. The ribosome reads it three letters at a time and builds the protein — the next game in the arcade."),
  ],
  simplification="Simplified on purpose: the warm-up zone pairs DNA with DNA so you learn both pairing tables — a real RNA polymerase builds RNA (with U) from the very first base, inside a transcription bubble.")

# ============================================================ FOLD-TRIS
GAMES["fold"] = dict(
  title="Fold-Tris", tag="Bury the oily core, fold the protein",
  codep="FT",
  extra_css="""
.foldpad{display:flex;gap:8px;justify-content:center;margin-top:14px;flex-wrap:wrap}
.foldpad button{border:2px solid var(--line);background:var(--surface);color:var(--ink);border-radius:14px;font-size:1.25rem;min-width:64px;padding:12px 0}
.foldpad button:active{background:var(--accent-soft);border-color:var(--accent)}
.foldpad .wide{min-width:96px;font-size:1rem;font-weight:700}
.chap{margin-top:10px;text-align:center}
.chap button{border:2px solid var(--violet);color:var(--violet);background:var(--surface);border-radius:999px;padding:9px 18px;font-weight:700;font-size:.95rem}
.chap button:disabled{opacity:.4}
.legend{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px;font-size:.88rem;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.legend i{width:14px;height:14px;border-radius:4px;display:inline-block}
#board{margin:0 auto}
""",
  hud=STD_HUD.replace("{L1}","Layers buried").replace("{V1}","0 / 6")
            .replace("{L2}","Score").replace("{V2}","0")
            .replace("{L3}","Misfolds"),
  stage_inner=flashcard(
    "Protein folding · the hydrophobic effect",
    "A protein folds to hide its oily parts from water.",
    "Proteins are chains of amino acids. Some residues are <strong>hydrophobic (H)</strong> — oily, water-fearing — and some are <strong>polar (P)</strong> — water-loving. In the cell's watery interior, the chain folds so H residues bury into the <strong>core</strong> and P residues face the water. That buried core is what makes a protein stable and functional.",
    ["Explain what drives protein folding: hydrophobic residues burying away from water.",
     "Predict where a residue belongs: H inside the core, P on the surface.",
     "Connect misfolding and aggregation to real diseases, and say what chaperones do."],
    ["Pieces of H (gold) and P (blue) residues fall into the protein.",
     "Steer and rotate so <strong>H lands in the shaded core</strong> (middle columns) and <strong>P at the water-facing edges</strong>.",
     "A complete, correctly placed layer buries — bury 6 to fold the domain. Wrongly placed full layers <strong>misfold</strong> and pile up; three means aggregation."],
    "One chaperone rescue per game removes your worst misfolded layer — real cells have chaperone proteins that do exactly this.",
    "Start folding"),
  controls="""<div class="foldpad" id="foldpad">
  <button data-k="left" aria-label="Move left">←</button>
  <button data-k="rot" class="wide">Rotate</button>
  <button data-k="right" aria-label="Move right">→</button>
  <button data-k="drop" class="wide">Drop</button>
</div>
<div class="chap"><button id="chap-btn">Chaperone rescue · 1 left</button></div>
<div class="legend">
  <span><i style="background:#C98F2C"></i>H — hydrophobic (oily)</span>
  <span><i style="background:#4A69C4"></i>P — polar (water-loving)</span>
  <span><i style="background:#9AA5B1"></i>misfolded layer</span>
</div>
<p class="ctrl-note">Tap buttons · desktop: arrow keys move, up = rotate, space = drop</p>""",
  js=r"""
/* Board fit — tunable without editing code:
   URL params  ?rows=12&cell=36&reserve=220   or console: FTfit({rows:12,cell:36,reserve:220}) */
var qs=new URLSearchParams(location.search);
var COLS=9,ROWS=Math.max(8,Math.min(16,parseInt(qs.get("rows"),10)||13)),CORE_LO=3,CORE_HI=5,cell=30,dpr=1;
var RESERVE=Math.max(0,parseInt(qs.get("reserve"),10)||235),CELLMAX=Math.max(18,parseInt(qs.get("cell"),10)||40);
var canvas=$("#board"),ctx=canvas.getContext("2d");
var g=null,timer=null,lastFall=0,fallMs=700;
var SHAPES=[[[0,0]],[[0,0],[1,0]],[[0,0],[0,1]],[[0,0],[1,0],[0,1]]];
function newPiece(){
  var sh=SHAPES[Math.floor(Math.random()*SHAPES.length)];
  var cells=sh.map(function(c){return {dx:c[0],dy:c[1],t:Math.random()<0.34?"H":"P"};});
  return {x:Math.floor(COLS/2),y:0,cells:cells};
}
function reset(){
  g={grid:[],piece:newPiece(),next:newPiece(),layers:0,score:0,misfolds:0,
     chaperone:1,over:false,confetti:null,running:false};
  for(var y=0;y<ROWS;y++){g.grid.push(new Array(COLS).fill(null));}
  fallMs=700;renderHUD();
}
function renderHUD(){
  $("#s1").textContent=g.layers+" / 6";
  $("#s2").textContent=g.score;
  var h="";for(var i=0;i<3;i++)h+='<span class="'+(i<g.misfolds?"":"off")+'" style="color:var(--bad)">●</span>';
  $("#hearts").innerHTML=h;
  var cb=$("#chap-btn");
  cb.textContent="Chaperone rescue · "+g.chaperone+" left";
  cb.disabled=!g.chaperone||!g.running;
}
function cellsOf(p){return p.cells.map(function(c){return {x:p.x+c.dx,y:p.y+c.dy,t:c.t};});}
function fits(p){
  return cellsOf(p).every(function(c){
    return c.x>=0&&c.x<COLS&&c.y<ROWS&&(c.y<0||!g.grid[c.y][c.x]);
  });
}
function move(dx){var p={x:g.piece.x+dx,y:g.piece.y,cells:g.piece.cells};if(fits(p))g.piece=p;}
function rotate(){
  var cells=g.piece.cells.map(function(c){return {dx:-c.dy,dy:c.dx,t:c.t};});
  var p={x:g.piece.x,y:g.piece.y,cells:cells};
  if(fits(p))g.piece=p;
}
function softDrop(){var p={x:g.piece.x,y:g.piece.y+1,cells:g.piece.cells};
  if(fits(p)){g.piece=p;return true;}return false;}
function hardDrop(){while(softDrop()){}lock();}
function lock(){
  var top=false;
  cellsOf(g.piece).forEach(function(c){
    if(c.y<0){top=true;return;}
    g.grid[c.y][c.x]={t:c.t,mis:false};
  });
  if(top)return endGame(false,"The chain overflowed — aggregation. Misfolded, clumped proteins are behind diseases such as Alzheimer's and Parkinson's.");
  scanRows();
  if(g.over)return;
  g.piece=g.next;g.next=newPiece();
  if(!fits(g.piece))return endGame(false,"The chain overflowed — aggregation. Misfolded, clumped proteins are behind diseases such as Alzheimer's and Parkinson's.");
}
function rowFull(y){return g.grid[y].every(function(c){return c;});}
function rowValid(y){
  for(var x=0;x<COLS;x++){
    var c=g.grid[y][x],inCore=x>=CORE_LO&&x<=CORE_HI;
    if(c.t==="H"&&!inCore)return "a hydrophobic residue is facing the water";
    if(c.t==="P"&&inCore)return "a polar residue is trapped in the oily core";
  }
  return null;
}
function clearRow(y){
  g.grid.splice(y,1);g.grid.unshift(new Array(COLS).fill(null));
}
function scanRows(){
  for(var y=ROWS-1;y>=0;y--){
    if(!rowFull(y))continue;
    var already=g.grid[y].some(function(c){return c.mis;});
    if(already)continue;
    var why=rowValid(y);
    if(!why){
      clearRow(y);g.layers++;g.score+=100;
      setBanner("Layer buried — the core stays dry","ok");
      fallMs=Math.max(380,fallMs-45);
      y++; // recheck same index after collapse
      if(g.layers>=6)return endGame(true,null);
    }else{
      g.grid[y].forEach(function(c){c.mis=true;});
      g.misfolds++;
      setBanner("Misfolded: "+why,"no");
      if(g.misfolds>=3)return endGame(false,"Three misfolded layers clumped together — aggregation. In cells, aggregates of misfolded protein are cleared by quality control; when that fails, disease can follow.");
    }
  }
  renderHUD();
}
function chaperone(){
  if(!g.chaperone||!g.running)return;
  for(var y=ROWS-1;y>=0;y--){
    if(g.grid[y].some(function(c){return c&&c.mis;})){
      g.grid.splice(y,1);g.grid.unshift(new Array(COLS).fill(null));
      g.chaperone--;g.misfolds=Math.max(0,g.misfolds-1);
      setBanner("Chaperone rescue — the misfolded layer was unfolded and released","vi");
      renderHUD();return;
    }
  }
  setBanner("No misfolded layer to rescue — chaperones act on misfolds","vi");
}
function endGame(won,msg){
  g.over=true;g.running=false;renderHUD();
  if(won&&!reducedMotion()){
    g.confetti=makeConfetti(COLS*cell,ROWS*cell);
    cancelAnimationFrame(timer);timer=requestAnimationFrame(loop);
  }
  var ov=$("#overlay");
  setTimeout(function(){
    ov.hidden=false;
    ov.innerHTML= won?
      '<h2>Folded! The domain is stable.</h2>'+
      '<p><strong>'+g.score+' points</strong> · 6 layers buried with the oily core hidden from water.</p>'+
      '<div class="facts">'+
      '<div>You just used the <strong>hydrophobic effect</strong> — the main force that folds real proteins: oily residues cluster inside, polar residues face the water.</div>'+
      '<div>The amino-acid <strong>sequence</strong> decided what you could build — sequence determines structure, and structure determines function.</div>'+
      '<div>Your chaperone rescue is real: chaperone proteins catch and refold misfolded chains in every cell.</div>'+
      '<div>Simplification to know: real folding is 3D, fast, and cooperative — not falling blocks. The placement rule is the true part.</div>'+
      '</div><button class="btn" id="start-btn">Fold another domain</button>'
      :
      '<h2>Aggregation</h2><p>'+msg+'</p>'+
      '<p class="muted">Score: '+g.score+' · '+g.layers+' layers buried. Try again — watch where H and P land before you drop.</p>'+
      '<button class="btn" id="start-btn">Try again</button>';
    $("#start-btn").addEventListener("click",start);
  },won&&!reducedMotion()?2000:600);
}
function start(){
  reset();$("#overlay").hidden=true;
  g.running=true;lastFall=performance.now();
  cancelAnimationFrame(timer);timer=requestAnimationFrame(loop);
}
function loop(now){
  if(g.running&&now-lastFall>=fallMs){
    lastFall=now;
    if(!softDrop())lock();
  }
  if(g.confetti&&g.confetti.length)g.confetti=stepConfetti(g.confetti,ROWS*cell,0.016);
  draw();
  if(g.running||(g.confetti&&g.confetti.length))timer=requestAnimationFrame(loop);
}
function sizeCanvas(){
  var w=canvas.parentElement.clientWidth;
  var top=canvas.parentElement.getBoundingClientRect().top;
  var availH=Math.max(260,window.innerHeight-Math.max(60,top)-RESERVE);
  cell=Math.max(18,Math.min(Math.floor(w/COLS),Math.floor(availH/ROWS),CELLMAX));
  dpr=Math.min(window.devicePixelRatio||1,3);
  canvas.style.width=(cell*COLS)+"px";canvas.style.height=(cell*ROWS)+"px";
  canvas.width=Math.round(cell*COLS*dpr);canvas.height=Math.round(cell*ROWS*dpr);
  ctx.setTransform(dpr,0,0,dpr,0,0);
}
window.FTfit=function(o){o=o||{};
  if(o.rows)ROWS=Math.max(8,Math.min(16,o.rows));
  if(o.cell)CELLMAX=Math.max(18,o.cell);
  if(o.reserve!=null)RESERVE=Math.max(0,o.reserve);
  sizeCanvas();reset();draw();
  return {rows:ROWS,cellPx:cell,boardPx:cell*ROWS,reserve:RESERVE,fitsViewport:(canvas.getBoundingClientRect().bottom<=window.innerHeight)};
};
function colorOf(c,dark){
  if(c.mis)return dark?"#5A646E":"#9AA5B1";
  return c.t==="H"?"#C98F2C":"#4A69C4";
}
function draw(){
  var dark=isDark(),W=COLS*cell,H=ROWS*cell;
  ctx.fillStyle=dark?"#1F2228":"#FFFFFF";ctx.fillRect(0,0,canvas.width,canvas.height);
  // water edges + core tint
  ctx.fillStyle=dark?"rgba(74,105,196,.12)":"rgba(74,105,196,.07)";
  ctx.fillRect(0,0,CORE_LO*cell,H);ctx.fillRect((CORE_HI+1)*cell,0,W-(CORE_HI+1)*cell,H);
  ctx.fillStyle=dark?"rgba(201,143,44,.14)":"rgba(201,143,44,.1)";
  ctx.fillRect(CORE_LO*cell,0,(CORE_HI-CORE_LO+1)*cell,H);
  var ink=dark?"rgba(232,234,237,.5)":"rgba(31,41,51,.45)";
  ctx.fillStyle=ink;ctx.font="700 11px "+"ui-sans-serif,system-ui";ctx.textAlign="center";
  ctx.fillText("water",CORE_LO*cell/2,14);
  ctx.fillText("CORE",W/2,14);
  ctx.fillText("water",(CORE_HI+1)*cell+(W-(CORE_HI+1)*cell)/2,14);
  if(!g)return;
  function drawCell(x,y,c,ghost){
    var px=x*cell,py=y*cell;
    ctx.globalAlpha=ghost?0.35:1;
    ctx.fillStyle=colorOf(c,dark);
    rrp(ctx,px+2,py+2,cell-4,cell-4,6);ctx.fill();
    if(cell>=24){
      ctx.fillStyle=c.mis?(dark?"#D98378":"#A83E32"):"#fff";
      ctx.font="700 "+Math.round(cell*0.42)+"px ui-sans-serif,system-ui";ctx.textAlign="center";
      ctx.fillText(c.t,px+cell/2,py+cell*0.66);
    }
    ctx.globalAlpha=1;
  }
  for(var y=0;y<ROWS;y++)for(var x=0;x<COLS;x++)if(g.grid[y][x])drawCell(x,y,g.grid[y][x]);
  if(g.running)cellsOf(g.piece).forEach(function(c){if(c.y>=0)drawCell(c.x,c.y,{t:c.t});});
  if(g.confetti)drawConfetti(ctx,g.confetti);
}
document.getElementById("foldpad").addEventListener("click",function(e){
  var b=e.target.closest("[data-k]");if(!b||!g.running)return;
  var k=b.dataset.k;
  if(k==="left")move(-1);else if(k==="right")move(1);
  else if(k==="rot")rotate();else if(k==="drop")hardDrop();
  draw();
});
$("#chap-btn").addEventListener("click",chaperone);
document.addEventListener("keydown",function(e){
  if(!g||!g.running)return;
  if(e.key==="ArrowLeft"){e.preventDefault();move(-1);}
  else if(e.key==="ArrowRight"){e.preventDefault();move(1);}
  else if(e.key==="ArrowUp"){e.preventDefault();rotate();}
  else if(e.key==="ArrowDown"){e.preventDefault();if(!softDrop())lock();}
  else if(e.key===" "){e.preventDefault();hardDrop();}
  draw();
});
var tS=null;
canvas.addEventListener("touchstart",function(e){if(e.touches.length)tS={x:e.touches[0].clientX,y:e.touches[0].clientY,t:Date.now()};},{passive:true});
canvas.addEventListener("touchend",function(e){
  if(!tS||!g||!g.running)return;
  var dx=e.changedTouches[0].clientX-tS.x,dy=e.changedTouches[0].clientY-tS.y;
  if(Math.abs(dx)<16&&Math.abs(dy)<16){rotate();}
  else if(Math.abs(dx)>Math.abs(dy)){move(dx>0?1:-1);}
  else if(dy>0){hardDrop();}
  tS=null;draw();
},{passive:true});
document.addEventListener("visibilitychange",function(){
  if(document.hidden&&g&&g.running){g.running=false;
    var ov=$("#overlay");ov.hidden=false;
    ov.innerHTML='<h2>Paused</h2><button class="btn" id="start-btn">Restart</button>';
    $("#start-btn").addEventListener("click",start);}
});
window.addEventListener("resize",function(){sizeCanvas();draw();});
sizeCanvas();reset();draw();
$("#start-btn").addEventListener("click",start);
""",
  quiz=[
   dict(stem="A protein is:",opts=["A kind of DNA","A chain of amino acids folded into a 3D shape","A single round molecule with no structure"],a=1,
        explain="Proteins are amino-acid chains, and their folded 3D shape is what lets them work — catalyze reactions, carry signals, build structure."),
   dict(stem="What mainly drives a protein to fold?",opts=["Hydrophobic (oily) residues burying away from water","Gravity pulling the chain down","Sunlight"],a=0,
        explain="The hydrophobic effect: in a watery cell, oily residues cluster inward and water-loving residues face out. That's the rule you played."),
   dict(stem="Where do hydrophobic residues belong in a folded protein?",opts=["On the water-facing surface","Buried in the core","Outside the cell"],a=1,
        explain="H residues hide in the dry core; P residues face the water. A protein with oily residues exposed is unstable — your misfolded rows."),
   dict(stem="Misfolded proteins that clump together are called:",opts=["Aggregates — associated with diseases such as Alzheimer's","Vitamins","Enzymes"],a=0,
        explain="Aggregation of misfolded protein is a real failure mode, linked to neurodegenerative diseases. Cells fight it constantly."),
   dict(stem="What do chaperone proteins do?",opts=["Digest food","Help other proteins fold and rescue misfolded ones","Copy DNA"],a=1,
        explain="Chaperones catch misfolding chains, unfold them, and give them another chance — your one-per-game rescue button is their job description."),
   dict(stem="What determines how a protein folds?",opts=["Its amino-acid sequence","The time of day","The cell's color"],a=0,
        explain="Sequence determines structure; structure determines function. That chain of logic runs through all of molecular biology — and through AlphaFold."),
  ],
  simplification="Simplified on purpose: real folding is three-dimensional and cooperative, not falling blocks — the placement rule (H in, P out) is the true part.")

# ============================================================ PHAGOCYTE PATROL
GAMES["phago"] = dict(
  title="Phagocyte Patrol", tag="Clear the tissue, engulf the invaders",
  codep="PP",
  extra_css="""
.opso{height:8px;border-radius:999px;background:var(--line);overflow:hidden;margin-top:8px;opacity:0;transition:opacity .2s}
.opso.on{opacity:1}
.opso i{display:block;height:100%;background:var(--violet);width:100%}
""",
  hud=STD_HUD.replace("{L1}","Debris cleared").replace("{V1}","0")
            .replace("{L2}","Engulfed").replace("{V2}","0")
            .replace("{L3}","Health")
      + '<div class="opso" id="opso"><i id="opso-i"></i></div>',
  stage_inner=flashcard(
    "Innate immunity · phagocytosis & opsonization",
    "You are a macrophage — the immune system's clean-up cell.",
    "Phagocytes such as macrophages patrol your tissues and <strong>engulf</strong> pathogens and debris — a process called <strong>phagocytosis</strong>. Some bacteria have slippery capsules that resist engulfment. The counter-move is <strong>opsonization</strong>: antibodies coat the pathogen, turning it into an easy target. The power-up in this game is real immunology.",
    ["Define phagocytosis and name the cells that do it.",
     "Explain opsonization: antibodies tag pathogens so phagocytes engulf them.",
     "Say why innate and adaptive immunity work as a team — and where vaccines fit in."],
    ["Steer the macrophage; sweep up <strong>cell debris</strong> (dots) as you patrol.",
     "Avoid the roaming <strong>encapsulated pathogens</strong> — touching one costs health.",
     "Grab an <strong>antibody dose</strong> (◆): pathogens get coated for a few seconds — chase them down and engulf!"],
    "Clear all debris to win. Three hits and the infection takes hold.",
    "Start patrol"),
  controls=PAD + '<p class="ctrl-note">Swipe on the board or use the arrows · desktop: arrow keys / WASD</p>',
  js=r"""
var MAZE=[
"#############",
"#O...#.#...O#",
"#.##.#.#.##.#",
"#.#.......#.#",
"#.#.##.##.#.#",
"#.....#.....#",
"###.#.#.#.###",
"#...#...#...#",
"#.#.##.##.#.#",
"#.#.......#.#",
"#.##.#.#.##.#",
"#....#.#....#",
"#.##.....##.#",
"#O...###...O#",
"#############"];
var COLS=13,ROWS=15,cell=26,dpr=1;
var canvas=$("#board"),ctx=canvas.getContext("2d");
var g=null,timer=null,lastTick=0,TICK=240;
function wall(x,y){return MAZE[y][x]==="#";}
function reset(){
  g={px:6,py:12,dir:{x:0,y:0},queue:null,hearts:3,debris:0,engulfed:0,score:0,
     pellets:{},powers:{},nPellets:0,ghosts:[],opso:0,over:false,running:false,confetti:null,inv:0};
  for(var y=0;y<ROWS;y++)for(var x=0;x<COLS;x++){
    if(MAZE[y][x]==="."){g.pellets[x+","+y]=1;g.nPellets++;}
    if(MAZE[y][x]==="O")g.powers[x+","+y]=1;
  }
  delete g.pellets[g.px+","+g.py];g.nPellets--;
  g.ghosts=[{x:6,y:5},{x:3,y:3},{x:9,y:3}].map(function(p,i){
    return {x:p.x,y:p.y,home:p,dir:{x:0,y:0},color:["#5E8C3F","#3E8FA8","#A8653E"][i],dead:0};
  });
  renderHUD();
}
function renderHUD(){
  $("#s1").textContent=g.debris;
  $("#s2").textContent=g.engulfed;
  var h="";for(var i=0;i<3;i++)h+='<span class="'+(i<g.hearts?"":"off")+'" style="color:var(--bad)">●</span>';
  $("#hearts").innerHTML=h;
}
function canGo(x,y,d){return !wall(x+d.x,y+d.y);}
function step(){
  if(g.inv>0)g.inv--;
  if(g.queue&&canGo(g.px,g.py,g.queue)){g.dir=g.queue;g.queue=null;}
  if(canGo(g.px,g.py,g.dir)){g.px+=g.dir.x;g.py+=g.dir.y;}
  var k=g.px+","+g.py;
  if(g.pellets[k]){delete g.pellets[k];g.debris++;g.score+=5;g.nPellets--;}
  if(g.powers[k]){
    delete g.powers[k];g.opso=28;g.score+=20;
    setBanner("Opsonized! Antibodies have coated the pathogens — engulf them now","vi");
  }
  if(g.opso>0)g.opso--;
  $("#opso").className="opso"+(g.opso>0?" on":"");
  $("#opso-i").style.width=Math.round(g.opso/28*100)+"%";
  // ghosts
  g.ghosts.forEach(function(gh){
    if(gh.dead>0){gh.dead--;if(gh.dead===0){gh.x=gh.home.x;gh.y=gh.home.y;}return;}
    var opts=[{x:1,y:0},{x:-1,y:0},{x:0,y:1},{x:0,y:-1}].filter(function(d){
      return canGo(gh.x,gh.y,d)&&!(d.x===-gh.dir.x&&d.y===-gh.dir.y);});
    if(!opts.length)opts=[{x:-gh.dir.x,y:-gh.dir.y}];
    var pick;
    var chase=Math.random()<(g.opso>0?0.1:0.45);
    if(chase){
      opts.sort(function(a,b){
        var da=Math.abs(gh.x+a.x-g.px)+Math.abs(gh.y+a.y-g.py);
        var db=Math.abs(gh.x+b.x-g.px)+Math.abs(gh.y+b.y-g.py);
        return g.opso>0?(db-da):(da-db);
      });
      pick=opts[0];
    }else pick=opts[Math.floor(Math.random()*opts.length)];
    gh.dir=pick;gh.x+=pick.x;gh.y+=pick.y;
  });
  // collisions
  g.ghosts.forEach(function(gh){
    if(gh.dead>0)return;
    if(gh.x===g.px&&gh.y===g.py){
      if(g.opso>0){
        gh.dead=16;g.engulfed++;g.score+=100;
        setBanner("Engulfed! Opsonized pathogens are easy prey","ok");
      }else if(g.inv===0){
        g.hearts--;g.inv=8;
        setBanner("Its capsule resisted engulfment — you took damage","no");
        if(g.hearts<=0)return endGame(false);
      }
    }
  });
  renderHUD();
  if(g.nPellets<=0&&Object.keys(g.powers).length===0&&!g.over)endGame(true);
}
function endGame(won){
  g.over=true;g.running=false;
  if(won&&!reducedMotion()){
    g.confetti=makeConfetti(COLS*cell,ROWS*cell);
    cancelAnimationFrame(timer);timer=requestAnimationFrame(loop);
  }
  setTimeout(function(){
    var ov=$("#overlay");ov.hidden=false;
    ov.innerHTML= won?
      '<h2>Tissue cleared!</h2>'+
      '<p><strong>'+g.score+' points</strong> · '+g.debris+' debris removed · '+g.engulfed+' pathogens engulfed.</p>'+
      '<div class="facts">'+
      '<div><strong>Phagocytosis</strong> is real: macrophages and neutrophils patrol tissue and literally eat pathogens and debris — your body’s first responders, no learning required.</div>'+
      '<div>The power-up was <strong>opsonization</strong>: antibodies (made by adaptive immunity’s B cells) coat pathogens so phagocytes grip and engulf them easily.</div>'+
      '<div>That teamwork — innate speed plus adaptive precision — is why vaccines help you clear infections faster: they stock you with ready antibodies.</div>'+
      '<div>Simplification to know: macrophages don’t chase through mazes, and capsules are one of several evasion tricks — the tagging-helps-eating rule is the true part.</div>'+
      '</div><button class="btn" id="start-btn">Patrol again</button>'
      :
      '<h2>The infection took hold</h2>'+
      '<p>Even real macrophages need backup — that’s exactly why innate and adaptive immunity work as a team. Grab the antibody dose before taking on the pathogens.</p>'+
      '<p class="muted">Score: '+g.score+'</p>'+
      '<button class="btn" id="start-btn">Try again</button>';
    $("#start-btn").addEventListener("click",start);
  },won&&!reducedMotion()?2000:600);
}
function start(){
  reset();$("#overlay").hidden=true;
  g.running=true;lastTick=performance.now();
  cancelAnimationFrame(timer);timer=requestAnimationFrame(loop);
}
function loop(now){
  if(g.running&&now-lastTick>=TICK){lastTick=now;step();}
  if(g.confetti&&g.confetti.length)g.confetti=stepConfetti(g.confetti,ROWS*cell,0.016);
  draw();
  if(g.running||(g.confetti&&g.confetti.length))timer=requestAnimationFrame(loop);
}
function sizeCanvas(){
  var w=canvas.parentElement.clientWidth;
  cell=Math.floor(w/COLS);
  dpr=Math.min(window.devicePixelRatio||1,3);
  canvas.style.height=(cell*ROWS)+"px";
  canvas.width=Math.round(w*dpr);canvas.height=Math.round(cell*ROWS*dpr);
  ctx.setTransform(dpr,0,0,dpr,0,0);
}
function draw(){
  var dark=isDark();
  ctx.fillStyle=dark?"#1F2228":"#FFF7F2";ctx.fillRect(0,0,canvas.width,canvas.height);
  for(var y=0;y<ROWS;y++)for(var x=0;x<COLS;x++){
    if(wall(x,y)){
      ctx.fillStyle=dark?"#3A251D":"#F0D9CE";
      rrp(ctx,x*cell+1,y*cell+1,cell-2,cell-2,5);ctx.fill();
    }
  }
  if(!g)return;
  ctx.fillStyle=dark?"#9AA5B1":"#B8A79B";
  Object.keys(g.pellets).forEach(function(k){
    var p=k.split(",");ctx.beginPath();ctx.arc(+p[0]*cell+cell/2,+p[1]*cell+cell/2,cell*0.09,0,7);ctx.fill();
  });
  Object.keys(g.powers).forEach(function(k){
    var p=k.split(",");var cx=+p[0]*cell+cell/2,cy=+p[1]*cell+cell/2,r=cell*0.3;
    ctx.fillStyle=dark?"#B08CE8":"#8A4BD9";
    ctx.beginPath();ctx.moveTo(cx,cy-r);ctx.lineTo(cx+r,cy);ctx.lineTo(cx,cy+r);ctx.lineTo(cx-r,cy);ctx.closePath();ctx.fill();
    if(cell>=26){ctx.fillStyle="#fff";ctx.font="700 "+Math.round(cell*0.24)+"px ui-sans-serif";ctx.textAlign="center";ctx.fillText("Ab",cx,cy+cell*0.09);}
  });
  g.ghosts.forEach(function(gh){
    if(gh.dead>0)return;
    var cx=gh.x*cell+cell/2,cy=gh.y*cell+cell/2,r=cell*0.38;
    ctx.fillStyle=g.opso>0?(dark?"#B08CE8":"#8A4BD9"):gh.color;
    ctx.beginPath();ctx.arc(cx,cy-r*0.15,r,Math.PI,0);
    ctx.lineTo(cx+r,cy+r*0.7);ctx.lineTo(cx+r*0.33,cy+r*0.45);ctx.lineTo(cx-r*0.33,cy+r*0.7);ctx.lineTo(cx-r,cy+r*0.45);
    ctx.closePath();ctx.fill();
    if(g.opso===0){
      ctx.strokeStyle=dark?"rgba(255,255,255,.55)":"rgba(255,255,255,.8)";
      ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(cx,cy,r+2.5,0,7);ctx.stroke();
    }else if(cell>=26){
      ctx.fillStyle="#fff";ctx.font="700 "+Math.round(cell*0.24)+"px ui-sans-serif";ctx.textAlign="center";ctx.fillText("Ab",cx,cy+cell*0.08);
    }
    ctx.fillStyle="#fff";
    ctx.beginPath();ctx.arc(cx-r*0.35,cy-r*0.25,r*0.16,0,7);ctx.arc(cx+r*0.35,cy-r*0.25,r*0.16,0,7);ctx.fill();
  });
  var cx=g.px*cell+cell/2,cy=g.py*cell+cell/2,r=cell*0.42;
  ctx.globalAlpha=g.inv>0?(g.inv%2?0.35:1):1;
  ctx.fillStyle=dark?"#D68264":"#B04A2F";
  ctx.beginPath();
  var ang=0.28*Math.PI*(0.6+0.4*Math.sin(Date.now()/160));
  var base=g.dir.x===1?0:g.dir.x===-1?Math.PI:g.dir.y===1?Math.PI/2:g.dir.y===-1?-Math.PI/2:0;
  ctx.moveTo(cx,cy);ctx.arc(cx,cy,r,base+ang/2,base-ang/2+Math.PI*2);ctx.closePath();ctx.fill();
  ctx.globalAlpha=1;
  if(g.confetti)drawConfetti(ctx,g.confetti);
}
function queueDir(x,y){if(g&&g.running)g.queue={x:x,y:y};}
var tS=null;
canvas.addEventListener("touchstart",function(e){if(e.touches.length)tS={x:e.touches[0].clientX,y:e.touches[0].clientY};},{passive:true});
canvas.addEventListener("touchend",function(e){
  if(!tS)return;
  var dx=e.changedTouches[0].clientX-tS.x,dy=e.changedTouches[0].clientY-tS.y;
  if(Math.abs(dx)<18&&Math.abs(dy)<18)return;
  if(Math.abs(dx)>Math.abs(dy))queueDir(dx>0?1:-1,0);else queueDir(0,dy>0?1:-1);
  tS=null;
},{passive:true});
document.getElementById("pad").addEventListener("click",function(e){
  var b=e.target.closest("[data-k]");if(!b)return;
  var m={up:[0,-1],down:[0,1],left:[-1,0],right:[1,0]}[b.dataset.k];
  queueDir(m[0],m[1]);
});
document.addEventListener("keydown",function(e){
  if(!g||!g.running)return;
  var k=e.key;
  if(k==="ArrowUp"||k==="w"||k==="W"){e.preventDefault();queueDir(0,-1);}
  else if(k==="ArrowDown"||k==="s"||k==="S"){e.preventDefault();queueDir(0,1);}
  else if(k==="ArrowLeft"||k==="a"||k==="A"){e.preventDefault();queueDir(-1,0);}
  else if(k==="ArrowRight"||k==="d"||k==="D"){e.preventDefault();queueDir(1,0);}
});
document.addEventListener("visibilitychange",function(){
  if(document.hidden&&g&&g.running){g.running=false;
    var ov=$("#overlay");ov.hidden=false;
    ov.innerHTML='<h2>Paused</h2><button class="btn" id="start-btn">Restart</button>';
    $("#start-btn").addEventListener("click",start);}
});
window.addEventListener("resize",function(){sizeCanvas();draw();});
sizeCanvas();reset();draw();
$("#start-btn").addEventListener("click",start);
""",
  quiz=[
   dict(stem="Phagocytosis means:",opts=["A cell engulfing and digesting particles such as pathogens","A cell dividing in two","A virus copying itself"],a=0,
        explain="From Greek 'phagein' — to eat. Macrophages ('big eaters') and neutrophils clear pathogens and debris this way, exactly as you just played."),
   dict(stem="A macrophage belongs to which arm of the immune system?",opts=["Adaptive — slow and specific","Innate — fast, first-line, ready from birth","Neither; it is a bacterium"],a=1,
        explain="Innate immunity responds within minutes and needs no prior training. The adaptive arm (B and T cells) is slower but precise."),
   dict(stem="Opsonization is:",opts=["Antibodies coating a pathogen so phagocytes can engulf it easily","A pathogen eating a macrophage","A kind of vitamin"],a=0,
        explain="Opsonins (antibodies, complement) tag the pathogen's surface and give phagocytes a handle to grip — the game's power-up, for real."),
   dict(stem="Why can some bacteria resist being engulfed?",opts=["They are too hot","Slippery capsules and surface tricks make them hard to grip","They apologize"],a=1,
        explain="Capsules are a classic evasion strategy — the white ring on the game's pathogens. Opsonization defeats it by giving phagocytes something to hold."),
   dict(stem="Where do the antibodies that opsonize pathogens come from?",opts=["The pathogens themselves","B cells of the adaptive immune system","The stomach"],a=1,
        explain="B cells make antibodies — adaptive immunity arming the innate clean-up crew. Two systems, one team."),
   dict(stem="How does vaccination connect to what you played?",opts=["It teaches macrophages to run faster","It stocks you with ready antibodies, so pathogens get opsonized and cleared sooner","It has no connection"],a=1,
        explain="Vaccines train adaptive immunity in advance. When the real pathogen shows up, antibodies coat it immediately — the power-up is already active."),
  ],
  simplification="Simplified on purpose: macrophages don’t chase through mazes, and capsules are one of several evasion tactics — the tagging-makes-engulfing-easier rule is the true part.")

# ============================================================ DRUG FLIGHT
GAMES["drug"] = dict(
  title="Drug Flight", tag="Keep the dose in the therapeutic window",
  codep="DF",
  extra_css="",
  hud=STD_HUD.replace("{L1}","Dose intervals survived").replace("{V1}","0 / 15")
            .replace("{L2}","Score").replace("{V2}","0")
            .replace("{L3}","Safety margin"),
  stage_inner=flashcard(
    "Pharmacokinetics · the therapeutic window",
    "A drug only works inside its window.",
    "After a dose, drug concentration in your blood <strong>rises</strong> (absorption), then is constantly <strong>pulled down</strong> as the liver metabolizes and the kidneys excrete it — together called <strong>clearance</strong>. The <strong>therapeutic window</strong> is the concentration range between <em>too low to work</em> and <em>high enough to be toxic</em>. Dosing is the art of staying inside it over time.",
    ["Explain why drug levels rise and fall: absorption versus clearance (liver and kidneys).",
     "Define the therapeutic window: below it, no effect; above it, toxicity.",
     "Say why dose timing matters — a missed dose drops you out of the window."],
    ["Your dot is the drug concentration. <strong>Gravity is clearance</strong> — it never stops pulling you down.",
     "Tap (or press space) to take a <strong>dose</strong> — each tap is an absorption boost upward.",
     "Fly through the gaps — each gap is the <strong>therapeutic window</strong> between the toxic zone above and the no-effect zone below. Liver and kidney pillars mark each clearance interval."],
    "Survive 15 dose intervals to reach steady state. Three crashes end the run.",
    "Take first dose"),
  controls='<p class="ctrl-note">Tap the board to dose · desktop: space or click</p>',
  js=r"""
var canvas=$("#board"),ctx=canvas.getContext("2d");
var W=360,H=430,dpr=1;
var g=null,timer=null,lastT=0;
var GRAV=1150,IMP=-330,SPEED0=115;
function reset(){
  g={y:H/2,vy:0,pipes:[],t:0,passed:0,score:0,hearts:3,speed:SPEED0,
     over:false,running:false,confetti:null,inv:0,nextX:W+60,gap:150,count:0};
  renderHUD();
}
function renderHUD(){
  $("#s1").textContent=g.passed+" / 15";
  $("#s2").textContent=g.score;
  var h="";for(var i=0;i<3;i++)h+='<span class="'+(i<g.hearts?"":"off")+'" style="color:var(--bad)">●</span>';
  $("#hearts").innerHTML=h;
}
var TOX=56,LOW=56;
function spawnPipe(){
  var gapY=TOX+30+Math.random()*(H-TOX-LOW-60-g.gap);
  g.pipes.push({x:g.nextX,gapY:gapY,gapH:g.gap,organ:(g.count%2?"KIDNEY":"LIVER"),passed:false});
  g.count++;g.nextX=0;
}
function hurt(msg){
  if(g.inv>0)return;
  g.hearts--;g.inv=1.4;setBanner(msg,"no");renderHUD();
  if(g.hearts<=0){endGame(false,msg);return;}
  g.y=H/2;g.vy=0;
}
function step(dt){
  g.t+=dt;if(g.inv>0)g.inv-=dt;
  g.vy+=GRAV*dt;g.y+=g.vy*dt;
  g.speed=Math.min(175,SPEED0+g.passed*4);
  g.gap=Math.max(118,150-g.passed*2);
  g.pipes.forEach(function(p){p.x-=g.speed*dt;});
  if(!g.pipes.length||g.pipes[g.pipes.length-1].x<W-230){g.nextX=W+40;spawnPipe();}
  g.pipes=g.pipes.filter(function(p){return p.x>-70;});
  var bx=86,r=13;
  if(g.y-r<TOX)hurt("Overdose — concentration rose above the therapeutic window into the toxic zone");
  if(g.y+r>H-LOW)hurt("Too low — below the window the drug simply stops working");
  if(g.over)return;
  g.pipes.forEach(function(p){
    var inX=bx+r>p.x&&bx-r<p.x+46;
    if(inX&&(g.y-r<p.gapY||g.y+r>p.gapY+p.gapH)){
      hurt("Cleared by the "+p.organ.toLowerCase()+" — concentration crashed out of the window");
    }else if(!p.passed&&p.x+46<bx-r){
      p.passed=true;g.passed++;g.score+=10;renderHUD();
      if(g.passed>=15)endGame(true,null);
    }
  });
}
function dose(){
  if(!g||!g.running)return;
  g.vy=IMP;
}
function endGame(won,msg){
  g.over=true;g.running=false;
  if(won&&!reducedMotion()){
    g.confetti=makeConfetti(W,H);
    cancelAnimationFrame(timer);timer=requestAnimationFrame(loop);
  }
  setTimeout(function(){
    var ov=$("#overlay");ov.hidden=false;
    ov.innerHTML= won?
      '<h2>Steady state — 15 intervals in the window.</h2>'+
      '<p><strong>'+g.score+' points.</strong> You kept the concentration effective and safe, dose after dose.</p>'+
      '<div class="facts">'+
      '<div>Gravity was <strong>clearance</strong>: the liver metabolizes drugs and the kidneys excrete them, pulling concentration down around the clock.</div>'+
      '<div>Each tap was a <strong>dose</strong>; the gap was the <strong>therapeutic window</strong> — above it toxicity, below it no effect.</div>'+
      '<div>That’s why prescriptions say “every 8 hours”: the schedule is timed to clearance, keeping levels inside the window.</div>'+
      '<div>Simplification to know: real concentrations follow smooth exponential curves, and windows differ per drug and per patient — pharmacokinetic models (Module 4) compute them.</div>'+
      '</div><button class="btn" id="start-btn">Fly again</button>'
      :
      '<h2>Out of the window</h2><p>'+msg+'</p>'+
      '<p class="muted">Intervals survived: '+g.passed+'. Small, timely doses beat big panicked ones — just like real dosing.</p>'+
      '<button class="btn" id="start-btn">Try again</button>';
    $("#start-btn").addEventListener("click",start);
  },won&&!reducedMotion()?2000:600);
}
function start(){
  reset();$("#overlay").hidden=true;
  g.running=true;lastT=performance.now();
  cancelAnimationFrame(timer);timer=requestAnimationFrame(loop);
}
function loop(now){
  var dt=Math.min(0.033,(now-lastT)/1000);lastT=now;
  if(g.running)step(dt);
  if(g.confetti&&g.confetti.length)g.confetti=stepConfetti(g.confetti,H,dt);
  draw();
  if(g.running||(g.confetti&&g.confetti.length))timer=requestAnimationFrame(loop);
}
function sizeCanvas(){
  var w=canvas.parentElement.clientWidth;
  W=w;
  dpr=Math.min(window.devicePixelRatio||1,3);
  canvas.style.height=H+"px";
  canvas.width=Math.round(w*dpr);canvas.height=Math.round(H*dpr);
  ctx.setTransform(dpr,0,0,dpr,0,0);
}
function draw(){
  var dark=isDark();
  ctx.fillStyle=dark?"#1F2228":"#FFFFFF";ctx.fillRect(0,0,canvas.width,canvas.height);
  // zones
  ctx.fillStyle=dark?"rgba(217,131,120,.2)":"rgba(168,62,50,.12)";
  ctx.fillRect(0,0,W,TOX);
  ctx.fillStyle=dark?"rgba(154,165,177,.14)":"rgba(82,96,109,.1)";
  ctx.fillRect(0,H-LOW,W,LOW);
  var ink=dark?"rgba(232,234,237,.6)":"rgba(31,41,51,.55)";
  ctx.fillStyle=ink;ctx.font="700 11px ui-sans-serif,system-ui";ctx.textAlign="left";
  ctx.fillText("TOXIC — above the window",12,20);
  ctx.fillText("TOO LOW — no effect",12,H-LOW+20);
  if(!g)return;
  // pipes
  g.pipes.forEach(function(p){
    ctx.fillStyle=dark?"#3A251D":"#F0D9CE";
    rrp(ctx,p.x,TOX,46,p.gapY-TOX,8);ctx.fill();
    rrp(ctx,p.x,p.gapY+p.gapH,46,H-LOW-(p.gapY+p.gapH),8);ctx.fill();
    // window band
    ctx.fillStyle=dark?"rgba(95,176,132,.16)":"rgba(47,125,82,.12)";
    ctx.fillRect(p.x,p.gapY,46,p.gapH);
    ctx.save();
    ctx.translate(p.x+23,p.gapY-10);
    ctx.fillStyle=ink;ctx.font="700 10px ui-sans-serif";ctx.textAlign="center";
    ctx.fillText(p.organ,0,0);
    ctx.restore();
  });
  // y-axis hint
  ctx.save();ctx.translate(14,H/2);ctx.rotate(-Math.PI/2);
  ctx.fillStyle=dark?"rgba(232,234,237,.35)":"rgba(31,41,51,.3)";
  ctx.font="10px ui-sans-serif";ctx.textAlign="center";
  ctx.fillText("drug concentration →",0,0);ctx.restore();
  // drug dot
  ctx.globalAlpha=g.inv>0?(Math.floor(g.inv*10)%2?0.35:1):1;
  ctx.fillStyle=dark?"#D68264":"#B04A2F";
  ctx.beginPath();ctx.arc(86,g.y,13,0,7);ctx.fill();
  ctx.fillStyle="#fff";ctx.font="700 9px ui-sans-serif";ctx.textAlign="center";
  ctx.fillText("drug",86,g.y+3);
  ctx.globalAlpha=1;
  if(g.confetti)drawConfetti(ctx,g.confetti);
}
canvas.addEventListener("pointerdown",function(e){e.preventDefault();dose();});
document.addEventListener("keydown",function(e){
  if(e.key===" "||e.code==="Space"){if(g&&g.running){e.preventDefault();dose();}}
});
document.addEventListener("visibilitychange",function(){
  if(document.hidden&&g&&g.running){g.running=false;
    var ov=$("#overlay");ov.hidden=false;
    ov.innerHTML='<h2>Paused</h2><button class="btn" id="start-btn">Restart</button>';
    $("#start-btn").addEventListener("click",start);}
});
window.addEventListener("resize",function(){sizeCanvas();draw();});
sizeCanvas();reset();draw();
$("#start-btn").addEventListener("click",start);
""",
  quiz=[
   dict(stem="The therapeutic window of a drug is:",opts=["The hours a pharmacy is open","The concentration range between too-low-to-work and high-enough-to-be-toxic","The shape of the pill"],a=1,
        explain="Below the window a drug does nothing; above it, it harms. Dosing exists to keep blood concentration inside that range — the gap you flew through."),
   dict(stem="What constantly pulls drug concentration down?",opts=["Clearance — the liver metabolizing and the kidneys excreting the drug","Sunlight","Exercise only"],a=0,
        explain="Clearance never stops — that was the gravity in the game. It's why one dose wears off and why dosing is repeated."),
   dict(stem="A drug concentration above the window causes:",opts=["Faster healing","Nothing","Toxicity — side effects and harm"],a=2,
        explain="More is not better. The red zone is real: overdoses are concentrations above the therapeutic window."),
   dict(stem="Why are doses taken on a schedule (e.g., every 8 hours)?",opts=["Tradition","To keep concentration inside the window as clearance pulls it down","Pills expire hourly"],a=1,
        explain="The schedule is matched to how fast the liver and kidneys clear the drug — a timed series of boosts against a constant pull, exactly your gameplay."),
   dict(stem="In the game, gravity represented:",opts=["Clearance by liver and kidneys","Absorption","The placebo effect"],a=0,
        explain="Every metaphor in the game maps: tap = dose (absorption), gravity = clearance, gap = therapeutic window."),
   dict(stem="What happens when a dose is missed?",opts=["Concentration falls below the window and the drug stops working","The drug becomes stronger","Nothing changes"],a=0,
        explain="Concentration keeps falling with clearance, drops out of the window, and the effect is lost — which is why adherence matters so much in real treatment."),
  ],
  simplification="Simplified on purpose: real concentrations follow smooth exponential pharmacokinetic curves and windows differ per drug and patient — the rise-fall-window logic is the true part.")

# ============================================================ LYSIS LAB
GAMES["lysis"] = dict(
  title="Lysis Lab", tag="Break the wall, burst the bacterium",
  codep="LL",
  extra_css="",
  hud=STD_HUD.replace("{L1}","Wall remaining").replace("{V1}","—")
            .replace("{L2}","Score").replace("{V2}","0")
            .replace("{L3}","Antibiotic doses"),
  stage_inner=flashcard(
    "Antibiotics · the bacterial cell wall",
    "Bacteria have a wall. Your cells don't. That's the whole trick.",
    "Bacteria wrap themselves in a mesh wall of <strong>peptidoglycan</strong> that holds them together against their own internal pressure. <strong>Penicillin-class antibiotics</strong> block the enzymes that build this wall — the weakened wall then fails and the cell <strong>bursts (lysis)</strong> under osmotic pressure. Human cells have no wall, which is why these drugs can kill bacteria without killing you: <strong>selective toxicity</strong>.",
    ["Name what the bacterial wall is made of and why losing it bursts the cell.",
     "Explain selective toxicity: wall-targeting antibiotics spare human cells, which have no wall.",
     "Describe one real resistance mechanism (β-lactamase) and one real counter-move (clavulanate)."],
    ["Bounce the <strong>antibiotic</strong> off your paddle into the wall — every gold brick is peptidoglycan.",
     "<strong>β bricks</strong> are β-lactamase, the resistance enzyme: they destroy your antibiotic on contact.",
     "Catch a falling <strong>CLV</strong> capsule (clavulanate): it inhibits β-lactamase for a while, letting your antibiotic break those bricks too."],
    "Clear the wall and osmotic pressure finishes the job. Three lost doses end the run.",
    "Administer antibiotic"),
  controls='<p class="ctrl-note">Drag on the board to move the paddle · desktop: mouse or arrow keys</p>',
  js=r"""
var canvas=$("#board"),ctx=canvas.getContext("2d");
var W=360,H=460,dpr=1;
var g=null,timer=null,lastT=0;
var BR_COLS=9,BR_ROWS=5;
function reset(){
  var brickW=(W-24)/BR_COLS,brickH=24;
  g={paddleX:W/2,ball:null,bricks:[],drops:[],balls:3,score:0,inhib:0,
     over:false,running:false,confetti:null,total:0};
  var betas=[];while(betas.length<6){var r=Math.floor(Math.random()*BR_COLS*BR_ROWS);if(betas.indexOf(r)<0)betas.push(r);}
  var clvs=[];while(clvs.length<3){var r2=Math.floor(Math.random()*BR_COLS*BR_ROWS);if(betas.indexOf(r2)<0&&clvs.indexOf(r2)<0)clvs.push(r2);}
  for(var row=0;row<BR_ROWS;row++)for(var col=0;col<BR_COLS;col++){
    var idx=row*BR_COLS+col;
    g.bricks.push({x:12+col*brickW,y:54+row*(brickH+5),w:brickW-4,h:brickH,
      beta:betas.indexOf(idx)>=0,clv:clvs.indexOf(idx)>=0,alive:true});
    g.total++;
  }
  serveBall();
  renderHUD();
}
function serveBall(){
  g.ball={x:W/2,y:H-110,vx:(Math.random()<0.5?-1:1)*130,vy:-240,r:9,stuck:false};
}
function renderHUD(){
  var left=g.bricks.filter(function(b){return b.alive;}).length;
  $("#s1").textContent=left+" bricks";
  $("#s2").textContent=g.score;
  var h="";for(var i=0;i<3;i++)h+='<span class="'+(i<g.balls?"":"off")+'" style="color:var(--bad)">●</span>';
  $("#hearts").innerHTML=h;
}
function step(dt){
  if(g.inhib>0)g.inhib-=dt;
  var b=g.ball,pw=92,ph=14,py=H-46;
  b.x+=b.vx*dt;b.y+=b.vy*dt;
  if(b.x-b.r<6){b.x=6+b.r;b.vx=Math.abs(b.vx);}
  if(b.x+b.r>W-6){b.x=W-6-b.r;b.vx=-Math.abs(b.vx);}
  if(b.y-b.r<6){b.y=6+b.r;b.vy=Math.abs(b.vy);}
  // paddle
  if(b.vy>0&&b.y+b.r>=py&&b.y+b.r<=py+ph+8&&b.x>g.paddleX-pw/2-4&&b.x<g.paddleX+pw/2+4){
    b.vy=-Math.abs(b.vy)*1.01;
    b.vx+= (b.x-g.paddleX)/ (pw/2) * 110;
    b.vx=Math.max(-280,Math.min(280,b.vx));
  }
  // floor
  if(b.y-b.r>H){
    loseBall("The dose washed out — keep the antibiotic in play");
    return;
  }
  // bricks
  for(var i=0;i<g.bricks.length;i++){
    var br=g.bricks[i];
    if(!br.alive)continue;
    if(b.x+b.r>br.x&&b.x-b.r<br.x+br.w&&b.y+b.r>br.y&&b.y-b.r<br.y+br.h){
      if(br.beta&&g.inhib<=0){
        br.alive=false; // the beta brick is consumed destroying the dose
        loseBall("β-lactamase destroyed the antibiotic — resistance in action");
        return;
      }
      br.alive=false;
      g.score+=br.beta?40:20;
      if(br.beta)setBanner("β-lactamase neutralized — clavulanate is doing its job","vi");
      if(br.clv)g.drops.push({x:br.x+br.w/2,y:br.y+br.h,vy:120});
      var fromSide=Math.min(Math.abs(b.x-br.x),Math.abs(b.x-(br.x+br.w)))<Math.min(Math.abs(b.y-br.y),Math.abs(b.y-(br.y+br.h)));
      if(fromSide)b.vx=-b.vx;else b.vy=-b.vy;
      renderHUD();
      if(!g.bricks.some(function(x){return x.alive;}))return endGame(true);
      break;
    }
  }
  // drops
  g.drops.forEach(function(d){d.y+=d.vy*dt;});
  g.drops=g.drops.filter(function(d){
    if(d.y>py-6&&d.y<py+ph+16&&d.x>g.paddleX-pw/2-10&&d.x<g.paddleX+pw/2+10){
      g.inhib=12;g.score+=30;
      setBanner("Clavulanate caught — β-lactamase inhibited (this combo is real: co-amoxiclav)","vi");
      return false;
    }
    return d.y<H+20;
  });
}
function loseBall(msg){
  g.balls--;setBanner(msg,"no");renderHUD();
  if(g.balls<=0)endGame(false,msg);
  else serveBall();
}
function endGame(won,msg){
  g.over=true;g.running=false;
  if(won&&!reducedMotion()){
    g.confetti=makeConfetti(W,H);
    cancelAnimationFrame(timer);timer=requestAnimationFrame(loop);
  }
  setTimeout(function(){
    var ov=$("#overlay");ov.hidden=false;
    ov.innerHTML= won?
      '<h2>Lysis! Osmotic pressure burst the cell.</h2>'+
      '<p><strong>'+g.score+' points</strong> · wall cleared. With no peptidoglycan to hold it, the bacterium’s own internal pressure did the rest.</p>'+
      '<div class="facts">'+
      '<div>Penicillin-class (β-lactam) antibiotics block the enzymes that build the peptidoglycan wall — the weakened wall fails and the cell bursts.</div>'+
      '<div><strong>Selective toxicity:</strong> your cells have no wall, so wall-targeting drugs can kill bacteria without harming you.</div>'+
      '<div>The β bricks were <strong>β-lactamase</strong>, a real resistance enzyme that chops up the antibiotic — and <strong>clavulanate</strong> is the real inhibitor paired with amoxicillin as co-amoxiclav.</div>'+
      '<div>Simplification to know: antibiotics don’t bounce — they block wall-building chemistry while the bacterium grows. The mechanism and the resistance arms race are the true part.</div>'+
      '</div><button class="btn" id="start-btn">New bacterium</button>'
      :
      '<h2>The infection persisted</h2><p>'+msg+'</p>'+
      '<p class="muted">Score: '+g.score+'. Watch for β bricks — catch clavulanate before engaging them. Resistance is beatable with the right combination.</p>'+
      '<button class="btn" id="start-btn">Try again</button>';
    $("#start-btn").addEventListener("click",start);
  },won&&!reducedMotion()?2000:600);
}
function start(){
  reset();$("#overlay").hidden=true;
  g.running=true;lastT=performance.now();
  cancelAnimationFrame(timer);timer=requestAnimationFrame(loop);
}
function loop(now){
  var dt=Math.min(0.03,(now-lastT)/1000);lastT=now;
  if(g.running)step(dt);
  if(g.confetti&&g.confetti.length)g.confetti=stepConfetti(g.confetti,H,dt);
  draw();
  if(g.running||(g.confetti&&g.confetti.length))timer=requestAnimationFrame(loop);
}
function sizeCanvas(){
  var w=canvas.parentElement.clientWidth;
  W=w;
  dpr=Math.min(window.devicePixelRatio||1,3);
  canvas.style.height=H+"px";
  canvas.width=Math.round(w*dpr);canvas.height=Math.round(H*dpr);
  ctx.setTransform(dpr,0,0,dpr,0,0);
  if(g&&!g.running&&!g.over)reset();
}
function draw(){
  var dark=isDark();
  ctx.fillStyle=dark?"#1F2228":"#FFFFFF";ctx.fillRect(0,0,canvas.width,canvas.height);
  var ink=dark?"rgba(232,234,237,.5)":"rgba(31,41,51,.45)";
  ctx.fillStyle=ink;ctx.font="700 11px ui-sans-serif";ctx.textAlign="center";
  ctx.fillText("peptidoglycan cell wall",W/2,24);
  ctx.fillText("bacterial interior — under osmotic pressure",W/2,40);
  if(!g)return;
  g.bricks.forEach(function(br){
    if(!br.alive)return;
    var col=br.beta?(g.inhib>0?"#8A4BD9":"#A83E32"):(br.clv?"#2F7D52":"#C98F2C");
    ctx.fillStyle=col;
    rrp(ctx,br.x,br.y,br.w,br.h,5);ctx.fill();
    ctx.fillStyle="#fff";ctx.font="700 12px ui-sans-serif";ctx.textAlign="center";
    if(br.beta)ctx.fillText("β",br.x+br.w/2,br.y+br.h*0.68);
    else if(br.clv)ctx.fillText("CLV",br.x+br.w/2,br.y+br.h*0.68);
  });
  g.drops.forEach(function(d){
    ctx.fillStyle="#2F7D52";
    rrp(ctx,d.x-16,d.y-9,32,18,9);ctx.fill();
    ctx.fillStyle="#fff";ctx.font="700 10px ui-sans-serif";ctx.textAlign="center";
    ctx.fillText("CLV",d.x,d.y+3.5);
  });
  var pw=92,ph=14,py=H-46;
  ctx.fillStyle=g.inhib>0?"#8A4BD9":(dark?"#D68264":"#B04A2F");
  rrp(ctx,g.paddleX-pw/2,py,pw,ph,7);ctx.fill();
  ctx.fillStyle=ink;ctx.font="700 10px ui-sans-serif";ctx.textAlign="center";
  ctx.fillText(g.inhib>0?"lysozyme + clavulanate ("+Math.ceil(g.inhib)+"s)":"lysozyme paddle",g.paddleX,py+ph+14);
  if(g.ball){
    ctx.fillStyle=dark?"#E8EAED":"#1F2933";
    ctx.beginPath();ctx.arc(g.ball.x,g.ball.y,g.ball.r,0,7);ctx.fill();
    ctx.fillStyle=dark?"#1F2228":"#fff";ctx.font="700 7px ui-sans-serif";ctx.textAlign="center";
    ctx.fillText("AMX",g.ball.x,g.ball.y+2.5);
  }
  if(g.confetti)drawConfetti(ctx,g.confetti);
}
function movePaddle(clientX){
  var r=canvas.getBoundingClientRect();
  g.paddleX=Math.max(50,Math.min(W-50,(clientX-r.left)));
}
canvas.addEventListener("pointermove",function(e){if(g&&g.running)movePaddle(e.clientX);});
canvas.addEventListener("pointerdown",function(e){if(g&&g.running)movePaddle(e.clientX);});
canvas.addEventListener("touchmove",function(e){
  if(g&&g.running&&e.touches.length){e.preventDefault();movePaddle(e.touches[0].clientX);}
},{passive:false});
document.addEventListener("keydown",function(e){
  if(!g||!g.running)return;
  if(e.key==="ArrowLeft"){e.preventDefault();g.paddleX=Math.max(50,g.paddleX-32);}
  else if(e.key==="ArrowRight"){e.preventDefault();g.paddleX=Math.min(W-50,g.paddleX+32);}
});
document.addEventListener("visibilitychange",function(){
  if(document.hidden&&g&&g.running){g.running=false;
    var ov=$("#overlay");ov.hidden=false;
    ov.innerHTML='<h2>Paused</h2><button class="btn" id="start-btn">Restart</button>';
    $("#start-btn").addEventListener("click",start);}
});
window.addEventListener("resize",function(){sizeCanvas();draw();});
sizeCanvas();reset();draw();
$("#start-btn").addEventListener("click",start);
""",
  quiz=[
   dict(stem="The bacterial cell wall is made of:",opts=["Peptidoglycan","Bone","DNA"],a=0,
        explain="Peptidoglycan is a sugar-and-peptide mesh unique to bacteria — every gold brick you broke. It holds the cell together against its own pressure."),
   dict(stem="Why can penicillin-class antibiotics kill bacteria without killing your cells?",opts=["They are too small to enter human cells","Human cells have no cell wall, so there is nothing for the drug to target","They only work at night"],a=1,
        explain="Selective toxicity: the drug's target simply doesn't exist in human cells. Targeting what the microbe has and you don't is the core logic of antibiotics."),
   dict(stem="How do penicillin-class (β-lactam) antibiotics kill bacteria?",opts=["They block the enzymes that build the wall; the weakened wall fails and the cell bursts","They freeze the bacteria","They starve them of sugar"],a=0,
        explain="Blocked wall-building + internal osmotic pressure = lysis. You watched the end of that story when the last brick fell."),
   dict(stem="β-lactamase is:",opts=["A vitamin bacteria need","A bacterial enzyme that destroys β-lactam antibiotics — a resistance mechanism","A type of white blood cell"],a=1,
        explain="The β bricks that ate your antibiotic. Bacteria carrying β-lactamase genes survive penicillin — and those genes spread."),
   dict(stem="Clavulanate (the CLV capsule) works by:",opts=["Inhibiting β-lactamase so the antibiotic survives to do its job","Making bacteria larger","Replacing the cell wall"],a=0,
        explain="A real combination strategy: clavulanate ties up β-lactamase, protecting amoxicillin. Together they're co-amoxiclav, one of the world's most prescribed antibiotics."),
   dict(stem="What actually bursts the bacterium once the wall is weakened?",opts=["The antibiotic explodes","The cell's own internal osmotic pressure","Heat"],a=1,
        explain="The wall was the only thing holding back the pressure. Remove it and physics finishes the job — lysis."),
  ],
  simplification="Simplified on purpose: antibiotics don’t bounce off paddles — they block wall-building chemistry as the bacterium grows. The mechanism, the resistance enzyme, and the inhibitor combo are the true parts.")

# ============================================================ ALIGNMENT GRID
GAMES["align"] = dict(
  title="Alignment Grid", tag="Fill the matrix, walk the traceback",
  codep="AG",
  extra_css="""
.algnpad{display:flex;gap:8px;justify-content:center;margin-top:14px;flex-wrap:wrap}
.algnpad button{border:2px solid var(--line);background:var(--surface);color:var(--ink);border-radius:14px;font-size:1rem;font-weight:700;min-width:104px;padding:12px 8px;line-height:1.3}
.algnpad button:active{background:var(--accent-soft);border-color:var(--accent)}
.algnpad button small{display:block;font-weight:400;font-size:.78rem;color:var(--muted)}
.algnpad button:disabled{opacity:.35;cursor:default}
.scorekey{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px;font-size:.88rem;color:var(--muted);justify-content:center}
.scorekey b{color:var(--ink)}
.alnout{font-family:var(--mono);font-size:1.05rem;line-height:1.5;white-space:pre;background:var(--accent-soft);border-radius:10px;padding:10px 14px;display:inline-block;margin:10px 0}
""",
  hud=STD_HUD.replace("{L1}","Cells filled").replace("{V1}","0")
            .replace("{L2}","Score").replace("{V2}","–")
            .replace("{L3}","Slips"),
  stage_inner=flashcard(
    "Needleman–Wunsch · global alignment",
    "You are the algorithm — fill the table, then walk back.",
    "How similar are two protein sequences? Trying every possible alignment explodes exponentially. In 1970 Needleman &amp; Wunsch showed the best <strong>global</strong> (end-to-end) alignment falls out of one table filled cell by cell: each cell holds <strong>the best score aligning the first letters of A with the first letters of B</strong>, and it only needs its three finished neighbors — diagonal (pair the letters, match +2 / mismatch −1), from above or from the left (a gap, −2). The bottom-right cell is the optimal score, and <strong>walking the arrows back</strong> reconstructs the alignment itself. This is dynamic programming — the same idea that powers route planners and spell-checkers.",
    ["Say what one cell of the matrix means, and name the three neighbors it is computed from.",
     "Explain what the diagonal move is (pairing two letters) versus the up/left moves (gaps).",
     "Explain what the traceback recovers, and why Needleman–Wunsch is exact and global — unlike BLASTP's fast local search."],
    ["Each highlighted cell shows its <strong>three candidate scores</strong> — tap the move with the <strong>largest</strong> one. That maximum IS the cell's value.",
     "Fill the whole grid. Your first 2 wrong picks are free practice; after that, 3 slips end the run.",
     "Then <strong>trace back</strong> from the bottom-right: at each cell, tap the move its value actually came from, and watch the alignment assemble."],
    "Scoring here is training wheels: match +2, mismatch −1, gap −2. Real protein alignment scores every pair with the BLOSUM62 matrix.",
    "Start aligning"),
  controls="""<div class="algnpad" id="algnpad">
  <button id="ag-diag" data-m="d" aria-label="Diagonal move">↘ Pair<small id="ag-diag-s">–</small></button>
  <button id="ag-up" data-m="u" aria-label="Gap from above">↓ Gap<small id="ag-up-s">–</small></button>
  <button id="ag-left" data-m="l" aria-label="Gap from left">→ Gap<small id="ag-left-s">–</small></button>
</div>
<div class="scorekey"><span>Match <b>+2</b></span><span>Mismatch <b>−1</b></span><span>Gap <b>−2</b></span><span>Cell = <b>max of the three</b></span></div>
<p class="ctrl-note">Tap the biggest candidate · desktop: 1 = diagonal, 2 = above, 3 = left</p>""",
  js=r"""
var MATCH=2,MIS=-1,GAPP=-2;
var PRESETS=[["ACDE","ACE"],["WYH","WFH"],["MKVL","MKL"],["GAVL","GVL"]];
var canvas=$("#board"),ctx=canvas.getContext("2d");
var W=360,H=300,dpr=1,g=null;
function sub(x,y){return x===y?MATCH:MIS;}
function reset(){
  var p=PRESETS[Math.floor(Math.random()*PRESETS.length)];
  var A=p[0],B=p[1],n=A.length,m=B.length,F=[],D=[];
  for(var i=0;i<=m;i++){F[i]=[];D[i]=[];for(var j=0;j<=n;j++){F[i][j]=null;D[i][j]=null;}}
  F[0][0]=0;D[0][0]="s";
  for(var j2=1;j2<=n;j2++){F[0][j2]=GAPP*j2;D[0][j2]="l";}
  for(var i2=1;i2<=m;i2++){F[i2][0]=GAPP*i2;D[i2][0]="u";}
  g={A:A,B:B,n:n,m:m,F:F,D:D,ci:1,cj:1,phase:"fill",filled:0,total:m*n,
     ti:m,tj:n,alnA:"",alnB:"",alnM:"",hearts:3,practice:2,over:false,confetti:null};
  updHud();updPad();draw();
}
function cands(i,j){
  return {d:g.F[i-1][j-1]+sub(g.A[j-1],g.B[i-1]), u:g.F[i-1][j]+GAPP, l:g.F[i][j-1]+GAPP};
}
function bestOf(c){return Math.max(c.d,c.u,c.l);}
function argBest(c){ if(c.d>=c.u&&c.d>=c.l)return "d"; if(c.u>=c.l)return "u"; return "l"; }
function updHud(){
  $("#s1").textContent=g.filled+" / "+g.total;
  $("#s2").textContent= g.phase==="fill"? "–" : String(g.F[g.m][g.n]);
  var h=g.hearts;$("#hearts").innerHTML="●".repeat(h)+'<span class="off">'+"●".repeat(3-h)+"</span>";
}
function updPad(){
  var bd=$("#ag-diag"),bu=$("#ag-up"),bl=$("#ag-left");
  if(g.phase==="fill"){
    var c=cands(g.ci,g.cj);
    bd.firstChild.textContent="↘ Pair "+g.A[g.cj-1]+"·"+g.B[g.ci-1];
    $("#ag-diag-s").textContent=(c.d>=0?"+":"")+c.d;
    bu.firstChild.textContent="↓ Gap";$("#ag-up-s").textContent=(c.u>=0?"+":"")+c.u;
    bl.firstChild.textContent="→ Gap";$("#ag-left-s").textContent=(c.l>=0?"+":"")+c.l;
    bd.disabled=bu.disabled=bl.disabled=false;
  } else if(g.phase==="trace"){
    bd.firstChild.textContent="↖ From diagonal";$("#ag-diag-s").textContent="pair";
    bu.firstChild.textContent="↑ From above";$("#ag-up-s").textContent="gap";
    bl.firstChild.textContent="← From left";$("#ag-left-s").textContent="gap";
    bd.disabled=(g.ti===0||g.tj===0);bu.disabled=(g.ti===0);bl.disabled=(g.tj===0);
  } else { bd.disabled=bu.disabled=bl.disabled=true; }
}
function slip(why){
  if(g.practice>0){g.practice--;setBanner(why+" — free practice ("+g.practice+" left)","bad");return;}
  g.hearts--;updHud();
  if(g.hearts<=0){g.over=true;g.phase="over";updPad();
    var ov=$("#overlay");ov.hidden=false;
    ov.innerHTML='<p class="eyebrow">Out of slips</p><h2>The matrix defeats guessing — but not arithmetic.</h2><p>Each cell is just the <strong>largest</strong> of three sums: diagonal + pair score, above − 2, left − 2. Work the three numbers, then pick.</p><button class="btn" id="start-btn">Try again</button>';
    $("#start-btn").addEventListener("click",function(){ov.hidden=true;reset();});
  } else setBanner(why,"bad");
}
function pick(mv){
  if(!g||g.over)return;
  if(g.phase==="fill"){
    var c=cands(g.ci,g.cj),best=bestOf(c);
    if(c[mv]===best){
      g.F[g.ci][g.cj]=best;g.D[g.ci][g.cj]=argBest(c);g.filled++;
      setBanner("Cell = "+best+" ✓","good");
      if(g.cj<g.n)g.cj++;else if(g.ci<g.m){g.ci++;g.cj=1;}
      if(g.filled>=g.total){g.phase="trace";g.ti=g.m;g.tj=g.n;
        setBanner("Matrix complete — optimal score "+g.F[g.m][g.n]+". Now trace back from the corner.","good");}
      updHud();updPad();draw();
    } else slip("Not the max — the cell takes the LARGEST of the three ("+best+")");
  } else if(g.phase==="trace"){
    var want=g.D[g.ti][g.tj];
    if(want==="s"){return;}
    if(mv===want){
      if(mv==="d"){g.alnA=g.A[g.tj-1]+g.alnA;g.alnB=g.B[g.ti-1]+g.alnB;
        g.alnM=(g.A[g.tj-1]===g.B[g.ti-1]?"|":"·")+g.alnM;g.ti--;g.tj--;}
      else if(mv==="u"){g.alnA="-"+g.alnA;g.alnB=g.B[g.ti-1]+g.alnB;g.alnM=" "+g.alnM;g.ti--;}
      else{g.alnA=g.A[g.tj-1]+g.alnA;g.alnB="-"+g.alnB;g.alnM=" "+g.alnM;g.tj--;}
      if(g.ti===0&&g.tj===0)win();else{setBanner("Step ✓","good");updPad();draw();}
    } else slip("That's not where "+g.F[g.ti][g.tj]+" came from — recompute the three candidates");
  }
}
function win(){
  g.phase="over";g.over=true;updPad();updHud();
  if(!reducedMotion())g.confetti=makeConfetti(W,H),animConfetti();
  var ov=$("#overlay");ov.hidden=false;
  ov.innerHTML='<p class="eyebrow">Optimal alignment found</p><h2>Score '+g.F[g.m][g.n]+' — and you can prove nothing beats it.</h2>'+
    '<div class="alnout">'+g.alnA+"\n"+g.alnM+"\n"+g.alnB+'</div>'+
    '<p>Every alignment of these sequences scores at most <strong>'+g.F[g.m][g.n]+'</strong> — that is what filling the table guarantees, with only '+g.total+' cells of arithmetic instead of exponentially many alignments. <strong>Needleman–Wunsch is exact and global</strong>: end to end. BLASTP plays a different game — fast, heuristic, local — and that is the next module, Seed &amp; Extend.</p>'+
    '<button class="btn" id="start-btn">Align another pair</button>';
  $("#start-btn").addEventListener("click",function(){ov.hidden=true;reset();});
  draw();
}
function animConfetti(){
  if(!g.confetti||!g.confetti.length)return;
  g.confetti=stepConfetti(g.confetti,H,1/60);draw();
  requestAnimationFrame(animConfetti);
}
function sizeCanvas(){
  var w=canvas.parentElement.clientWidth||360;dpr=window.devicePixelRatio||1;
  W=w;H=Math.round(w*0.84);
  canvas.width=Math.round(W*dpr);canvas.height=Math.round(H*dpr);
  canvas.style.width=W+"px";canvas.style.height=H+"px";
  ctx.setTransform(dpr,0,0,dpr,0,0);
}
function draw(){
  if(!g)return;
  var ink=isDark()?"#E8EAED":"#1F2933",muted=isDark()?"#9AA5B1":"#52606D",
      line=isDark()?"rgba(255,255,255,.18)":"rgba(0,0,0,.14)",
      acc=isDark()?"#D68264":"#B04A2F",good=isDark()?"#5FB084":"#2F7D52",
      soft=isDark()?"#3A251D":"#F4E4DD";
  ctx.clearRect(0,0,W,H);
  var cols=g.n+2,rows=g.m+2;
  var cell=Math.min(Math.floor((W-24)/cols),Math.floor((H-24)/rows));
  var ox=Math.round((W-cell*cols)/2)+cell,oy=18+cell;
  ctx.font="700 "+Math.round(cell*0.42)+"px "+getComputedStyle(document.body).fontFamily;
  ctx.textAlign="center";ctx.textBaseline="middle";
  for(var j=0;j<g.n;j++){ctx.fillStyle=acc;ctx.fillText(g.A[j],ox+(j+1)*cell+cell/2,oy-cell/2-2);}
  for(var i=0;i<g.m;i++){ctx.fillStyle=acc;ctx.fillText(g.B[i],ox-cell/2-2,oy+(i+1)*cell+cell/2);}
  for(var ii=0;ii<=g.m;ii++)for(var jj=0;jj<=g.n;jj++){
    var x=ox+jj*cell,y=oy+ii*cell;
    var cur=(g.phase==="fill"&&ii===g.ci&&jj===g.cj);
    var tr=(g.phase!=="fill"&&ii===g.ti&&jj===g.tj);
    ctx.fillStyle= cur? soft : tr? soft : "transparent";
    if(cur||tr){rrp(ctx,x+2,y+2,cell-4,cell-4,6);ctx.fill();}
    ctx.strokeStyle=line;ctx.lineWidth=1;ctx.strokeRect(x,y,cell,cell);
    var v=g.F[ii][jj];
    if(v!==null){
      ctx.fillStyle= (ii===0||jj===0)? muted : ink;
      ctx.font=(cur||tr?"800 ":"600 ")+Math.round(cell*0.38)+"px "+getComputedStyle(document.body).fontFamily;
      ctx.fillText(String(v),x+cell/2,y+cell/2);
      var d=g.D[ii][jj];
      if(d&&d!=="s"&&ii>0&&jj>0){ctx.fillStyle=good;ctx.font="600 "+Math.round(cell*0.26)+"px sans-serif";
        ctx.fillText(d==="d"?"↖":d==="u"?"↑":"←",x+cell*0.22,y+cell*0.24);}
    } else if(cur){ctx.fillStyle=acc;ctx.font="800 "+Math.round(cell*0.38)+"px sans-serif";ctx.fillText("?",x+cell/2,y+cell/2);}
  }
  if(g.confetti)drawConfetti(ctx,g.confetti);
}
window.AGstate=function(){return g?{phase:g.phase,ci:g.ci,cj:g.cj,ti:g.ti,tj:g.tj,filled:g.filled,total:g.total,hearts:g.hearts,over:g.over,F:g.F,D:g.D,A:g.A,B:g.B}:null;};
$("#algnpad").addEventListener("click",function(e){var b=e.target.closest("button");if(b&&!b.disabled)pick(b.getAttribute("data-m"));});
document.addEventListener("keydown",function(e){
  if($("#overlay")&&!$("#overlay").hidden)return;
  if(e.key==="1")pick("d");else if(e.key==="2")pick("u");else if(e.key==="3")pick("l");
});
window.addEventListener("resize",function(){sizeCanvas();draw();});
sizeCanvas();
$("#start-btn").addEventListener("click",function(){$("#overlay").hidden=true;reset();});
""",
  quiz=[
   dict(stem="One cell of the Needleman–Wunsch matrix holds:",opts=["The best score for aligning the first i letters of one sequence with the first j of the other","A random guess refined later","The number of mutations between the species"],a=0,
        explain="That is the dynamic-programming insight: every cell is the answer to a smaller version of the whole problem, built from answers already on the table."),
   dict(stem="A cell's value is computed from:",opts=["The whole rest of the matrix","Its three finished neighbors — diagonal, above, and left — taking the maximum","The longest sequence only"],a=1,
        explain="Diagonal + pair score, above + gap, left + gap — the cell takes the largest. You tapped that maximum for every cell on the board."),
   dict(stem="The diagonal move means:",opts=["Pairing the two letters — a match or a mismatch","Inserting a gap in both sequences","Skipping the rest of the row"],a=0,
        explain="Diagonal consumes one letter from each sequence and scores the pair. Up and left each consume a letter from only one sequence — that's what a gap is."),
   dict(stem="Why fill a table instead of trying every alignment?",opts=["Tables are prettier","Computers cannot try alignments","The table is m × n cells of arithmetic; the number of possible alignments grows exponentially"],a=2,
        explain="Your board was a dozen-odd cells. The alignments it ruled out number in the hundreds — and for real sequences, more than atoms in the universe. Same answer, tiny cost."),
   dict(stem="What does the traceback give you that the final score alone does not?",opts=["The alignment itself — which letters pair and where the gaps go","A faster computer","The protein's 3D structure"],a=0,
        explain="The bottom-right cell proves how good the best alignment is; following the arrows back reconstructs what that alignment actually is. You walked it letter by letter."),
   dict(stem="Needleman–Wunsch versus BLASTP — which is true?",opts=["NW is exact and global (end-to-end); BLASTP is a fast heuristic local search, with Smith–Waterman as the exact local counterpart","NW is the algorithm running inside BLASTP","They are the same algorithm with different names"],a=0,
        explain="Different tools for different jobs: NW guarantees the best end-to-end alignment of two sequences; BLASTP trades that guarantee for the speed to search millions, and Smith–Waterman is the exact version of the local problem. NW is not 'inside' BLASTP."),
  ],
  simplification="Simplified on purpose: training-wheel scoring (match +2, mismatch −1, gap −2) so the arithmetic stays in your head — real protein alignment scores every pair with the BLOSUM62 matrix and uses affine gap penalties, and local alignment (Smith–Waterman) tweaks the recurrence. The table, the max-of-three rule, and the traceback are the true parts.")

# ============================================================ SEED & EXTEND
GAMES["seed"] = dict(
  title="Seed & Extend", tag="How BLASTP searches millions, fast",
  codep="SE",
  extra_css="""
.seedpad{display:flex;gap:8px;justify-content:center;margin-top:14px;flex-wrap:wrap}
.seedpad button{border:2px solid var(--line);background:var(--surface);color:var(--ink);border-radius:14px;font-size:1rem;font-weight:700;min-width:104px;padding:12px 8px;line-height:1.3}
.seedpad button:active{background:var(--accent-soft);border-color:var(--accent)}
.seedpad button small{display:block;font-weight:400;font-size:.78rem;color:var(--muted)}
.seedpad button:disabled{opacity:.35;cursor:default}
.seedpad .skipb{border-color:var(--violet);color:var(--violet)}
.scorekey{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px;font-size:.88rem;color:var(--muted);justify-content:center}
.scorekey b{color:var(--ink)}
.hitrep{font-family:var(--mono);font-size:.95rem;line-height:1.6;white-space:pre;background:var(--accent-soft);border-radius:10px;padding:10px 14px;display:inline-block;margin:10px 0;text-align:left}
""",
  hud=STD_HUD.replace("{L1}","Database sequence").replace("{V1}","1 / 3")
            .replace("{L2}","Hit score").replace("{V2}","0")
            .replace("{L3}","Slips"),
  stage_inner=flashcard(
    "BLASTP · heuristic local search",
    "You are BLAST — too busy for the full matrix.",
    "A protein database holds millions of sequences. Filling a Needleman–Wunsch table against every one would take forever, so <strong>BLASTP cheats, brilliantly</strong>: it chops the query into short <strong>words</strong> (3 amino acids), looks only where a word already matches — a <strong>seed</strong> — and <strong>extends</strong> outward from it while the score stays good. No seed? The sequence is <strong>skipped entirely</strong>, even if a decent alignment was hiding there. That is the trade: guaranteed-best is swapped for fast, and the <strong>E-value</strong> then says how many hits this good you'd expect by pure chance.",
    ["Explain seeding: why matching a short word first makes search fast, and what happens to sequences with no seed.",
     "Explain extension: grow the hit outward while the score holds, and stop when it decays — a local alignment.",
     "Give the E-value idea — expected chance hits at this score — and name Smith–Waterman as the exact local counterpart."],
    ["<strong>Find the seed:</strong> the query's 3-letter word glows gold — tap where those 3 letters sit in the database sequence. No seed anywhere? Hit <strong>Skip</strong>: BLAST wouldn't look twice.",
     "<strong>Extend</strong> the hit left and right: matches +2, mismatches −1. Watch the running score.",
     "<strong>Stop at the peak.</strong> Extending into junk bleeds points — stopping while the score is high is exactly BLAST's drop-off rule. 2 free practice taps, then 3 slips end the run."],
    "Three database sequences, one query. Rack up the best total hit score you can.",
    "Start searching"),
  controls="""<div class="seedpad" id="seedpad">
  <button id="se-left" data-m="left" aria-label="Extend left">⟵ Extend<small id="se-left-s">–</small></button>
  <button id="se-stop" data-m="stop" aria-label="Stop and lock hit">✓ Stop<small>lock the hit</small></button>
  <button id="se-right" data-m="right" aria-label="Extend right">Extend ⟶<small id="se-right-s">–</small></button>
  <button id="se-skip" data-m="skip" class="skipb" aria-label="Skip sequence">Skip<small>no seed here</small></button>
</div>
<div class="scorekey"><span>Match <b>+2</b></span><span>Mismatch <b>−1</b></span><span>Seed = <b>3 exact letters</b></span></div>
<p class="ctrl-note">Tap the database letters to place the seed · then extend / stop · S = skip</p>""",
  js=r"""
var MATCH=2,MIS=-1;
var QSEQ="KMLWAVFSD",SEED_AT=2,SEEDW=QSEQ.substr(SEED_AT,3);
var ROUNDS=[
 {db:"GPLWAVFNT",seedAt:2,hint:"a strong hit — extend while it holds"},
 {db:"DNLWATRGE",seedAt:2,hint:"a weak hit — know when to stop"},
 {db:"QRSTGENDH",seedAt:-1,hint:"no seed — what does BLAST do?"}
];
var canvas=$("#board"),ctx=canvas.getContext("2d");
var W=360,H=300,dpr=1,g=null;
function reset(){
  g={r:0,phase:"seek",hearts:3,practice:2,total:0,hits:[],over:false,confetti:null};
  loadRound();updHud();updPad();draw();
}
function loadRound(){
  var R=ROUNDS[g.r];
  g.db=R.db;g.seedAt=R.seedAt;g.phase="seek";
  g.L=0;g.Rr=0;g.score=0;g.peak=0;g.locked=false;
  updHud();updPad();draw();
  setBanner("Sequence "+(g.r+1)+" of 3: "+R.hint,"good");
}
function updHud(){
  $("#s1").textContent=(g.r+1)+" / 3";
  $("#s2").textContent=String(g.phase==="seek"?g.total:g.total+g.score);
  var h=g.hearts;$("#hearts").innerHTML="●".repeat(h)+'<span class="off">'+"●".repeat(3-h)+"</span>";
}
function extDelta(side){
  /* next pair when extending: align QSEQ against db anchored at seed */
  var off=g.seedAt-SEED_AT; /* db index = query index + off */
  if(side==="left"){var qi=SEED_AT-g.L-1,di=qi+off;
    if(qi<0||di<0)return null;return {q:QSEQ[qi],d:g.db[di],v:QSEQ[qi]===g.db[di]?MATCH:MIS};}
  var qj=SEED_AT+3+g.Rr,dj=qj+off;
  if(qj>=QSEQ.length||dj>=g.db.length)return null;
  return {q:QSEQ[qj],d:g.db[dj],v:QSEQ[qj]===g.db[dj]?MATCH:MIS};
}
function updPad(){
  var seek=(g.phase==="seek"),ext=(g.phase==="extend");
  $("#se-skip").disabled=!seek;
  var dl=ext?extDelta("left"):null,dr=ext?extDelta("right"):null;
  $("#se-left").disabled=!ext||!dl; $("#se-right").disabled=!ext||!dr; $("#se-stop").disabled=!ext;
  $("#se-left-s").textContent= dl? dl.q+"·"+dl.d+" "+(dl.v>0?"+2":"−1") : "–";
  $("#se-right-s").textContent= dr? dr.q+"·"+dr.d+" "+(dr.v>0?"+2":"−1") : "–";
}
function slip(why){
  if(g.practice>0){g.practice--;setBanner(why+" — free practice ("+g.practice+" left)","bad");return;}
  g.hearts--;updHud();
  if(g.hearts<=0){g.over=true;g.phase="over";updPad();
    var ov=$("#overlay");ov.hidden=false;
    ov.innerHTML='<p class="eyebrow">Out of slips</p><h2>Wasted compute — the one thing BLAST never spends.</h2><p>Scan for the gold word\'s <strong>exact</strong> 3 letters before tapping, and when no seed exists, Skip is the right move — that skip is the whole speed trick.</p><button class="btn" id="start-btn">Search again</button>';
    $("#start-btn").addEventListener("click",function(){ov.hidden=true;reset();});
  } else setBanner(why,"bad");
}
function tapDb(idx){
  if(g.phase!=="seek"||g.over)return;
  if(g.seedAt>=0&&idx===g.seedAt){
    g.phase="extend";g.score=3*MATCH;g.peak=g.score;
    setBanner("Seed found — "+SEEDW+" sits here. Base score +6. Now extend.","good");
    updHud();updPad();draw();
  } else if(g.seedAt<0){
    slip("No seed exists in this sequence — BLAST would Skip it entirely");
  } else slip("Not the seed — the word must match exactly, letter for letter");
}
function act(mv){
  if(!g||g.over)return;
  if(mv==="skip"){
    if(g.phase!=="seek")return;
    if(g.seedAt<0){
      g.hits.push({r:g.r+1,score:0,note:"skipped — no seed"});
      setBanner("Correct — no seed, no alignment. Millions of skips like this are BLAST's speed.","good");
      nextRound();
    } else slip("There IS a seed here — "+SEEDW+" appears in this sequence. Find it");
    return;
  }
  if(g.phase!=="extend")return;
  if(mv==="left"||mv==="right"){
    var d=extDelta(mv);if(!d)return;
    if(mv==="left")g.L++;else g.Rr++;
    g.score+=d.v;if(g.score>g.peak)g.peak=g.score;
    setBanner((d.v>0?"Match ":"Mismatch ")+d.q+"·"+d.d+" → score "+g.score,d.v>0?"good":"bad");
    updHud();updPad();draw();
  } else if(mv==="stop"){
    var left=g.peak-g.score;
    g.hits.push({r:g.r+1,score:g.score,note: left===0? "stopped at the peak ✓" : "overshot by "+left+" — BLAST stops when the score falls"});
    setBanner(left===0? "Locked at the peak — exactly BLAST's drop-off rule.":"Locked "+left+" below your peak — extending into junk bleeds score.","good");
    g.total+=g.score;nextRound();
  }
}
function nextRound(){
  g.r++;
  if(g.r>=ROUNDS.length)win();else loadRound();
}
function win(){
  g.phase="over";g.over=true;updPad();updHud();
  if(!reducedMotion())g.confetti=makeConfetti(W,H),animConfetti();
  var rep=g.hits.map(function(h){return "seq "+h.r+"   score "+String(h.score).padStart(2)+"   "+h.note;}).join("\n");
  var ov=$("#overlay");ov.hidden=false;
  ov.innerHTML='<p class="eyebrow">Search complete</p><h2>Total hit score '+g.total+' — your BLASTP-style report.</h2>'+
    '<div class="hitrep">'+rep+'</div>'+
    '<p>High-scoring hits are the ones worth trusting: the <strong>E-value</strong> turns each score into "how many hits this good would chance alone produce in a database this size" — tiny E-value, real relationship. And remember what you skipped: that unexamined sequence is the price of speed. The exact way to never miss a local hit is <strong>Smith–Waterman</strong> — a Needleman–Wunsch cousin, far too slow for millions of sequences.</p>'+
    '<button class="btn" id="start-btn">Search again</button>';
  $("#start-btn").addEventListener("click",function(){ov.hidden=true;reset();});
  draw();
}
function animConfetti(){
  if(!g.confetti||!g.confetti.length)return;
  g.confetti=stepConfetti(g.confetti,H,1/60);draw();
  requestAnimationFrame(animConfetti);
}
function sizeCanvas(){
  var w=canvas.parentElement.clientWidth||360;dpr=window.devicePixelRatio||1;
  W=w;H=Math.round(w*0.62);
  canvas.width=Math.round(W*dpr);canvas.height=Math.round(H*dpr);
  canvas.style.width=W+"px";canvas.style.height=H+"px";
  ctx.setTransform(dpr,0,0,dpr,0,0);
  g&&computeTiles();
}
var tiles=[];
function computeTiles(){
  tiles=[];
  var n=Math.max(QSEQ.length,g.db.length);
  var cell=Math.min(Math.floor((W-24)/n),46);
  var ox=Math.round((W-cell*g.db.length)/2);
  for(var i=0;i<g.db.length;i++)tiles.push({x:ox+i*cell,w:cell,i:i});
}
function draw(){
  if(!g)return;computeTiles();
  var ink=isDark()?"#E8EAED":"#1F2933",muted=isDark()?"#9AA5B1":"#52606D",
      line=isDark()?"rgba(255,255,255,.18)":"rgba(0,0,0,.14)",
      gold=isDark()?"#E0B458":"#C98F2C",good=isDark()?"#5FB084":"#2F7D52",
      bad=isDark()?"#D98378":"#A83E32",soft=isDark()?"#3A251D":"#F4E4DD";
  ctx.clearRect(0,0,W,H);
  var n=Math.max(QSEQ.length,g.db.length);
  var cell=Math.min(Math.floor((W-24)/n),46);
  var qx=Math.round((W-cell*QSEQ.length)/2),qy=Math.round(H*0.2);
  var dy=Math.round(H*0.62);
  ctx.textAlign="center";ctx.textBaseline="middle";
  ctx.fillStyle=muted;ctx.font="700 11px sans-serif";
  ctx.fillText("QUERY — seed word in gold",W/2,qy-cell*0.75);
  ctx.fillText("DATABASE SEQUENCE "+(g.phase==="seek"?"— tap the first letter of the matching word":""),W/2,dy-cell*0.75);
  for(var i=0;i<QSEQ.length;i++){
    var x=qx+i*cell,inSeed=(i>=SEED_AT&&i<SEED_AT+3);
    var qiLo=SEED_AT-g.L,qiHi=SEED_AT+2+g.Rr;
    var inExt=(g.phase!=="seek")&&(i>=qiLo&&i<=qiHi)&&!inSeed;
    if(inSeed){rrp(ctx,x+1,qy,cell-2,cell,7);ctx.fillStyle=gold;ctx.globalAlpha=.25;ctx.fill();ctx.globalAlpha=1;}
    else if(inExt){rrp(ctx,x+1,qy,cell-2,cell,7);ctx.fillStyle=good;ctx.globalAlpha=.16;ctx.fill();ctx.globalAlpha=1;}
    ctx.fillStyle=inSeed?gold:ink;ctx.font=(inSeed?"800 ":"600 ")+Math.round(cell*0.5)+"px "+getComputedStyle(document.body).fontFamily;
    ctx.fillText(QSEQ[i],x+cell/2,qy+cell/2);
  }
  var off=g.seedAt-SEED_AT;
  for(var k=0;k<g.db.length;k++){
    var t=tiles[k],x2=t.x;
    var seeded=(g.phase!=="seek")&&g.seedAt>=0&&(k>=g.seedAt&&k<g.seedAt+3);
    var kq=k-off;
    var extd=(g.phase!=="seek")&&g.seedAt>=0&&((kq>=SEED_AT-g.L&&kq<SEED_AT)||(kq>SEED_AT+2&&kq<=SEED_AT+2+g.Rr));
    var isM=extd&&QSEQ[kq]===g.db[k];
    ctx.strokeStyle=line;ctx.lineWidth=1;
    rrp(ctx,x2+1,dy,t.w-2,cell,7);
    if(seeded){ctx.fillStyle=gold;ctx.globalAlpha=.25;ctx.fill();ctx.globalAlpha=1;}
    else if(extd){ctx.fillStyle=isM?good:bad;ctx.globalAlpha=.18;ctx.fill();ctx.globalAlpha=1;}
    else{ctx.fillStyle=soft;ctx.globalAlpha=.0;ctx.fill();ctx.globalAlpha=1;}
    ctx.stroke();
    ctx.fillStyle= seeded? gold : extd? (isM?good:bad) : ink;
    ctx.font=(seeded?"800 ":"600 ")+Math.round(cell*0.5)+"px "+getComputedStyle(document.body).fontFamily;
    ctx.fillText(g.db[k],x2+t.w/2,dy+cell/2);
  }
  if(g.phase==="extend"){
    ctx.fillStyle=muted;ctx.font="700 12px sans-serif";
    ctx.fillText("hit score "+g.score+" · peak "+g.peak,W/2,dy+cell+18);
  }
  if(g.confetti)drawConfetti(ctx,g.confetti);
}
window.SEstate=function(){return g?{phase:g.phase,r:g.r,seedAt:g.seedAt,score:g.score,peak:g.peak,total:g.total,hearts:g.hearts,over:g.over,db:g.db,L:g.L,Rr:g.Rr}:null;};
canvas.addEventListener("click",function(e){
  var r=canvas.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;
  var n=Math.max(QSEQ.length,g.db.length);
  var cell=Math.min(Math.floor((W-24)/n),46);
  var dy=Math.round(H*0.62);
  if(y<dy-10||y>dy+cell+10)return;
  for(var i=0;i<tiles.length;i++)if(x>=tiles[i].x&&x<tiles[i].x+tiles[i].w){tapDb(tiles[i].i);break;}
});
$("#seedpad").addEventListener("click",function(e){var b=e.target.closest("button");if(b&&!b.disabled)act(b.getAttribute("data-m"));});
document.addEventListener("keydown",function(e){
  if($("#overlay")&&!$("#overlay").hidden)return;
  if(e.key==="s"||e.key==="S")act("skip");
  else if(e.key==="ArrowLeft")act("left");else if(e.key==="ArrowRight")act("right");
  else if(e.key==="Enter")act("stop");
});
window.addEventListener("resize",function(){sizeCanvas();draw();});
sizeCanvas();
$("#start-btn").addEventListener("click",function(){$("#overlay").hidden=true;reset();});
""",
  quiz=[
   dict(stem="BLASTP searches a huge database quickly by:",opts=["Aligning every sequence end-to-end with Needleman–Wunsch","Only running alignment where a short word of the query already matches exactly — a seed","Guessing randomly"],a=1,
        explain="Chop the query into 3-letter words, look only where one lands, extend from there. Everything else is never examined — that is where the speed comes from."),
   dict(stem="A database sequence with no seed word is:",opts=["Skipped entirely — even if a fair alignment was hiding in it","Aligned extra carefully","Reported as the best hit"],a=0,
        explain="The round-3 skip you played. It is the honest cost of the heuristic: speed is bought with the risk of missing a hit no seed pointed to."),
   dict(stem="After finding a seed, BLAST:",opts=["Stops immediately and reports it","Restarts from the beginning of the query","Extends the match outward in both directions while the score stays good"],a=2,
        explain="Extension grows the local alignment around the seed; when the score falls off, BLAST stops — just like locking your hit at the peak."),
   dict(stem="BLASTP alignments are local, meaning:",opts=["They cover the best-matching region, not necessarily either sequence end-to-end","They only work on your own computer","They ignore the middle of sequences"],a=0,
        explain="Local = the best island of similarity. Global (Needleman–Wunsch) forces end-to-end. Proteins often share one domain, not their whole length — local is usually what biology wants."),
   dict(stem="An E-value of a hit tells you:",opts=["The exact evolutionary distance in years","How many hits at least this good you would expect by pure chance in a database this size","The protein's molecular weight"],a=1,
        explain="Small E-value = chance alone almost never produces a score like this = the similarity likely means something. It scales with database size — the same score means less in a bigger haystack."),
   dict(stem="The exact algorithm for the local-alignment problem (what BLAST approximates) is:",opts=["Smith–Waterman","Needleman–Wunsch — it runs inside BLASTP","Bubble sort"],a=0,
        explain="Smith–Waterman is the exact local counterpart — too slow for millions of sequences, which is why BLAST exists. Needleman–Wunsch is exact but GLOBAL, and it is not the algorithm inside BLASTP."),
  ],
  simplification="Simplified on purpose: real BLASTP scores with BLOSUM62 (so near-matching 'neighborhood words' can seed too, not just exact ones), uses two-hit triggers and an X-drop rule for extension, and computes E-values from Karlin–Altschul statistics. Our exact-match seeds, +2/−1 scoring, and stop-at-the-peak rule are the training-wheel versions of those ideas.")

# ============================================================ BUILD
# games.json (repo root) is the single source of truth for the catalog:
# the hub index.html is generated from it, and every manifest entry with
# "generated": true must have a matching GAMES[key] block above.
# Hand-built games ("generated": false, e.g. ribosome-snake) are listed
# in the manifest for the hub only and are never overwritten.

import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = json.load(open(os.path.join(ROOT, "games.json")))
MF = {m["key"]: m for m in MANIFEST["games"]}

missing = [m["key"] for m in MANIFEST["games"] if m.get("generated") and m["key"] not in GAMES]
extra = [k for k in GAMES if k not in MF]
if missing: raise SystemExit("manifest marks these generated but GAMES has no block: %s" % missing)
if extra: raise SystemExit("GAMES has blocks missing from games.json: %s" % extra)

for key, G in GAMES.items():
    m = MF[key]
    html = page(G["title"], G["tag"], G["extra_css"], G["hud"], G["stage_inner"],
                G["controls"], G["js"], G["quiz"], G["codep"], G["simplification"])
    content = html.replace('<meta name="claude:viewport-fit-sides" content="cover">\n','')
    content = content.replace("<title>%s</title>\n" % G["title"], "")
    export = ('<!doctype html>\n<html lang="en" data-theme="light">\n<head>\n<meta charset="utf-8">\n'
      '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
      '<title>%s</title>\n<meta name="description" content="%s">\n'
      '<style>[hidden]{display:none!important}img{max-width:100%%}</style>\n'
      '</head>\n<body>\n' % (G["title"], m["description"]) + content + '\n</body>\n</html>\n')
    d = os.path.join(ROOT, "games", m["slug"])
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(export)
    # syntax check
    mt = re.search(r'<script>\n(.*)\n</script>', html, re.S)
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
        tf.write(mt.group(1)); checkpath = tf.name
    r = subprocess.run(["node","--check",checkpath],capture_output=True,text=True)
    os.unlink(checkpath)
    print(key, "->", m["slug"], "built:", len(export), "bytes; node check:", r.returncode, r.stderr[:200])

# ---------- hub ----------
NUMWORD = {6:"Six",7:"Seven",8:"Eight",9:"Nine",10:"Ten",11:"Eleven",12:"Twelve"}
ngames = len(MANIFEST["games"])
numword = NUMWORD.get(ngames, str(ngames))

CARD_T = """    <div class="card">
      <span class="mod">%s</span>
      <h2>%s</h2>
      <p class="teach">%s</p>
      <span class="meta">%s</span>
      <a class="play" href="games/%s/">Play</a>
    </div>
"""
SECTION_T = """  <h2 class="cat">%s</h2>
  <div class="grid">
%s  </div>
"""
sections = ""
for cat in MANIFEST["categories"]:
    gs = sorted([x for x in MANIFEST["games"] if x["category"] == cat], key=lambda x: x["module"])
    if not gs: continue
    cards = "".join(CARD_T % (gx["mod_label"], gx["title"], gx["teach"], gx["meta"], gx["slug"]) for gx in gs)
    sections += SECTION_T % (cat, cards)

HUB = """<!doctype html>
<html lang="en" data-theme="light"><!-- data-theme="light" pins the arcade to the site's light look; remove it to re-enable auto dark mode -->
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Bio Arcade — AR INBRE</title>
<meta name="description" content="%(numword)s short browser games that each teach one biomedical or bioinformatics concept: flashcard, play, quiz. Built under AR INBRE for Arkansas undergraduates.">
<style>
/* ============================================================
   THEME — swap these tokens to restyle the whole hub.
   Matches kalyanidhusia.github.io/student_training/ by default.
   ============================================================ */
:root{
  --bg:#FAFAF7;
  --ink:#1F2933;
  --muted:#52606D;
  --accent:#B04A2F;
  --accent-soft:#F4E4DD;
  --violet:#8A4BD9;
  --line:rgba(0,0,0,.10);
  --card:#FFFFFF;
  --radius:14px;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#15181C; --ink:#ECEFF2; --muted:#9AA5B1;
    --accent:#D97757; --accent-soft:#3A2A24; --violet:#A97BE8;
    --line:rgba(255,255,255,.14); --card:#1D2126;
  }
}
/* ============================================================ */
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--bg); color:var(--ink);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  -webkit-text-size-adjust:100%%;
}
.wrap{max-width:720px;margin:0 auto;padding:28px 16px 48px}
header h1{font-size:1.7rem;line-height:1.25;margin:0 0 6px}
.eyebrow{font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:700;margin:0 0 10px}
.lede{color:var(--muted);margin:0 0 8px;max-width:58ch}
.loop{display:inline-block;background:var(--accent-soft);color:var(--ink);border-radius:999px;padding:5px 14px;font-size:.85rem;margin:10px 0 10px}
.loop b{color:var(--accent)}
.cat{font-size:.85rem;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);font-weight:700;margin:28px 0 12px;padding-top:20px;border-top:1px solid var(--line)}
.grid{display:grid;grid-template-columns:1fr;gap:14px}
@media (min-width:560px){.grid{grid-template-columns:1fr 1fr}}
.card{
  background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  padding:18px 18px 16px;display:flex;flex-direction:column;gap:8px;min-width:0;
}
.card .mod{font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:700}
.card h2{font-size:1.12rem;margin:0;line-height:1.3}
.card .teach{font-size:.9rem;color:var(--muted);margin:0;flex:1}
.card .teach b{color:var(--ink);font-weight:600}
.meta{font-size:.78rem;color:var(--muted)}
.play{
  display:inline-block;align-self:flex-start;background:var(--accent);color:#fff;
  text-decoration:none;border-radius:999px;padding:9px 22px;font-weight:600;font-size:.92rem;
  touch-action:manipulation;
}
.play:active{transform:translateY(1px)}
.rna{color:var(--violet);font-weight:700}
footer{margin-top:36px;padding-top:18px;border-top:1px solid var(--line);font-size:.8rem;color:var(--muted)}
footer p{margin:4px 0}
a{color:var(--accent)}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <p class="eyebrow">AR INBRE · Student Training</p>
    <h1>Bio Arcade</h1>
    <p class="lede">%(numword)s short games. Each one teaches a single biomedical or bioinformatics concept — the game mechanic <em>is</em> the science, not decoration on top of it.</p>
    <span class="loop"><b>Learn</b> (flashcard) → <b>Play</b> (the mechanic is the concept) → <b>Check</b> (6-question quiz, pass at 5)</span>
  </header>

%(sections)s
  <footer>
    <p><b>Arkansas INBRE</b> — supported by the National Institute of General Medical Sciences of the NIH under grant P20&nbsp;GM103429.</p>
    <p>Educational content, not medical advice. Each game states its simplifications; the mechanics model one concept, not full biological reality.</p>
    <p>Part of the <a href="https://kalyanidhusia.github.io/student_training/">AR INBRE student training</a> materials · v1.1 · catalog generated from games.json</p>
  </footer>
</div>
</body>
</html>
""" % {"numword": numword, "sections": sections}
open(os.path.join(ROOT, "index.html"), "w").write(HUB)
print("hub built:", ngames, "games in", len([c for c in MANIFEST["categories"]]), "categories")
print("done")
