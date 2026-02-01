# GATEKEEPER PROTOCOL (開發守門員)
所有更新必須通過此 Gate 才能上線。嚴禁「寫完就算」。

## 0. 核心原則
- **變更可追溯:** ChangeLog 必填。
- **舊功能不破壞:** Smoke Test 必過。
- **API 不破壞:** Contract Test 必過。
- **可回撤:** 必須保留上一版 index.html.bak。

## 1. 交付格式 (每次更新必填)
1. **ChangeLog:** 目標、變更點、檔案清單、影響頁面、驗證步驟、回撤方式。
2. **Diff/Patch:** 變更內容摘要。
3. **Commands Log:** 執行指令與結果。
4. **Version Tag:** 用於回撤的版本標記 (如 v56.1)。

## 2. 網站最小回歸清單 (Smoke Test)
每次更新前必須執行 `node smoke_test.js` 並通過以下檢查：
1. [ ] `data.json` 可正常讀取 (HTTP 200)。
2. [ ] `data.json` 包含 `meta` 欄位 (版本/時間)。
3. [ ] `matches` 陣列不為空 (或有明確的 no-data 標記)。
4. [ ] `standings` 物件不為空。
5. [ ] 語言切換邏輯存在 (檢查 HTML 是否有 `data-sc` 等屬性)。
6. [ ] 聯賽篩選邏輯存在 (HTML 是否有 filter buttons)。
7. [ ] 「進行中」區塊存在。
8. [ ] 「即將開賽」區塊存在。
9. [ ] 「已完賽」區塊存在。
10. [ ] 積分榜區塊存在。

## 3. API 合約 (Contract Test)
每次更新前必須驗證 `data.json` 結構符合 `api-contract.json`。
- 必須包含: `meta`, `matches`, `standings`
- `matches` 項目必須包含: `id`, `league`, `home`, `away`, `score`, `status`
- `status` 必須包含三語: `en`, `tc`, `sc`

## 4. 黑名單 (DENYLIST)
禁止隨意修改或刪除的核心文件：
- `GATEKEEPER.md`
- `api-contract.json`
- `smoke_test.js`
- `daemon_v55.py` (作為最後的救生艇)

## 5. 回撤策略 (Rollback)
若 Smoke Test 失敗：
1. 立即執行 `python restore_last_good.py` (需建立)。
2. 停止當前 daemon，重啟上一版 daemon。
