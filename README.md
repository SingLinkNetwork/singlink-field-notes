# SingLink Field Notes

自有 SEO 站。文章是**員工現場筆記**，不是假用戶評測，也不是官網口號複製。

## 一次指令

```bash
python3 generate.py
python3 verify.py
```

會重寫 `site/`：首頁、市場頁、主題頁、1000 篇筆記、`sitemap.xml`、`robots.txt`。

## 免費上線

公開網址：https://singlinknetwork.github.io/singlink-field-notes/

`main` 一推，GitHub Actions 會發佈 `site/`。自訂 `notes.singlinkvpn.com` 需要 Cloudflare DNS，這台機器登不進去。

## 預設決策（grilling 建議案，你可改）

- 主連結：官網下載頁
- 矩陣：這一個自有站，少量不重複現場
- 作者：團隊真機，頁腳標 Field note
- 標題主打：每天免費重置，正文寫當天穩不穩
