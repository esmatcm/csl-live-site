<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>CSL PRO QUANTUM</title>
    <style>
        :root { --bg: #05070a; --surface: #0f1218; --surface-light: #1a1f2e; --primary: #00f2ea; --secondary: #ff0055; --text: #e2e8f0; --text-dim: #94a3b8; --border: rgba(255, 255, 255, 0.1); --glass: rgba(15, 18, 24, 0.7); }
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body { background-color: var(--bg); color: var(--text); font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; padding-bottom: 80px; overflow-x: hidden; }
        .nav { background: var(--glass); backdrop-filter: blur(12px); border-bottom: 1px solid var(--border); padding: 15px 20px; position: sticky; top: 0; z-index: 1000; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 20px; font-weight: 900; letter-spacing: -0.5px; background: linear-gradient(90deg, #fff, var(--primary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .lang-switch { font-size: 12px; background: var(--surface-light); padding: 4px; border-radius: 20px; display: flex; border: 1px solid var(--border); }
        .lang-btn { padding: 4px 10px; border-radius: 16px; cursor: pointer; transition: 0.3s; color: var(--text-dim); }
        .lang-btn.active { background: var(--primary); color: #000; font-weight: bold; }
        .search-container { padding: 15px 20px 0; max-width: 1000px; margin: 0 auto; }
        .search-box { width: 100%; background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 12px; color: var(--text); font-size: 14px; outline: none; }
        .container { max-width: 1000px; margin: 0 auto; padding: 10px 15px; }
        .tabs { display: flex; gap: 15px; margin-bottom: 20px; border-bottom: 1px solid var(--border); padding: 0 15px; }
        .tab-item { padding: 15px 5px; cursor: pointer; color: var(--text-dim); position: relative; }
        .tab-item.active { color: var(--primary); font-weight: bold; }
        .tab-item.active::after { content: ''; position: absolute; bottom: -1px; left: 0; width: 100%; height: 2px; background: var(--primary); }
        .grid { display: grid; grid-template-columns: 1fr; gap: 12px; }
        @media (min-width: 768px) { .grid { grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); } }
        .card { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 16px; position: relative; cursor: pointer; }
        .card.live { border-color: rgba(0, 242, 234, 0.5); background: linear-gradient(145deg, rgba(0, 242, 234, 0.05), var(--surface)); }
        .card-header { display: flex; justify-content: space-between; font-size: 12px; color: var(--text-dim); margin-bottom: 12px; }
        .status-badge { background: var(--surface-light); padding: 2px 8px; border-radius: 6px; color: var(--text); }
        .card.live .status-badge { background: var(--primary); color: #000; font-weight: 800; animation: pulse 2s infinite; }
        .match-row { display: flex; align-items: center; justify-content: space-between; }
        .team { flex: 1; display: flex; align-items: center; gap: 10px; font-size: 15px; font-weight: 600; }
        .team.away { justify-content: flex-end; }
        .team-logo { width: 32px; height: 32px; object-fit: contain; }
        .score { font-size: 24px; font-weight: 700; color: var(--text); font-family: monospace; }
        .card.live .score { color: var(--primary); }
        .loading { text-align: center; padding: 50px; color: var(--text-dim); }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; } }
        
        /* Modal */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); backdrop-filter: blur(8px); z-index: 2000; justify-content: center; align-items: center; }
        .modal.open { display: flex; }
        .modal-card { background: var(--surface); width: 90%; max-width: 450px; border-radius: 24px; border: 1px solid var(--border); padding: 25px; }
        .event-row { display: flex; margin-bottom: 8px; font-size: 14px; }
        .event-time { color: var(--primary); font-weight: bold; width: 40px; }
        .event-icon { margin-right: 8px; }
    </style>
</head>
<body>
<div class="nav">
    <div class="logo">CSL<span style="color:var(--primary)">.AI</span></div>
    <div class="lang-switch">
        <div class="lang-btn" onclick="setLang('sc')" id="btn-sc">简</div>
        <div class="lang-btn" onclick="setLang('tc')" id="btn-tc">繁</div>
        <div class="lang-btn" onclick="setLang('en')" id="btn-en">EN</div>
    </div>
</div>
<div class="search-container"><input type="text" class="search-box" id="searchInput" placeholder="Search..." onkeyup="filterData()"></div>
<div class="container">
    <div class="tabs">
        <div class="tab-item active" onclick="switchView('live')">LIVE</div>
        <div class="tab-item" onclick="switchView('upcoming')">UPCOMING</div>
        <div class="tab-item" onclick="switchView('finished')">HISTORY</div>
    </div>
    <div id="content-area"><div class="loading">CONNECTING...</div></div>
</div>

<!-- MODAL -->
<div class="modal" id="matchModal" onclick="closeModal(event)">
    <div class="modal-card">
        <div style="text-align:center; margin-bottom:20px;">
            <div id="m-league" style="color:#94a3b8; font-size:12px;"></div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:15px;">
                <div style="flex:1"><img id="m-home-logo" width="50"><div id="m-home" style="margin-top:5px; font-weight:bold;"></div></div>
                <div id="m-score" style="font-size:36px; font-weight:900; color:var(--primary)"></div>
                <div style="flex:1"><img id="m-away-logo" width="50"><div id="m-away" style="margin-top:5px; font-weight:bold;"></div></div>
            </div>
            <div id="m-status" style="margin-top:5px; color:var(--text-dim)"></div>
        </div>
        <div style="border-top:1px solid var(--border); padding-top:15px;" id="m-events">
            <!-- Events -->
        </div>
    </div>
</div>

<script>
    let CURRENT_LANG = localStorage.getItem('lang') || 'sc';
    let RAW_DATA = [];
    let CURRENT_VIEW = 'live';

    document.addEventListener('DOMContentLoaded', () => { updateLangUI(); fetchData(); setInterval(fetchData, 30000); });

    async function fetchData() {
        try {
            const res = await fetch('api.json?t=' + new Date().getTime());
            if (!res.ok) throw new Error("Network");
            RAW_DATA = await res.json();
            render();
        } catch (e) { document.getElementById('content-area').innerHTML = '<div class="loading">DATA SYNC ERROR</div>'; }
    }

    function render() {
        const query = document.getElementById('searchInput').value.toLowerCase();
        const container = document.getElementById('content-area');
        container.innerHTML = '';

        const filtered = RAW_DATA.filter(m => {
            let viewMatch = false;
            if (CURRENT_VIEW === 'live' && ['IN_PLAY', 'PAUSED', 'HT'].includes(m.statusRaw)) viewMatch = true;
            else if (CURRENT_VIEW === 'upcoming' && ['TIMED', 'SCHEDULED'].includes(m.statusRaw)) viewMatch = true;
            else if (CURRENT_VIEW === 'finished' && ['FINISHED', 'FT'].includes(m.statusRaw)) viewMatch = true;
            
            if (!viewMatch) return false;
            if (query) {
                // Safe check for lang objects
                const h = m.home[CURRENT_LANG] || m.home;
                const a = m.away[CURRENT_LANG] || m.away;
                return (h+a).toLowerCase().includes(query);
            }
            return true;
        });

        if (filtered.length === 0) { container.innerHTML = '<div class="loading">NO MATCHES FOUND</div>'; return; }

        const grid = document.createElement('div');
        grid.className = 'grid';

        filtered.forEach(m => {
            const card = document.createElement('div');
            card.className = `card ${['IN_PLAY', 'PAUSED', 'HT'].includes(m.statusRaw) ? 'live' : ''}`;
            card.onclick = () => openModal(m);
            
            const homeName = m.home[CURRENT_LANG] || m.home;
            const awayName = m.away[CURRENT_LANG] || m.away;
            const lgName = m.league[CURRENT_LANG] || m.league;
            const statusText = m.status[CURRENT_LANG] || m.status;

            card.innerHTML = `
                <div class="card-header"><span>${lgName}</span><span class="status-badge">${statusText}</span></div>
                <div class="match-row">
                    <div class="team"><img src="${m.homeLogo}" class="team-logo"> ${homeName}</div>
                    <div class="score">${m.score}</div>
                    <div class="team away">${awayName} <img src="${m.awayLogo}" class="team-logo"></div>
                </div>
            `;
            grid.appendChild(card);
        });
        container.appendChild(grid);
    }

    function setLang(lang) { CURRENT_LANG = lang; localStorage.setItem('lang', lang); updateLangUI(); render(); }
    function updateLangUI() { document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active')); document.getElementById(`btn-${CURRENT_LANG}`).classList.add('active'); }
    function switchView(view) { CURRENT_VIEW = view; document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active')); event.target.classList.add('active'); render(); }
    function filterData() { render(); }

    function openModal(m) {
        const modal = document.getElementById('matchModal');
        const homeName = m.home[CURRENT_LANG] || m.home;
        const awayName = m.away[CURRENT_LANG] || m.away;
        
        document.getElementById('m-league').innerText = m.league[CURRENT_LANG] || m.league;
        document.getElementById('m-home').innerText = homeName;
        document.getElementById('m-away').innerText = awayName;
        document.getElementById('m-home-logo').src = m.homeLogo;
        document.getElementById('m-away-logo').src = m.awayLogo;
        document.getElementById('m-score').innerText = m.score;
        document.getElementById('m-status').innerText = `${m.date} ${m.time}`;
        
        const eventsContainer = document.getElementById('m-events');
        eventsContainer.innerHTML = '';
        
        if (m.events && m.events.length > 0) {
            m.events.forEach(ev => {
                const row = document.createElement('div');
                row.className = 'event-row';
                let icon = '⚽';
                if(ev.type === 'card') icon = ev.card === 'red' ? '🟥' : '🟨';
                row.innerHTML = `<span class="event-time">${ev.minute}'</span> <span class="event-icon">${icon}</span> ${ev.text}`;
                eventsContainer.appendChild(row);
            });
        } else {
            eventsContainer.innerHTML = '<div style="text-align:center; color:#666">No events data</div>';
        }
        
        modal.classList.add('open');
    }
    function closeModal(e) { if (e.target.id === 'matchModal') document.getElementById('matchModal').classList.remove('open'); }
</script>
</body>
</html>
