const fs = require('fs');
const https = require('https');

// CONFIG
const DATA_URL = "https://hsapi.xyz/data.json";
const CONTRACT = require('./api-contract.json');

console.log("🚀 STARTING SMOKE TEST & CONTRACT CHECK...");

function fail(msg) {
    console.error("❌ FAIL: " + msg);
    process.exit(1);
}

function pass(msg) {
    console.log("✅ PASS: " + msg);
}

https.get(DATA_URL, (res) => {
    if (res.statusCode !== 200) fail(`HTTP ${res.statusCode}`);
    
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
        try {
            const json = JSON.parse(data);
            pass("JSON Valid");

            // 1. Contract Check (Root)
            CONTRACT.required_root.forEach(f => {
                if (!json[f]) fail(`Missing root field: ${f}`);
            });
            pass("Contract: Root Fields OK");

            // 2. Meta Check
            if (!json.meta.daemon) fail("Meta: Missing daemon version");
            pass(`Meta: Daemon ${json.meta.daemon}`);

            // 3. Matches Check
            if (!Array.isArray(json.matches)) fail("Matches is not array");
            if (json.matches.length === 0) console.warn("⚠️ WARNING: Matches array is empty (Check if off-season)");
            else {
                const m = json.matches[0];
                CONTRACT.match_fields.forEach(f => {
                    if (m[f] === undefined) fail(`Match missing field: ${f}`);
                });
                // I18N Check
                ['league', 'home', 'away', 'status'].forEach(k => {
                    CONTRACT.i18n_fields.forEach(lang => {
                        if (!m[k][lang]) fail(`Match ${k} missing lang: ${lang}`);
                    });
                });
                pass(`Contract: Match Fields OK (${json.matches.length} items)`);
            }

            // 4. Standings Check
            const codes = Object.keys(json.standings);
            if (codes.length === 0) fail("Standings empty");
            const row = json.standings[codes[0]][0];
            CONTRACT.standings_fields.forEach(f => {
                if (row[f] === undefined) fail(`Standing missing field: ${f}`);
            });
            pass("Contract: Standings OK");

            console.log("\n🎉 ALL CHECKS PASSED. READY FOR DEPLOY.");

        } catch (e) {
            fail("JSON Parse Error: " + e.message);
        }
    });
}).on('error', (e) => {
    fail("Network Error: " + e.message);
});
