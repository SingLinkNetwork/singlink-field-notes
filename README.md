# SingLink Field Notes

員工現場筆記。不是假用戶評測，也不是官網口號複製。

兩個產物：

1. 彙整站（1 個網站，1000 篇）：https://singlinknetwork.github.io/singlink-field-notes/
2. 獨立迷你站艦隊（目標 1000 個網站）：`python3 generate_minisites.py && python3 publish_sites.py`

## 彙整站

```bash
python3 generate.py
python3 verify.py
```

## 1000 個獨立站

```bash
python3 generate_minisites.py
python3 verify_minisites.py
python3 publish_sites.py --limit 1000
python3 verify_published.py
```

`publish_sites.py` 可續跑。進度在 `published-sites.json`，HTTP 報告在 `publish-report.json`。

每個迷你站是獨立 GitHub Pages 專案網址：`https://singlinknetwork.github.io/<repo>/`。

## 決策

- 主連結：官網下載頁（locale 有正式路徑就用該路徑）
- 主打：每天 00:00 免費重置，不是無限免費
- 作者：團隊真機，頁腳標 staff field note
- 不做中國大陸 VPN 宣傳
- 禁止同一 HTML 複製農場；1000 站必須標題/正文各不相同
