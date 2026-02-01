<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>CSL PRO</title>
<style>
:root { --bg:#05070a; --card:#0f172a; --text:#e2e8f0; --accent:#22c55e; --border:#1e293b; --glass:rgba(15,18,24,0.9); }
* { box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
body { background:var(--bg); color:var(--text); font-family:-apple-system, sans-serif; margin:0; padding-bottom:80px; }
.nav { background:var(--glass); border-bottom:1px solid var(--border); padding:15px 20px; position:sticky; top:0; z-index:100; display:flex; justify-content:space-between; align-items:center; backdrop-filter:blur(10px); }
.logo { font-size:20px; font-weight:900; color:#fff; }
.lang-box { font-size:12px; border:1px solid var(--border); border-radius:20px; padding:2px; display:flex; }
.lang-btn { padding:4px 10px; cursor:pointer; color:#94a3b8; border-radius:15px; }
.lang-btn.active { background:var(--accent); color:#000; font-weight:bold; }
.search-box { width:90%; margin:15px auto; display:block; background:var(--card); border:1px solid var(--border); padding:10px; color:#fff; border-radius:8px; outline:none; }
.tabs { display:flex; justify-content:center; gap:20px; margin:15px 0; border-bottom:1px solid var(--border); }
.tab { padding:10px; cursor:pointer; color:#94a3b8; font-weight:bold; border-bottom:2px solid transparent; }
.tab.active { color:var(--accent); border-color:var(--accent); }
.grid { display:grid; gap:10px; padding:15px; max-width:800px; margin:0 auto; }
.card { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:15px; cursor:pointer; }
.card.live { border-color:var(--accent); }
.header { display:flex; justify-content:space-between; font-size:12px; color:#94a3b8; margin-bottom:10px; }
.badge { background:#1e293b; padding:2px 6px; border-radius:4px; color:#fff; }
.badge.live { background:var(--accent); color:#000; font-weight:bold; }
.match { display:flex; justify-content:space-between; align-items:center; }
.team { display:flex; align-items:center; gap:8px; width:40%; font-size:14px; font-weight:500; }
.team.away { justify-content:flex-end; }
.team img { width:24px; height:24px; }
.score { font-size:20px; font-weight:bold; color:var(--accent); }
.loading { text-align:center; padding:50px; color:#666; }

/* Standings */
.std-tabs { overflow-x:auto; white-space:nowrap; padding:10px; text-align:center; }
.std-btn { background:transparent; border:1px solid var(--border); color:#94a3b8; padding:5px 12px; border-radius:15px; margin:0 4px; cursor:pointer; }
.std-btn.active { background:var(--accent); color:#000; border-color:var(--accent); font-weight:bold; }
table { width:100%; border-collapse:collapse; font-size:13px; text-align:center; }
th { color:#94a3b8; padding:10px; border-bottom:1px solid var(--border); }
td { padding:10px; border-bottom:1px solid var(--border); }
.team-cell { text-align:left; display:flex; align-items:center; gap:5px; }

/* Modal */
.modal { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:200; justify-content:center; align-items:center; }
.modal.open { display:flex; }
.modal-box { background:var(--card); width:90%; max-width:400px; padding:20px; border-radius:12px; border:1px solid var(--accent); max-height:80vh; overflow-y:auto; }
.ev-row { display:flex; margin-bottom:8px; font-size:13px; }
.ev-time { color:var(--accent); width:30px; font-weight:bold; }
</style>
</head>
<body>
<div class="nav">
    <div class="logo">CSL<span style="color:var(--accent)">PRO</span></div>
    <div class="lang-box">
        <div class="lang-btn" onclick="setLang('sc')" id="btn-sc">简</div>
        <div class="lang-btn" onclick="setLang('tc')" id="btn-tc">繁</div>
        <div class="lang-btn" onclick="setLang('en')" id="btn-en">EN</div>
    </div>
</div>

<input type="text" class="search-box" id="search" placeholder="Search..." onkeyup="render()">

<div class="tabs">
    <div class="tab active" onclick="setTab('live')" id="t-live">LIVE</div>
    <div class="tab" onclick="setTab('up')" id="t-up">UPCOMING</div>
    <div class="tab" onclick="setTab('std')" id="t-std">STANDINGS</div>
</div>

<div id="app"></div>

<div id="modal" class="modal" onclick="if(event.target===this)this.classList.remove('open')">
    <div class="modal-box" id="m-box"></div>
</div>

<script>
let DATA = { matches: [], standings: {} };
let LANG = localStorage.getItem('lang') || 'sc';
let TAB = 'live';

const TXT = {
    sc: { live:'正在进行', up:'即将开赛', std:'积分榜', no:'暂无数据', search:'搜索...' },
    tc: { live:'正在進行', up:'即將開賽', std:'積分榜', no:'暫無數據', search:'搜尋...' },
    en: { live:'LIVE', up:'UPCOMING', std:'STANDINGS', no:'NO DATA', search:'Search...' }
};

async function init() {
    updateUI();
    try {
        let res = await fetch('data.json?t=' + Date.now());
        let json = await res.json();
        DATA = json;
        render();
    } catch(e) { document.getElementById('app').innerHTML = '<div class="loading">DATA ERROR</div>'; }
}

function updateUI() {
    ['sc','tc','en'].forEach(l => document.getElementById('btn-'+l).className = `lang-btn ${l===LANG?'active':''}`);
    document.getElementById('t-live').innerText = TXT[LANG].live;
    document.getElementById('t-up').innerText = TXT[LANG].up;
    document.getElementById('t-std').innerText = TXT[LANG].std;
    document.getElementById('search').placeholder = TXT[LANG].search;
}

function setLang(l) { LANG=l; localStorage.setItem('lang',l); updateUI(); render(); }
function setTab(t) { TAB=t; document.querySelectorAll('.tab').forEach(e => e.className = `tab ${e.id==='t-'+t?'active':''}`); render(); }

function render() {
    const app = document.getElementById('app');
    app.innerHTML = '';
    
    if (TAB === 'std') {
        if(!DATA.standings || Object.keys(DATA.standings).length===0) { app.innerHTML='<div class="loading">Loading...</div>'; return; }
        
        let tabs = '<div class="std-tabs">';
        let content = '';
        let first = true;
        
        for(let code in DATA.standings) {
            let active = first ? 'active' : '';
            let display = first ? 'block' : 'none';
            tabs += `<button class="std-btn ${active}" onclick="openStd('${code}', this)">${code}</button>`;
            
            let rows = '';
            DATA.standings[code].forEach(r => {
                let name = r.team[LANG] || r.team.en;
                rows += `<tr><td>${r.pos}</td><td class="team-cell"><img src="${r.crest}" width="20"> ${name}</td><td>${r.played}</td><td><b>${r.points}</b></td></tr>`;
            });
            content += `<div id="st-${code}" style="display:${display}"><table><thead><tr><th>#</th><th>TEAM</th><th>PL</th><th>PTS</th></tr></thead><tbody>${rows}</tbody></table></div>`;
            first = false;
        }
        app.innerHTML = tabs + '</div>' + content;
        return;
    }

    const q = document.getElementById('search').value.toLowerCase();
    let list = DATA.matches.filter(m => {
        let ok = false;
        if(TAB==='live' && ['IN_PLAY','PAUSED','HT'].includes(m.statusRaw)) ok=true;
        if(TAB==='up' && ['TIMED','SCHEDULED'].includes(m.statusRaw)) ok=true;
        if(!ok) return false;
        if(q) {
            let n = (m.home[LANG]||m.home.en) + (m.away[LANG]||m.away.en);
            return n.toLowerCase().includes(q);
        }
        return true;
    });

    // Fallback
    if(TAB==='live' && list.length===0 && !q) {
        app.innerHTML += `<div style="text-align:center;color:#666;font-size:12px;margin-bottom:10px">${TXT[LANG].no} - History</div>`;
        list = DATA.matches.filter(m => ['FINISHED','FT'].includes(m.statusRaw)).slice(0, 10);
    }
    
    // Sort
    list.sort((a,b) => (a.priority||99) - (b.priority||99));

    if(list.length===0) { app.innerHTML = `<div class="loading">${TXT[LANG].no}</div>`; return; }

    let grid = document.createElement('div');
    grid.className = 'grid';
    
    list.forEach(m => {
        let card = document.createElement('div');
        card.className = `card ${['IN_PLAY','PAUSED'].includes(m.statusRaw)?'live':''}`;
        card.onclick = () => showModal(m);
        
        let h = m.home[LANG] || m.home.en;
        let a = m.away[LANG] || m.away.en;
        let lg = m.league[LANG] || m.league.en;
        let st = m.status[LANG] || m.status.en;
        
        card.innerHTML = `<div class="header"><span>${lg}</span><span class="badge ${card.className.includes('live')?'live':''}">${st}</span></div>
        <div class="match"><div class="team"><img src="${m.homeLogo}"> ${h}</div><div class="score">${m.score}</div><div class="team away">${a} <img src="${m.awayLogo}"></div></div>`;
        grid.appendChild(card);
    });
    app.appendChild(grid);
}

window.openStd = function(code, btn) {
    document.querySelectorAll('.std-btn').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('[id^="st-"]').forEach(d=>d.style.display='none');
    document.getElementById('st-'+code).style.display='block';
}

function showModal(m) {
    const box = document.getElementById('m-box');
    let h = m.home[LANG] || m.home.en;
    let a = m.away[LANG] || m.away.en;
    let st = m.status[LANG] || m.status.en;
    
    let html = `<div style="text-align:center;border-bottom:1px solid #333;padding-bottom:15px;margin-bottom:15px">
    <div style="font-size:12px;color:#999">${m.date} ${m.time}</div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px">
        <div style="flex:1"><img src="${m.homeLogo}" width="40"><br>${h}</div>
        <div style="font-size:30px;color:#22c55e;font-weight:bold">${m.score}</div>
        <div style="flex:1"><img src="${m.awayLogo}" width="40"><br>${a}</div>
    </div>
    <div style="margin-top:5px;color:#999">${st}</div></div>`;
    
    if(m.events) {
        m.events.forEach(ev => {
            let txt = ev.text[LANG] || ev.text.en;
            html += `<div class="ev-row"><span class="ev-time">${ev.minute}'</span> ${txt}</div>`;
        });
    }
    
    if(m.streams && m.streams.length>0) {
        html += '<div style="margin-top:15px;border-top:1px solid #333;padding-top:10px;font-weight:bold;font-size:12px;color:#22c55e">LIVE STREAMS</div>';
        m.streams.forEach(s => {
             let sn = s.name[LANG] || s.name.en;
             html += `<a href="${s.url}" target="_blank" style="display:block;padding:8px;background:#1e293b;color:#fff;text-decoration:none;margin-top:5px;border-radius:5px">📺 ${sn}</a>`;
        });
    }

    box.innerHTML = html;
    document.getElementById('modal').classList.add('open');
}

init();
</script>
</body>
</html>
