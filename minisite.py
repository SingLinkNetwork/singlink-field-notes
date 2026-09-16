#!/usr/bin/env python3
"""Render one standalone, crawlable mini-site from a field-note index."""

from __future__ import annotations

import hashlib
import html
import json

from generate import (
    DOWNLOAD,
    WRITERS,
    article_en,
    download_url,
    facts,
    intent_kw,
)

ORG = "SingLinkNetwork"
PAGES_HOST = "https://singlinknetwork.github.io"
REPO_PREFIXES = (
    "desk",
    "note",
    "log",
    "field",
    "meter",
    "lobby",
    "campus",
    "cafe",
    "shift",
    "wifi",
)
THEMES = (
    {"paper": "#f6f4ee", "ink": "#1c1c1a", "muted": "#5a5c57", "card": "#fff", "line": "#d9d4c8", "link": "#1f4d3a"},
    {"paper": "#f4f7f8", "ink": "#1b2430", "muted": "#5b6570", "card": "#fff", "line": "#d3dce0", "link": "#1a5276"},
    {"paper": "#f7f3ef", "ink": "#2a2118", "muted": "#6a5e52", "card": "#fffaf5", "line": "#e0d4c6", "link": "#6b3e1a"},
    {"paper": "#f3f5f1", "ink": "#1c2418", "muted": "#586054", "card": "#fff", "line": "#d5d8ce", "link": "#2d5a27"},
    {"paper": "#f6f2f4", "ink": "#241c20", "muted": "#655860", "card": "#fff", "line": "#ddd2d7", "link": "#5a2d44"},
    {"paper": "#f2f4f7", "ink": "#1a1f2a", "muted": "#5a6170", "card": "#fff", "line": "#d0d5de", "link": "#2c3e6b"},
    {"paper": "#f8f6f1", "ink": "#222018", "muted": "#646056", "card": "#fffdf8", "line": "#ddd6c6", "link": "#4a5c2a"},
    {"paper": "#f5f5f3", "ink": "#202020", "muted": "#5c5c5c", "card": "#fff", "line": "#d8d8d4", "link": "#3d4a44"},
)
FONTS = (
    'Georgia,"Songti TC","Noto Serif TC",serif',
    'Georgia,"Iowan Old Style",serif',
    '"Palatino Linotype",Palatino,"Songti TC",serif',
    'Georgia,"Noto Serif",serif',
)
CTA_LABEL = {
    "en": "Official {store} download",
    "zh-Hant": "官方 {store} 下載",
    "zh-Hans": "官方 {store} 下载",
    "ja": "公式 {store} ダウンロード",
    "ko": "공식 {store} 다운로드",
    "es": "Descarga oficial {store}",
    "pt": "Download oficial {store}",
    "de": "Offizieller {store}-Download",
    "fr": "Téléchargement officiel {store}",
    "it": "Download ufficiale {store}",
    "nl": "Officiële {store}-download",
    "pl": "Oficjalny download {store}",
    "tr": "Resmi {store} indirme",
    "id": "Unduhan resmi {store}",
    "th": "ดาวน์โหลด {store} ทางการ",
    "vi": "Tải chính thức {store}",
    "ar": "التنزيل الرسمي لـ {store}",
    "hi": "आधिकारिक {store} डाउनलोड",
    "ms": "Muat turun rasmi {store}",
    "uk": "Офіційне завантаження {store}",
    "ru": "Официальная загрузка {store}",
    "he": "הורדה רשמית של {store}",
    "fil": "Opisyal na {store} download",
}
FOOTERS = {
    "en": (
        "Staff field note for SingLinkVPN. Not an independent review and not homepage copy.",
        "Written by the team after using the app. Not a stranger review. Downloads stay on the official site.",
        "Internal desk note. We do not sell plans here. The only outbound install link is the official store page.",
        "A single field note, not a slogan page. Daily free traffic resets at 00:00; that is not unlimited free.",
    ),
    "zh-Hant": (
        "SingLinkVPN 員工現場筆記。不是獨立評測，也不是官網口號。",
        "團隊真機寫下的單篇筆記。這裡不賣套餐，安裝只連官方下載頁。",
        "現場備忘，不是路人開箱。免費檔是每天 0 點重置，不是無限免費。",
        "一篇現場，一個網址。下載請走官方對應系統頁。",
    ),
    "zh-Hans": (
        "SingLinkVPN 员工现场笔记。不是独立评测，也不是官网口号。",
        "团队真机写下的单篇笔记。这里不卖套餐，安装只连官方下载页。",
        "现场备忘，不是路人开箱。免费档是每天 0 点重置，不是无限免费。",
        "一篇现场，一个网址。下载请走官方对应系统页。",
    ),
    "ja": (
        "SingLinkVPN の社員による現場メモ。レビューサイトの投稿ではない。",
        "公式ダウンロード以外の導入リンクは置かない。料金プランは扱わない。",
        "無料枠は毎日 0:00 に戻る。無制限無料とは書いていない。",
        "スローガンは貼らない。公式ストアのページだけを出す。",
    ),
    "ko": (
        "SingLinkVPN 직원 현장 메모. 제3자 리뷰가 아니다.",
        "요금제를 팔지 않는다. 설치 링크는 공식 다운로드만.",
        "무료 용량은 매일 00:00에 리셋된다. 무제한 무료가 아니다.",
        "슬로건 페이지가 아니다. 공식 스토어만 남긴다.",
    ),
    "es": (
        "Nota de campo del equipo de SingLinkVPN. No es una reseña independiente.",
        "Aquí no vendemos planes. Solo el enlace oficial de descarga.",
        "Los datos gratis se reinician a las 00:00. No es gratis ilimitado.",
        "Una sola nota de escritorio. Sin eslóganes de la home.",
    ),
    "pt": (
        "Nota de campo da equipa SingLinkVPN. Não é review independente.",
        "Não vendemos planos aqui. Só o download oficial.",
        "A cota grátis reinicia às 00:00. Não é grátis ilimitado.",
        "Uma nota só. Sem slogans da homepage.",
    ),
    "de": (
        "Interne Feldnotiz zu SingLinkVPN. Keine unabhängige Bewertung.",
        "Keine Tarife auf dieser Seite. Nur der offizielle Download.",
        "Das Tageskontingent setzt um 00:00 zurück. Das ist nicht unlimited free.",
        "Eine Notiz, keine Slogan-Seite.",
    ),
    "fr": (
        "Note de terrain de l'équipe SingLinkVPN. Pas un avis indépendant.",
        "Pas de vente de forfaits ici. Uniquement le téléchargement officiel.",
        "Le quota gratuit revient à 00:00. Ce n'est pas un illimité gratuit.",
        "Une seule note. Pas de slogan de la page d'accueil.",
    ),
    "it": (
        "Nota di campo del team SingLinkVPN. Non è una recensione indipendente.",
        "Qui non vendiamo piani. Solo il download ufficiale.",
        "I dati gratis si azzerano alle 00:00. Non è gratis illimitato.",
        "Una sola nota. Niente slogan della home.",
    ),
    "nl": (
        "Veldnotitie van het SingLinkVPN-team. Geen onafhankelijke review.",
        "Geen abonnementen hier. Alleen de officiële download.",
        "De vrije data reset om 00:00. Dat is niet onbeperkt gratis.",
        "Eén notitie. Geen homepage-slogan.",
    ),
    "pl": (
        "Notatka zespołu SingLinkVPN. To nie niezależna recenzja.",
        "Nie sprzedajemy planów. Tylko oficjalny download.",
        "Darmowy transfer wraca o 00:00. To nie nielimitowane darmowe.",
        "Jedna notatka. Bez sloganu ze strony głównej.",
    ),
    "tr": (
        "SingLinkVPN ekip saha notu. Bağımsız inceleme değil.",
        "Burada tarife satmıyoruz. Yalnız resmi indirme.",
        "Ücretsiz kota 00:00'da sıfırlanır. Sınırsız ücretsiz değil.",
        "Tek not. Ana sayfa sloganı yok.",
    ),
    "id": (
        "Catatan lapangan tim SingLinkVPN. Bukan ulasan independen.",
        "Kami tidak menjual paket di sini. Hanya unduhan resmi.",
        "Kuota gratis kembali pukul 00:00. Bukan gratis tanpa batas.",
        "Satu catatan. Tanpa slogan beranda.",
    ),
    "th": (
        "บันทึกภาคสนามของทีม SingLinkVPN ไม่ใช่รีวิวอิสระ",
        "ที่นี่ไม่ขายแพ็กเกจ มีแต่ลิงก์ดาวน์โหลดทางการ",
        "โควตาฟรีรีเซ็ต 00:00 ไม่ใช่ฟรีไม่จำกัด",
        "บันทึกเดียว ไม่มีสโลแกนหน้าโฮม",
    ),
    "vi": (
        "Ghi chép hiện trường của team SingLinkVPN. Không phải review độc lập.",
        "Không bán gói ở đây. Chỉ tải chính thức.",
        "Data miễn phí reset lúc 00:00. Không phải miễn phí không giới hạn.",
        "Một ghi chép. Không slogan trang chủ.",
    ),
    "ar": (
        "ملاحظة ميدانية لفريق SingLinkVPN. ليست مراجعة مستقلة.",
        "لا نبيع خططاً هنا. التحميل الرسمي فقط.",
        "تُعاد البيانات المجانية عند 00:00. ليست مجانية بلا حد.",
        "ملاحظة واحدة. بلا شعار الصفحة الرئيسية.",
    ),
    "hi": (
        "SingLinkVPN टीम की फील्ड नोट। स्वतंत्र रिव्यू नहीं।",
        "यहाँ प्लान नहीं बेचते। सिर्फ़ आधिकारिक डाउनलोड।",
        "मुफ्त डेटा 00:00 पर रीसेट होता है। अनलिमिटेड फ्री नहीं।",
        "एक नोट। होमपेज का नारा नहीं।",
    ),
    "ms": (
        "Nota lapangan pasukan SingLinkVPN. Bukan ulasan bebas.",
        "Kami tidak jual pelan di sini. Muat turun rasmi sahaja.",
        "Data percuma direset 00:00. Bukan percuma tanpa had.",
        "Satu nota. Tiada slogan laman utama.",
    ),
    "uk": (
        "Польова нотатка команди SingLinkVPN. Це не незалежний огляд.",
        "Плани тут не продаємо. Лише офіційне завантаження.",
        "Безкоштовний трафік скидається о 00:00. Це не безлімітний free.",
        "Одна нотатка. Без слогана з головної.",
    ),
    "ru": (
        "Полевая заметка команды SingLinkVPN. Это не независимый обзор.",
        "Тарифы здесь не продаём. Только официальная загрузка.",
        "Бесплатный трафик сбрасывается в 00:00. Это не безлимитный free.",
        "Одна заметка. Без слогана с главной.",
    ),
    "he": (
        "פתק שטח של צוות SingLinkVPN. זו לא סקירה עצמאית.",
        "אין מכירת חבילות כאן. רק הורדה רשמית.",
        "הנפח החינמי מתאפס ב־00:00. זה לא חינם בלי הגבלה.",
        "פתק אחד. בלי סלוגן מדף הבית.",
    ),
    "fil": (
        "Field note ng team ng SingLinkVPN. Hindi ito independent review.",
        "Hindi kami nagbebenta ng plan dito. Opisyal na download lang.",
        "Nagre-reset ang free data sa 00:00. Hindi unlimited free.",
        "Isang tala. Walang slogan mula sa homepage.",
    ),
}


def _pick(seq, n, salt: str):
    h = int(hashlib.sha1(f"{n}:{salt}".encode()).hexdigest(), 16)
    return seq[h % len(seq)]


def repo_name(n: int) -> str:
    f = facts(n)
    prefix = REPO_PREFIXES[n % len(REPO_PREFIXES)]
    return f"{prefix}-{f['loc']['id']}-{f['intent']['id']}-{n + 1:04d}"


def live_url(n: int) -> str:
    return f"{PAGES_HOST}/{repo_name(n)}/"


def site_name(f) -> str:
    lang = f["loc"]["lang"]
    city, place, kw = f["city"], f["place"], f["intent"]["kw"]
    mode = f["n"] % 4
    if lang == "zh-Hant":
        choices = (f"{city}現場筆記", f"{place}備忘", f"{city} · {kw}", f"{city}單篇現場")
    elif lang == "zh-Hans":
        choices = (f"{city}现场笔记", f"{place}备忘", f"{city} · {kw}", f"{city}单篇现场")
    elif lang == "ja":
        choices = (f"{city}の現場メモ", f"{place}の記録", f"{city} / {kw}", f"{city}デスクノート")
    elif lang == "ko":
        choices = (f"{city} 현장 메모", f"{place} 기록", f"{city} · {kw}", f"{city} 데스크 노트")
    elif lang == "es":
        choices = (f"Nota en {city}", f"Desde {place}", f"{city} · {kw}", f"Diario de {city}")
    elif lang == "pt":
        choices = (f"Nota em {city}", f"Desde {place}", f"{city} · {kw}", f"Caderno de {city}")
    elif lang == "de":
        choices = (f"Notiz aus {city}", f"Aus {place}", f"{city} · {kw}", f"Feldlog {city}")
    elif lang == "fr":
        choices = (f"Note à {city}", f"Depuis {place}", f"{city} · {kw}", f"Carnet {city}")
    elif lang == "it":
        choices = (f"Nota a {city}", f"Da {place}", f"{city} · {kw}", f"Diario {city}")
    elif lang == "nl":
        choices = (f"Notitie in {city}", f"Vanaf {place}", f"{city} · {kw}", f"Log {city}")
    elif lang == "pl":
        choices = (f"Notatka z {city}", f"Z {place}", f"{city} · {kw}", f"Dziennik {city}")
    elif lang == "tr":
        choices = (f"{city} notu", f"{place} kaydı", f"{city} · {kw}", f"{city} saha defteri")
    elif lang == "id":
        choices = (f"Catatan {city}", f"Dari {place}", f"{city} · {kw}", f"Buku {city}")
    elif lang == "th":
        choices = (f"บันทึก {city}", f"จาก {place}", f"{city} · {kw}", f"สมุด {city}")
    elif lang == "vi":
        choices = (f"Ghi chép {city}", f"Từ {place}", f"{city} · {kw}", f"Sổ {city}")
    elif lang == "ar":
        choices = (f"ملاحظة {city}", f"من {place}", f"{city} · {kw}", f"دفتر {city}")
    elif lang == "hi":
        choices = (f"{city} नोट", f"{place} से", f"{city} · {kw}", f"{city} डेस्क लॉग")
    elif lang == "ms":
        choices = (f"Nota {city}", f"Dari {place}", f"{city} · {kw}", f"Log {city}")
    elif lang == "uk":
        choices = (f"Нотатка з {city}", f"З {place}", f"{city} · {kw}", f"Щоденник {city}")
    elif lang == "ru":
        choices = (f"Заметка из {city}", f"Из {place}", f"{city} · {kw}", f"Журнал {city}")
    elif lang == "he":
        choices = (f"פתק מ{city}", f"מ{place}", f"{city} · {kw}", f"יומן {city}")
    elif lang == "fil":
        choices = (f"Tala sa {city}", f"Mula sa {place}", f"{city} · {kw}", f"Kwaden {city}")
    else:
        choices = (f"{city} desk note", f"Notes from {place}", f"{city} · {kw}", f"Field log, {city}")
    return choices[mode]


def _css(theme, font: str, layout: str) -> str:
    width = {"a": "720px", "b": "800px", "c": "640px"}[layout]
    return f"""
:root {{ --ink:{theme['ink']}; --muted:{theme['muted']}; --paper:{theme['paper']}; --card:{theme['card']}; --line:{theme['line']}; --link:{theme['link']}; }}
*{{box-sizing:border-box}} html,body{{margin:0;padding:0}}
body{{font-family:{font};background:var(--paper);color:var(--ink);line-height:1.65}}
a{{color:var(--link)}} header,main,footer{{max-width:{width};margin:0 auto;padding:0 22px}}
header{{padding-top:32px;padding-bottom:14px;border-bottom:1px solid var(--line);margin-bottom:28px}}
.site-name{{font-weight:650;letter-spacing:.01em}}
h1{{font-size:1.85rem;line-height:1.28;margin:0 0 12px}}
p,li{{font-size:1.05rem}}
.muted{{color:var(--muted);font-size:.95rem}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:18px 0}}
.chips{{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 16px}}
.chip{{border:1px solid var(--line);border-radius:999px;padding:2px 10px;font-size:.85rem;color:var(--muted)}}
.cta{{display:inline-block;margin:8px 0 4px;padding:10px 16px;border:1px solid var(--link);border-radius:10px;text-decoration:none;font-weight:650}}
footer{{border-top:1px solid var(--line);margin-top:48px;padding:24px 22px 48px;color:var(--muted);font-size:.92rem}}
html[dir=rtl] body{{font-family:"Noto Naskh Arabic","Noto Serif Hebrew",Georgia,serif}}
"""


def _localize_article_urls(paras: list[str], store: str, lang: str) -> list[str]:
    src = DOWNLOAD.get(store, DOWNLOAD["home"])
    dst = download_url(store, lang)
    prefix_src = "https://singlinkvpn.com/en/download/"
    prefix_dst = dst.rsplit("/", 2)[0] + "/"
    return [p.replace(src, dst).replace(prefix_src, prefix_dst) for p in paras]


def render_files(n: int) -> dict:
    f = facts(n)
    lang = f["loc"]["lang"]
    writer = WRITERS.get(lang, article_en)
    title, desc, paras = writer(f)
    store = f["store"]
    cta = download_url(store, lang)
    paras = _localize_article_urls(paras, store, lang)
    theme = THEMES[n % len(THEMES)]
    font = FONTS[n % len(FONTS)]
    layout = ("a", "b", "c")[n % 3]
    name = site_name(f)
    footer = _pick(FOOTERS.get(lang, FOOTERS["en"]), n, "footer")
    label = CTA_LABEL.get(lang, CTA_LABEL["en"]).format(store=store)
    repo = repo_name(n)
    canon = live_url(n)
    home = download_url("home", lang)
    reset_aside = {
        "en": "Daily free traffic resets at 00:00. That is not an unlimited free plan.",
        "zh-Hant": "每日免費流量在 00:00 重置。這不是無限免費。",
        "zh-Hans": "每日免费流量在 00:00 重置。这不是无限免费。",
        "ja": "無料容量は毎日 0:00 にリセットされる。無制限無料ではない。",
        "ko": "무료 용량은 매일 00:00에 리셋된다. 무제한 무료가 아니다.",
        "es": "Los datos gratis se reinician a las 00:00. No es un plan gratis ilimitado.",
        "pt": "A cota grátis reinicia às 00:00. Não é um plano grátis ilimitado.",
        "de": "Das Tageskontingent setzt um 00:00 zurück. Das ist kein Unlimited-Free-Tarif.",
        "fr": "Le quota gratuit revient à 00:00. Ce n'est pas un forfait gratuit illimité.",
        "it": "I dati giornalieri si azzerano alle 00:00. Non è un piano gratis illimitato.",
        "nl": "De dagelijkse vrije data reset om 00:00. Dat is geen onbeperkt gratis plan.",
        "pl": "Dzienny transfer wraca o 00:00. To nie nielimitowany darmowy plan.",
        "tr": "Günlük kota 00:00'da sıfırlanır. Sınırsız ücretsiz plan değil.",
        "id": "Kuota harian kembali pukul 00:00. Bukan paket gratis tanpa batas.",
        "th": "โควตารายวันรีเซ็ต 00:00 ไม่ใช่แพ็กเกจฟรีไม่จำกัด",
        "vi": "Data ngày reset lúc 00:00. Không phải gói miễn phí không giới hạn.",
        "ar": "تُعاد الحصة اليومية عند 00:00. ليست خطة مجانية بلا حد.",
        "hi": "रोज़ का डेटा 00:00 पर रीसेट होता है। यह अनलिमिटेड फ्री प्लान नहीं है।",
        "ms": "Kuota harian direset 00:00. Ini bukan pelan percuma tanpa had.",
        "uk": "Щоденний трафік скидається о 00:00. Це не безлімітний безкоштовний план.",
        "ru": "Дневной трафик сбрасывается в 00:00. Это не безлимитный бесплатный тариф.",
        "he": "הנפח היומי מתאפס ב־00:00. זו לא חבילה חינמית בלי הגבלה.",
        "fil": "Nagre-reset ang daily data sa 00:00. Hindi ito unlimited free plan.",
    }.get(lang, "Daily free traffic resets at 00:00. That is not an unlimited free plan.")
    lis = "".join(f"<p>{html.escape(p)}</p>" for p in paras)
    chips = f"""<div class="chips">
<span class="chip">{html.escape(f['city'])}</span>
<span class="chip">{html.escape(f['isp'])}</span>
<span class="chip">{html.escape(f['device'])}</span>
<span class="chip">{html.escape(f['node'])}</span>
</div>"""
    cta_html = f'<p><a class="cta" href="{html.escape(cta)}">{html.escape(label)}</a></p>'
    aside = f'<div class="card"><p>{html.escape(reset_aside)}</p></div>'
    if layout == "a":
        article = f"""
<p class="muted">{html.escape(f['day'].isoformat())} · {html.escape(f['loc']['name'])} · {html.escape(f['place'])}</p>
<h1>{html.escape(title)}</h1>
{lis}
{cta_html}
{aside}
"""
    elif layout == "b":
        article = f"""
<p class="muted">{html.escape(name)}</p>
<h1>{html.escape(title)}</h1>
{chips}
<p class="muted">{html.escape(f['day'].isoformat())} · {html.escape(f['loc']['name'])}</p>
{lis}
{aside}
{cta_html}
"""
    else:
        mid = len(paras) // 2 or 1
        head = "".join(f"<p>{html.escape(p)}</p>" for p in paras[:mid])
        tail = "".join(f"<p>{html.escape(p)}</p>" for p in paras[mid:])
        article = f"""
<p class="muted">{html.escape(f['day'].isoformat())}</p>
<h1>{html.escape(title)}</h1>
{head}
{cta_html}
{tail}
{aside}
<p class="muted">{html.escape(f['city'])} · {html.escape(f['place'])} · {html.escape(f['isp'])}</p>
"""
    schema = json.dumps(
        {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "WebSite",
                    "name": name,
                    "url": canon,
                    "inLanguage": lang,
                },
                {
                    "@type": "Article",
                    "headline": title,
                    "description": desc,
                    "datePublished": f["day"].isoformat(),
                    "inLanguage": lang,
                    "author": {"@type": "Organization", "name": "SingLinkVPN field notes"},
                    "about": intent_kw(f),
                    "mainEntityOfPage": canon,
                },
            ],
        },
        ensure_ascii=False,
    )
    direction = "rtl" if lang in {"ar", "he"} else "ltr"
    kicker = {
        "en": "staff field note",
        "zh-Hant": "員工現場筆記",
        "zh-Hans": "员工现场笔记",
        "ja": "社員の現場メモ",
        "ko": "직원 현장 메모",
        "es": "nota de campo del equipo",
        "pt": "nota de campo da equipa",
        "de": "interne Feldnotiz",
        "fr": "note de terrain",
        "it": "nota di campo",
        "nl": "veldnotitie",
        "pl": "notatka zespołu",
        "tr": "ekip saha notu",
        "id": "catatan lapangan",
        "th": "บันทึกภาคสนาม",
        "vi": "ghi chép hiện trường",
        "ar": "ملاحظة ميدانية",
        "hi": "स्टाफ फील्ड नोट",
        "ms": "nota lapangan",
        "uk": "польова нотатка",
        "ru": "полевая заметка",
        "he": "פתק שטח",
        "fil": "field note ng staff",
    }.get(lang, "staff field note")
    index = f"""<!DOCTYPE html>
<html lang="{html.escape(lang)}" dir="{direction}">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}"/>
<link rel="canonical" href="{html.escape(canon)}"/>
<meta name="robots" content="index,follow"/>
<meta name="author" content="SingLinkVPN staff field notes"/>
<style>{_css(theme, font, layout)}</style>
<script type="application/ld+json">{schema}</script>
</head>
<body>
<header>
  <div class="site-name">{html.escape(name)}</div>
  <p class="muted">{html.escape(f['city'])} · {html.escape(kicker)}</p>
</header>
<main>
<article>
{article}
</article>
</main>
<footer>
  <p>{html.escape(footer)}</p>
  <p><a href="{html.escape(home)}">singlinkvpn.com</a></p>
</footer>
</body>
</html>
"""
    robots = f"User-agent: *\nAllow: /\nSitemap: {canon}sitemap.xml\n"
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{html.escape(canon)}</loc></url>
</urlset>
"""
    not_found = f"""<!DOCTYPE html>
<html lang="{html.escape(lang)}">
<head><meta charset="utf-8"/><title>Not found</title>
<meta name="robots" content="noindex"/>
<style>{_css(theme, font, layout)}</style>
</head>
<body>
<main>
<h1>Not found</h1>
<p><a href="./">{html.escape(name)}</a></p>
</main>
</body>
</html>
"""
    readme = f"""# {name}

Staff field note from {f['city']} ({f['isp']}) on {f['day'].isoformat()}.

Daily free traffic resets at 00:00. This is not an unlimited free plan.

Official download: {cta}

Live URL: {canon}
"""
    return {
        "n": n,
        "repo": repo,
        "url": canon,
        "title": title,
        "desc": desc,
        "lang": lang,
        "city": f["city"],
        "intent": f["intent"]["id"],
        "store": store,
        "cta": cta,
        "slug": f["slug"],
        "description": (
            f"Staff field note from {f['city']} ({f['isp']}). "
            f"Daily free reset at 00:00, not unlimited. Official {store} download only."
        )[:350],
        "files": {
            "index.html": index,
            "robots.txt": robots,
            "sitemap.xml": sitemap,
            "404.html": not_found,
            ".nojekyll": "",
            "README.md": readme,
        },
    }


def write_site(n: int, dest) -> dict:
    from pathlib import Path

    meta = render_files(n)
    root = Path(dest)
    root.mkdir(parents=True, exist_ok=True)
    for rel, text in meta["files"].items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return {k: v for k, v in meta.items() if k != "files"}
