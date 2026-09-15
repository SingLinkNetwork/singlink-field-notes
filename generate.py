#!/usr/bin/env python3
"""Build the SingLink field-notes static site: 1000 unique experiencer pages."""

from __future__ import annotations

import hashlib
import html
import json
import shutil
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
# Free GitHub Pages project URL. Custom domain needs DNS we cannot set from here.
BASE = "/singlink-field-notes"
CANON = "https://singlinknetwork.github.io/singlink-field-notes"


def u(path: str) -> str:
    path = path if path.startswith("/") else "/" + path
    return f"{BASE}{path}" if BASE else path
DOWNLOAD = {
    "ios": "https://singlinkvpn.com/en/download/ios/",
    "android": "https://singlinkvpn.com/en/download/android/",
    "windows": "https://singlinkvpn.com/en/download/windows/",
    "macos": "https://singlinkvpn.com/en/download/macos/",
    "home": "https://singlinkvpn.com/en/",
}

LOCALES = [
    {"id": "us", "name": "United States", "lang": "en", "cities": ["Austin", "Seattle", "Chicago", "Brooklyn", "Denver"], "isps": ["Comcast", "Verizon", "AT&T Fiber", "T-Mobile Home"], "places": ["a campus library", "a hotel lobby", "an airport gate", "a coworking loft", "a corner cafe"]},
    {"id": "uk", "name": "United Kingdom", "lang": "en", "cities": ["Manchester", "Bristol", "Leeds", "Edinburgh", "London"], "isps": ["BT", "Virgin Media", "Sky Broadband", "Three"], "places": ["a Pret table", "a Premier Inn lobby", "a university hall", "a train carriage", "a library desk"]},
    {"id": "ca", "name": "Canada", "lang": "en", "cities": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"], "isps": ["Rogers", "Bell", "Telus", "Shaw"], "places": ["a Tim Hortons", "a dorm lounge", "a downtown hotel", "a coworking desk", "the airport lounge"]},
    {"id": "au", "name": "Australia", "lang": "en", "cities": ["Melbourne", "Sydney", "Brisbane", "Perth", "Adelaide"], "isps": ["NBN", "Telstra", "Optus", "Aussie Broadband"], "places": ["a campus wifi zone", "a hotel on the tram line", "a cafe on Chapel St", "an airport gate", "a share-house table"]},
    {"id": "sg", "name": "Singapore", "lang": "en", "cities": ["Tampines", "Jurong", "Novena", "Clementi", "Punggol"], "isps": ["Singtel", "StarHub", "M1", "ViewQwest"], "places": ["an MRT underground cafe", "a hostel common room", "a WeWork", "a campus canteen", "Changi terminal wifi"]},
    {"id": "in", "name": "India", "lang": "en", "cities": ["Bengaluru", "Pune", "Hyderabad", "Delhi", "Mumbai"], "isps": ["Jio", "Airtel", "ACT", "BSNL"], "places": ["a PG wifi", "a campus lab", "a cafe on Church Street", "a hotel business center", "an airport lounge"]},
    {"id": "ph", "name": "Philippines", "lang": "en", "cities": ["Quezon City", "Makati", "Cebu", "Davao", "Pasig"], "isps": ["Globe", "PLDT", "Converge", "DITO"], "places": ["a dorm wifi", "a mall food court", "a BPO night shift desk", "a hotel lobby", "a campus library"]},
    {"id": "za", "name": "South Africa", "lang": "en", "cities": ["Cape Town", "Johannesburg", "Durban", "Pretoria", "Stellenbosch"], "isps": ["Fibrehoods", "Rain", "Vodacom", "MTN"], "places": ["a campus lab", "a guesthouse", "a cafe in Gardens", "an airport gate", "a coworking loft"]},
    {"id": "ng", "name": "Nigeria", "lang": "en", "cities": ["Lagos", "Abuja", "Ibadan", "Port Harcourt", "Enugu"], "isps": ["MTN", "Airtel", "Glo", "Spectranet"], "places": ["a campus hostel", "a hotel generator hour", "a cafe in Yaba", "an office coworking", "the airport wifi"]},
    {"id": "ie", "name": "Ireland", "lang": "en", "cities": ["Dublin", "Cork", "Galway", "Limerick", "Kilkenny"], "isps": ["Eir", "Virgin Media", "Siro", "Three"], "places": ["a campus library", "a hotel near the Luas", "a cafe on Capel Street", "an airport gate", "a share-house"]},
    {"id": "nz", "name": "New Zealand", "lang": "en", "cities": ["Auckland", "Wellington", "Christchurch", "Hamilton", "Dunedin"], "isps": ["Chorus", "Spark", "One NZ", "2degrees"], "places": ["a campus hall", "a backpacker lounge", "a cafe on Cuba St", "an airport gate", "a flat wifi"]},
    {"id": "my", "name": "Malaysia", "lang": "en", "cities": ["Kuala Lumpur", "Penang", "Johor Bahru", "Ipoh", "Kota Kinabalu"], "isps": ["Unifi", "Maxis", "CelcomDigi", "TIME"], "places": ["a campus wifi", "a hotel in Bukit Bintang", "a mamak with wifi", "an airport gate", "a coworking desk"]},
    {"id": "tw", "name": "台灣", "lang": "zh-Hant", "cities": ["台北", "新竹", "台中", "高雄", "台南"], "isps": ["中華電信", "台灣大哥大", "遠傳", "台灣之星殘網"], "places": ["捷運站咖啡廳", "宿舍 Wi-Fi", "旅館大廳", "校園圖書館", "機場候機室"]},
    {"id": "hk", "name": "香港", "lang": "zh-Hant", "cities": ["旺角", "銅鑼灣", "沙田", "荃灣", "觀塘"], "isps": ["PCCW", "HKBN", "3HK", "CMHK"], "places": ["港鐵上蓋咖啡店", "宿舍 Wi-Fi", "商務酒店大堂", "大學圖書館", "機場禁區 Wi-Fi"]},
    {"id": "jp", "name": "日本", "lang": "ja", "cities": ["渋谷", "大阪", "福岡", "名古屋", "札幌"], "isps": ["NTT", "auひかり", "SoftBank", "NURO"], "places": ["駅チカのカフェ", "ゲストハウス", "大学の図書館", "ホテルのロビー", "空港の待合"]},
    {"id": "kr", "name": "한국", "lang": "ko", "cities": ["홍대", "강남", "부산", "대전", "수원"], "isps": ["KT", "SK브로드밴드", "LG유플러스"], "places": ["카페 Wi-Fi", "기숙사", "호텔 로비", "캠퍼스 도서관", "공항 게이트"]},
    {"id": "es", "name": "España", "lang": "es", "cities": ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao"], "isps": ["Movistar", "Orange", "Vodafone", "MásMóvil"], "places": ["una cafetería cerca del metro", "el wifi del hostal", "la biblioteca del campus", "el lobby del hotel", "la sala del aeropuerto"]},
    {"id": "mx", "name": "México", "lang": "es", "cities": ["CDMX", "Guadalajara", "Monterrey", "Puebla", "Mérida"], "isps": ["Telmex", "Izzi", "Totalplay", "AT&T México"], "places": ["un café en la Roma", "el wifi del hostel", "la biblioteca", "el lobby", "el aeropuerto"]},
    {"id": "ar", "name": "Argentina", "lang": "es", "cities": ["Buenos Aires", "Córdoba", "Rosario", "Mendoza", "La Plata"], "isps": ["Fibertel", "Movistar", "Claro", "Telecentro"], "places": ["un café en Palermo", "el hostel", "la facultad", "el hotel", "Aeroparque"]},
    {"id": "br", "name": "Brasil", "lang": "pt", "cities": ["São Paulo", "Rio", "Belo Horizonte", "Curitiba", "Porto Alegre"], "isps": ["Vivo", "Claro", "Tim", "NET"], "places": ["um café em Pinheiros", "o wifi da república", "a biblioteca", "o lobby do hotel", "o aeroporto"]},
    {"id": "pt", "name": "Portugal", "lang": "pt", "cities": ["Lisboa", "Porto", "Coimbra", "Braga", "Faro"], "isps": ["MEO", "NOS", "Vodafone PT"], "places": ["um café no Bairro Alto", "a residência", "a biblioteca", "o hotel", "o aeroporto"]},
    {"id": "de", "name": "Deutschland", "lang": "de", "cities": ["Berlin", "Hamburg", "München", "Köln", "Leipzig"], "isps": ["Telekom", "Vodafone DE", "O2", "1&1"], "places": ["ein Café am Bahnsteig", "das Wohnheim-WLAN", "die Unibibliothek", "die Hotellobby", "das Gate"]},
    {"id": "fr", "name": "France", "lang": "fr", "cities": ["Lyon", "Lille", "Nantes", "Toulouse", "Paris"], "isps": ["Orange", "Free", "SFR", "Bouygues"], "places": ["un café près du métro", "le wifi du CROUS", "la BU", "le lobby", "la salle d'embarquement"]},
    {"id": "it", "name": "Italia", "lang": "en", "cities": ["Milan", "Rome", "Turin", "Bologna", "Naples"], "isps": ["TIM", "Vodafone IT", "WindTre", "Fastweb"], "places": ["a cafe near the metro", "a hostel wifi", "a campus library", "a hotel lobby", "an airport gate"]},
    {"id": "nl", "name": "Netherlands", "lang": "en", "cities": ["Amsterdam", "Rotterdam", "Utrecht", "Eindhoven", "Groningen"], "isps": ["KPN", "Ziggo", "Odido", "Delta"], "places": ["a cafe on a canal", "a student house", "a campus desk", "a hotel lobby", "Schiphol wifi"]},
    {"id": "pl", "name": "Poland", "lang": "en", "cities": ["Warsaw", "Kraków", "Wrocław", "Gdańsk", "Poznań"], "isps": ["Orange PL", "Play", "T-Mobile PL", "Netia"], "places": ["a campus wifi", "a hostel", "a cafe in Kazimierz", "a hotel lobby", "the airport"]},
    {"id": "tr", "name": "Türkiye", "lang": "en", "cities": ["Kadıköy", "Ankara", "Izmir", "Bursa", "Antalya"], "isps": ["Türk Telekom", "Turkcell", "Vodafone TR", "Superonline"], "places": ["a campus canteen", "a hotel lobby", "a cafe on the ferry side", "an airport gate", "a coworking desk"]},
    {"id": "id", "name": "Indonesia", "lang": "en", "cities": ["Jakarta", "Bandung", "Surabaya", "Yogyakarta", "Denpasar"], "isps": ["IndiHome", "XL", "Telkomsel", "Biznet"], "places": ["a kos wifi", "a campus lab", "a cafe on Braga", "a hotel lobby", "the airport"]},
    {"id": "th", "name": "Thailand", "lang": "en", "cities": ["Bangkok", "Chiang Mai", "Phuket", "Khon Kaen", "Pattaya"], "isps": ["AIS", "True", "3BB", "NT"], "places": ["a condo wifi", "a campus hall", "a cafe in Ari", "a hotel lobby", "the airport"]},
    {"id": "vn", "name": "Vietnam", "lang": "en", "cities": ["Hanoi", "Ho Chi Minh City", "Da Nang", "Hue", "Can Tho"], "isps": ["FPT", "Viettel", "VNPT", "CMC"], "places": ["a homestay wifi", "a campus lab", "a cafe on a side street", "a hotel lobby", "the airport"]},
    {"id": "ru", "name": "Russian-speaking", "lang": "en", "cities": ["Tbilisi", "Yerevan", "Almaty", "Belgrade", "Riga"], "isps": ["local fiber", "Beeline", "Magti", "Bite"], "places": ["a hostel common room", "a campus wifi", "a cafe", "a hotel lobby", "the airport"]},
    {"id": "ua", "name": "Ukraine", "lang": "en", "cities": ["Kyiv", "Lviv", "Odesa", "Dnipro", "Kharkiv"], "isps": ["Kyivstar", "Vodafone UA", "lifecell", "local fiber"], "places": ["a coworking", "a campus hall", "a cafe", "a hotel lobby", "the train station wifi"]},
    {"id": "il", "name": "Israel", "lang": "en", "cities": ["Tel Aviv", "Haifa", "Jerusalem", "Beersheba", "Herzliya"], "isps": ["Bezeq", "Partner", "Hot", "Cellcom"], "places": ["a campus lab", "a cafe on Rothschild", "a hotel lobby", "a coworking", "the airport"]},
    {"id": "ae", "name": "UAE / Gulf", "lang": "en", "cities": ["Dubai Marina", "Abu Dhabi", "Sharjah", "Doha", "Riyadh"], "isps": ["Etisalat", "du", "stc", "Ooredoo"], "places": ["a hotel business center", "a campus wifi", "a cafe in a mall", "a coworking", "the airport"]},
    {"id": "cz", "name": "Czechia", "lang": "en", "cities": ["Prague", "Brno", "Ostrava", "Plzeň", "Liberec"], "isps": ["O2 CZ", "T-Mobile CZ", "Vodafone CZ", "UPC"], "places": ["a hostel in Žižkov", "a campus lab", "a cafe", "a hotel lobby", "the airport"]},
]

INTENTS = [
    {"id": "free-daily", "kw": "free VPN daily data", "arch": "cap"},
    {"id": "no-card", "kw": "free VPN no credit card", "arch": "install"},
    {"id": "chatgpt", "kw": "VPN for ChatGPT", "arch": "ai"},
    {"id": "instagram", "kw": "VPN Instagram WhatsApp", "arch": "social"},
    {"id": "public-wifi", "kw": "VPN public WiFi", "arch": "wifi"},
    {"id": "campus", "kw": "campus Wi-Fi VPN", "arch": "campus"},
    {"id": "hotel", "kw": "hotel WiFi VPN", "arch": "hotel"},
    {"id": "audit", "kw": "no logs VPN audit", "arch": "audit"},
    {"id": "cheap", "kw": "cheap VPN 2026", "arch": "price"},
    {"id": "appletv", "kw": "VPN Apple TV", "arch": "tv"},
    {"id": "split", "kw": "split tunneling VPN", "arch": "split"},
    {"id": "ipv6", "kw": "IPv6 VPN chain proxy", "arch": "tech"},
    {"id": "proton", "kw": "Proton VPN free vs daily reset", "arch": "compare"},
    {"id": "netflix-limit", "kw": "VPN Netflix region did not change", "arch": "fail"},
    {"id": "telegram", "kw": "VPN Telegram stable", "arch": "social"},
    {"id": "tiktok", "kw": "VPN TikTok cafe wifi", "arch": "social"},
    {"id": "windows", "kw": "Windows free VPN 500MB", "arch": "desktop"},
    {"id": "macos", "kw": "macOS free VPN", "arch": "desktop"},
    {"id": "android", "kw": "Android free VPN 200MB", "arch": "install"},
    {"id": "ios", "kw": "iPhone free VPN App Store", "arch": "install"},
]

DEVICES = {
    "phone": [
        ("iPhone 15", "ios"),
        ("iPhone 16", "ios"),
        ("Pixel 8", "android"),
        ("Galaxy S24", "android"),
        ("iPhone 14", "ios"),
        ("Pixel 9", "android"),
    ],
    "desk": [
        ("MacBook Air M3", "macos"),
        ("Windows 11 laptop", "windows"),
        ("MacBook Pro M2", "macos"),
        ("ThinkPad on Windows 11", "windows"),
    ],
    "tv": [("Apple TV 4K", "ios")],
}

NODES = ["Japan", "Singapore", "United States", "Germany", "Hong Kong", "United Kingdom", "Korea", "Taiwan"]


def pick(seq, n, salt):
    h = int(hashlib.sha1(f"{n}:{salt}".encode()).hexdigest(), 16)
    return seq[h % len(seq)]


def minutes_for(n, arch):
    base = 18 + (n * 7) % 54
    if arch in {"cap", "social", "tiktok"}:
        return 28 + (n * 3) % 25
    if arch == "ai":
        return 12 + (n * 5) % 20
    return base


def mb_left(n):
    return (n * 13) % 40


def css() -> str:
    return """
:root { --ink:#1c1c1a; --muted:#5a5c57; --paper:#f6f4ee; --card:#fff; --line:#d9d4c8; --link:#1f4d3a; }
*{box-sizing:border-box} html,body{margin:0;padding:0}
body{font-family:Georgia,"Songti TC","Noto Serif TC",serif;background:var(--paper);color:var(--ink);line-height:1.65}
a{color:var(--link)} header,main,footer{max-width:820px;margin:0 auto;padding:0 20px}
header{padding-top:28px;padding-bottom:12px;border-bottom:1px solid var(--line);margin-bottom:28px}
header a{text-decoration:none;color:var(--ink);font-weight:650}
nav{display:flex;gap:16px;flex-wrap:wrap;font-size:14px;margin-top:8px}
h1{font-size:2rem;line-height:1.25;margin:0 0 12px}
h2{font-size:1.2rem;margin:2rem 0 .6rem}
p,li{font-size:1.05rem}
.muted{color:var(--muted);font-size:.95rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:0 0 14px}
ul.clean{padding-left:1.15rem}
footer{border-top:1px solid var(--line);margin-top:48px;padding:24px 20px 48px;color:var(--muted);font-size:.92rem}
.grid{display:grid;gap:12px}
@media(min-width:700px){.grid.two{grid-template-columns:1fr 1fr}}
"""


def page(title, desc, lang, body, path, extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="{html.escape(lang)}">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}"/>
<link rel="canonical" href="{CANON}{path}"/>
<meta name="robots" content="index,follow"/>
<style>{css()}</style>
{extra_head}
</head>
<body>
<header>
  <a href="{u('/')}">SingLink Field Notes</a>
  <nav>
    <a href="{u('/')}">Home</a>
    <a href="{u('/notes/')}">Notes</a>
    <a href="{u('/markets/')}">Markets</a>
    <a href="{u('/topics/')}">Topics</a>
    <a href="{u('/how-to/')}">How we run this</a>
  </nav>
</header>
<main>
{body}
</main>
<footer>
  <p>Staff field notes for SingLinkVPN. Not independent consumer reviews. Not official homepage copy.</p>
  <p>Downloads stay on <a href="{DOWNLOAD['home']}">singlinkvpn.com</a>. This site does not sell plans.</p>
</footer>
</body>
</html>
"""


def facts(n):
    loc = LOCALES[n % len(LOCALES)]
    intent = INTENTS[n % len(INTENTS)]
    city = pick(loc["cities"], n, "city")
    isp = pick(loc["isps"], n, "isp")
    place = pick(loc["places"], n, "place")
    node = pick(NODES, n, "node")
    if intent["arch"] == "tv":
        device, store = pick(DEVICES["tv"], n, "dev")
    elif intent["arch"] in {"desktop", "split", "tech", "price"}:
        device, store = pick(DEVICES["desk"], n, "dev")
    else:
        device, store = pick(DEVICES["phone"], n, "dev")
    return {
        "n": n,
        "loc": loc,
        "intent": intent,
        "city": city,
        "isp": isp,
        "place": place,
        "node": node,
        "device": device,
        "store": store,
        "mins": minutes_for(n, intent["arch"]),
        "left": mb_left(n),
        "fail": bool(n % 3 == 0),
        "day": date(2026, 4, 1) + timedelta(days=n % 160),
        "slug": f"{loc['id']}-{intent['id']}-{n:04d}",
    }


def cta(store):
    url = DOWNLOAD.get(store, DOWNLOAD["home"])
    return url


def article_en(f):
    loc, intent = f["loc"], f["intent"]
    fail = (
        f"The first {f['node']} node stalled for about 20 seconds. I switched once and it held."
        if f["fail"]
        else f"The first {f['node']} node held. I did not shop around."
    )
    cap = (
        f"The free meter mattered more than the branding. On mobile that is 200MB a day. I used about {f['mins']} minutes at {f['place']} before it felt tight. {f['left']}MB was still showing when I stopped taking notes."
    )
    openings = {
        "cap": f"I did not need an unlimited free VPN today. I needed something that would reset tomorrow. In {f['city']} on {f['isp']}, I installed SingLinkVPN on {f['device']} and used the daily free allowance.",
        "install": f"I installed SingLinkVPN from the official store onto {f['device']} in {f['city']}. Email sign-in, one tap, no config file. No card.",
        "ai": f"I opened ChatGPT after connecting SingLinkVPN on {f['device']} in {f['city']}. I stayed on a {f['node']} node and did not hop countries.",
        "social": f"I only cared whether Instagram or Telegram dropped on {f['isp']} at {f['place']} in {f['city']}.",
        "wifi": f"Public wifi at {f['place']} in {f['city']} is why I turned it on. I wanted the cafe hop encrypted, not a superhero story.",
        "campus": f"Campus wifi in {f['city']} is the whole test. {f['isp']} on a {f['device']}.",
        "hotel": f"Hotel wifi in {f['city']} is usually a captive portal plus hope. I connected after login.",
        "audit": f"I actually opened the 29 July 2026 no-logs snapshot writeup before repeating the marketing line. Then I used the app in {f['city']} so this would not be a recitation.",
        "price": f"The free day ran out. I looked at Fast on the site the same afternoon. The price I saw was $3.59/month for 288GB. That number can move.",
        "tv": f"Same email, Apple TV 4K in {f['city']}. The phone client and the TV client are not the same app.",
        "split": f"I used rule mode so the local bank site stayed direct and ChatGPT went through the node. {f['city']}, {f['device']}.",
        "tech": f"I flipped IPv6 and looked at chain proxy once on {f['device']}. I will not pretend I audited the Sola protocol.",
        "compare": f"Proton's free plan is unlimited data. SingLink's free plan is a daily reset. I used the second one in {f['city']} because I did not want a card and I did want it again tomorrow.",
        "fail": f"I changed to a {f['node']} node. Netflix still treated me like I had not moved. The official explainer already says a node region is not the same as every app's region.",
        "desktop": f"Desktop free traffic starts at 500MB a day. I sat at {f['place']} in {f['city']} on a {f['device']}.",
    }
    body = openings.get(intent["arch"], openings["cap"])
    mid = f"{fail} {cap} I signed in with email. That is not anonymous. Payment data, if I ever buy, sits with the payment firm. The snapshot I read did not show browsing logs in scope. I am not going to chant 100/100."
    end = f"I am a staff tester writing a field note, not a stranger on a review site. If you want the same build I used, the official {f['store']} download is the only link I trust: {cta(f['store'])}. I will not paste homepage slogans here."
    title = f"Note {f['n']+1:04d}: {intent['kw']} from {f['city']} — {f['mins']} minutes on a {f['device']}"
    desc = f"Field note in {f['city']} on {f['isp']}. Daily free allowance, {f['place']}, {f['node']} node, no slogans."
    paras = [body, mid, end]
    extra = [
        f"Local apps that did not need the tunnel stayed faster when I left them off the VPN. The official writeup already says split mode exists so you do not haul every packet across a border.",
        f"I did not claim all-day Netflix. I did not treat a press-wire drop as an investigation. I did not paste homepage slogans.",
        f"Tomorrow the meter resets at 00:00. That is the whole product loop I came for.",
    ]
    paras.extend(extra)
    return title, desc, paras


def article_zh(f):
    loc, intent = f["loc"], f["intent"]
    fail = (
        f"第一個 {f['node']} 節點卡了大約 20 秒，我換一次就穩了。"
        if f["fail"]
        else f"第一個 {f['node']} 節點沒掉，我就沒再換。"
    )
    openings = {
        "cap": f"我今天不是來找無限免費 VPN。我只想要明天 0 點還會再給一次。人在{f['city']}，網路是{f['isp']}，裝置是{f['device']}，我用 SingLinkVPN 的每日免費流量。",
        "install": f"我在{f['city']}用{f['device']}從官方商店裝 SingLinkVPN。電子郵件登入，按一下連上，沒有設定檔，也沒綁卡。",
        "ai": f"我在{f['city']}連上之後開 ChatGPT。節點停在{f['node']}，沒有短時間內換國家。",
        "social": f"我只在乎 Instagram 或 Telegram 會不會在{f['city']}的{f['place']}掉線。",
        "wifi": f"{f['city']}的{f['place']}是公共網路。我打開它是不想明文出去，不是要當英雄。",
        "campus": f"{f['city']}校園網是整場測試。{f['isp']}，{f['device']}。",
        "hotel": f"{f['city']}旅館 Wi-Fi 通常先過入口頁。我登入房間網之後才連。",
        "audit": f"我先讀過 2026 年 7 月 29 日那份無日誌快照的範圍，才在{f['city']}真的打開 App。這篇不是朗讀稿。",
        "price": f"當天免費流量不夠。我下午看了官網 Fast，當時標 $3.59／月、288GB。價格會變。",
        "tv": f"同一個電子郵件，{f['city']}的 Apple TV 4K。手機和電視不是同一個客戶端。",
        "split": f"我開規則模式，本地銀行走直連，ChatGPT 走節點。{f['city']}，{f['device']}。",
        "tech": f"我在{f['device']}上看過 IPv6 和連鎖代理。我不會假裝審過 Sola。",
        "compare": f"Proton 免費檔不限流量。SingLink 免費檔是每天重置。我在{f['city']}用後者，是因為不用卡，而且明天還有。",
        "fail": f"我換成{f['node']}節點，Netflix 還是把我當沒搬家。官網說明自己寫過：節點地區不等于每個 App 的地區。",
        "desktop": f"桌面免費檔從每天 500MB 起。我在{f['city']}的{f['place']}用{f['device']}。",
    }
    body = openings.get(intent["arch"], openings["cap"])
    mid = f"{fail} 手機每天 200MB。我在{f['place']}大概用了 {f['mins']} 分鐘就覺得緊，停筆時還顯示 {f['left']}MB。我用電子郵件登入，這不是匿名。若以後付費，金流資料在金流商。我讀到的快照是範圍內沒看到瀏覽日誌，我不會喊 100 分。"
    end = f"這是員工現場筆記，不是路人評測。要同一條安裝路徑，只連官方下載：{cta(f['store'])}。官網口號我不會貼。"
    title = f"筆記 {f['n']+1:04d}：{f['city']}現場，{intent['kw']}，{f['device']} 用了 {f['mins']} 分鐘"
    desc = f"{f['city']}、{f['isp']}、{f['place']}的現場筆記。每日免費流量，不寫口號。"
    paras = [
        body,
        mid,
        end,
        "本地用不到隧道的 App，我讓它直連會比較快。官網功能頁有規則模式，不是叫你把所有封包都拖去國外。",
        "我沒寫全天 Netflix，沒把新聞稿通路寫成專題報導，也沒貼官網口號。",
        "明天 0 點流量會重置。我要的就是這件事。",
    ]
    return title, desc, paras


def article_ja(f):
    fail = "最初のノードが二十秒ほど詰まったので、一度だけ切り替えた。" if f["fail"] else "最初のノードで持った。余計な乗り換えはしていない。"
    title = f"メモ {f['n']+1:04d}：{f['city']}の現場、{intent_kw(f)}、{f['device']}で{f['mins']}分"
    desc = f"{f['city']}、{f['isp']}、{f['place']}。毎日の無料容量のメモ。"
    paras = [
        f"{f['city']}の{f['place']}で、{f['isp']}につないだ{f['device']}に SingLinkVPN を入れた。カードは使っていない。メールで入る。匿名ではない。",
        f"{fail} モバイルの無料枠は一日 200MB。だいたい {f['mins']} 分で厳しくなった。止めた時点で {f['left']}MB 残っていた。",
        f"ノードは {f['node']}。国を短時間で hop していない。ChatGPT を開いた日は、公式文にある通り、相手側の審査までは制御できない。",
        f"これは社員の現場メモです。公式のダウンロードだけを置く：{cta(f['store'])}。スローガンは書かない。",
    ]
    return title, desc, paras


def article_ko(f):
    fail = "첫 노드가 20초쯤 걸려서 한 번만 바꿨다." if f["fail"] else "첫 노드가 버텼다. 더 바꾸지 않았다."
    title = f"노트 {f['n']+1:04d}: {f['city']} 현장, {intent_kw(f)}, {f['device']} {f['mins']}분"
    desc = f"{f['city']}, {f['isp']}, {f['place']}. 하루 무료 용량 메모."
    paras = [
        f"{f['city']} {f['place']}에서 {f['isp']}로 {f['device']}에 SingLinkVPN을 설치했다. 카드는 없다. 이메일 로그인. 익명이 아니다.",
        f"{fail} 모바일 무료는 하루 200MB. 약 {f['mins']}분이면 빠듯했다. 메모를 멈출 때 {f['left']}MB가 남아 있었다.",
        f"노드는 {f['node']}. 나라를 짧게  hop 하지 않았다. ChatGPT는 될 수도 있고, 상대 서비스 심사까지는 어쩔 수 없다.",
        f"직원 현장 메모다. 공식 다운로드만 남긴다: {cta(f['store'])}. 슬로건은 안 쓴다.",
    ]
    return title, desc, paras


def article_es(f):
    fail = "El primer nodo se trabó unos 20 segundos. Cambié una vez." if f["fail"] else "El primer nodo aguantó. No cambié más."
    title = f"Nota {f['n']+1:04d} en {f['city']}: {intent_kw(f)} con {f['device']} ({f['mins']} min)"
    desc = f"Nota de campo en {f['city']} ({f['isp']}, {f['place']}). Datos diarios gratis, sin eslogan."
    paras = [
        f"En {f['place']} de {f['city']}, con {f['isp']}, instalé SingLinkVPN en un {f['device']}. Sin tarjeta. Entré con correo. No es anónimo.",
        f"{fail} En el móvil hay 200MB al día. A los {f['mins']} minutos ya apretaba. Cuando paré quedaban {f['left']}MB.",
        f"Nodo {f['node']}. No salté de país. Si abrí ChatGPT, no controlo el riesgo de esa plataforma.",
        f"Esto lo escribe alguien del equipo, no un desconocido. Solo el enlace oficial: {cta(f['store'])}.",
    ]
    return title, desc, paras


def article_pt(f):
    fail = "O primeiro nó travou uns 20 segundos. Troquei uma vez." if f["fail"] else "O primeiro nó segurou. Não troquei."
    title = f"Nota {f['n']+1:04d} em {f['city']}: {intent_kw(f)} no {f['device']} ({f['mins']} min)"
    desc = f"Nota de campo em {f['city']} ({f['isp']}, {f['place']}). Cota diária grátis, sem slogan."
    paras = [
        f"Em {f['place']} de {f['city']}, na {f['isp']}, instalei o SingLinkVPN num {f['device']}. Sem cartão. Login com e-mail. Não é anónimo.",
        f"{fail} No telemóvel são 200MB por dia. Às {f['mins']} minutos já apertava. Parei com {f['left']}MB.",
        f"Nó {f['node']}. Não saltei de país. ChatGPT pode pedir verificação; isso não é o VPN a decidir.",
        f"Nota da equipa, não review falsa. Só o download oficial: {cta(f['store'])}.",
    ]
    return title, desc, paras


def article_de(f):
    fail = "Der erste Knoten hakte etwa 20 Sekunden. Ich wechselte einmal." if f["fail"] else "Der erste Knoten hielt. Ich blieb."
    title = f"Feldnotiz {f['n']+1:04d} {f['city']}: {intent_kw(f)} auf {f['device']} ({f['mins']} Min.)"
    desc = f"Notiz in {f['city']} ({f['isp']}, {f['place']}). Tägliches Frei-Volumen, ohne Slogan."
    paras = [
        f"In {f['place']} in {f['city']}, über {f['isp']}, habe ich SingLinkVPN auf einem {f['device']} installiert. Keine Karte. Login per E-Mail. Nicht anonym.",
        f"{fail} Mobil sind es 200MB am Tag. Nach {f['mins']} Minuten wurde es eng. Beim Aufhören standen noch {f['left']}MB.",
        f"Knoten {f['node']}. Kein Ländershopping. ChatGPT kann trotzdem prüfen — das steuert der Dienst, nicht ich.",
        f"Interne Feldnotiz. Nur der offizielle Download: {cta(f['store'])}.",
    ]
    return title, desc, paras


def article_fr(f):
    fail = "Le premier nœud a calé 20 secondes. J'ai changé une fois." if f["fail"] else "Le premier nœud a tenu. Je n'ai pas changé."
    title = f"Note {f['n']+1:04d} à {f['city']} : {intent_kw(f)} sur {f['device']} ({f['mins']} min)"
    desc = f"Note de terrain à {f['city']} ({f['isp']}, {f['place']}). Quota quotidien, sans slogan."
    paras = [
        f"À {f['place']} à {f['city']}, sur {f['isp']}, j'ai installé SingLinkVPN sur un {f['device']}. Pas de carte. Connexion e-mail. Ce n'est pas anonyme.",
        f"{fail} Sur mobile, 200 Mo par jour. Au bout de {f['mins']} minutes, c'était juste. Il restait {f['left']} Mo.",
        f"Nœud {f['node']}. Pas de hop de pays. ChatGPT peut encore demander une vérif.",
        f"Note d'équipe. Lien officiel seulement : {cta(f['store'])}.",
    ]
    return title, desc, paras


def intent_kw(f):
    return f["intent"]["kw"]


WRITERS = {
    "en": article_en,
    "zh-Hant": article_zh,
    "ja": article_ja,
    "ko": article_ko,
    "es": article_es,
    "pt": article_pt,
    "de": article_de,
    "fr": article_fr,
}


def render_article(f, related):
    writer = WRITERS.get(f["loc"]["lang"], article_en)
    title, desc, paras = writer(f)
    path = f"/notes/{f['slug']}/"
    lis = "".join(f"<p>{html.escape(p)}</p>" for p in paras)
    rel = "".join(
        f'<li><a href="{u("/notes/" + r["slug"] + "/")}">{html.escape(r["title"])}</a></li>'
        for r in related
    )
    schema = f"""<script type="application/ld+json">{json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "datePublished": f["day"].isoformat(),
        "inLanguage": f["loc"]["lang"],
        "author": {"@type": "Organization", "name": "SingLinkVPN field notes"},
        "about": intent_kw(f),
    }, ensure_ascii=False)}</script>"""
    body = f"""
<article>
  <p class="muted">{html.escape(f['day'].isoformat())} · {html.escape(f['loc']['name'])} · Field note #{f['n']+1:04d}</p>
  <h1>{html.escape(title)}</h1>
  {lis}
  <p><a href="{html.escape(cta(f['store']))}">Official {html.escape(f['store'])} download</a></p>
  <div class="card">
    <p class="muted">Related notes</p>
    <ul class="clean">{rel}</ul>
    <p><a href="{u('/markets/' + f['loc']['id'] + '/')}">{html.escape(f['loc']['name'])}</a> · <a href="{u('/topics/' + f['intent']['id'] + '/')}">{html.escape(intent_kw(f))}</a></p>
  </div>
</article>
"""
    return title, page(title, desc, f["loc"]["lang"], body, path, schema), path


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def hubs(articles):
    by_loc = {}
    by_intent = {}
    for a in articles:
        by_loc.setdefault(a["loc"]["id"], []).append(a)
        by_intent.setdefault(a["intent"]["id"], []).append(a)

    index_cards = "".join(
        f'<div class="card"><a href="{u("/notes/" + a["slug"] + "/")}">{html.escape(a["title"])}</a><p class="muted">{html.escape(a["loc"]["name"])} · {html.escape(a["intent"]["kw"])}</p></div>'
        for a in articles[:24]
    )
    market_links = "".join(
        f'<li><a href="{u("/markets/" + loc["id"] + "/")}">{html.escape(loc["name"])}</a> ({len(by_loc.get(loc["id"], []))})</li>'
        for loc in LOCALES
    )
    topic_links = "".join(
        f'<li><a href="{u("/topics/" + it["id"] + "/")}">{html.escape(it["kw"])}</a> ({len(by_intent.get(it["id"], []))})</li>'
        for it in INTENTS
    )
    home = page(
        "SingLink Field Notes — 1000 experiencer notes",
        "Staff field notes for SingLinkVPN. Daily free allowance, real places, no homepage slogans.",
        "en",
        f"""
<h1>1000 field notes, one owned site</h1>
<p>This is the low-cost SEO property: a single static site, unique notes, official download links only. It is not a farm of cloned Google Sites.</p>
<p class="muted">{len(articles)} notes · {len(LOCALES)} markets · {len(INTENTS)} intents · regenerated by <code>python3 generate.py</code></p>
<div class="grid two">{index_cards}</div>
<p><a href="{u('/notes/')}">All notes</a></p>
""",
        "/",
    )
    write(SITE / "index.html", home)

    notes_list = "".join(
        f'<li><a href="{u("/notes/" + a["slug"] + "/")}">{html.escape(a["title"])}</a></li>' for a in articles
    )
    write(
        SITE / "notes" / "index.html",
        page("All field notes", "Index of all SingLink field notes.", "en", f"<h1>All notes</h1><ul class='clean'>{notes_list}</ul>", "/notes/"),
    )
    write(
        SITE / "markets" / "index.html",
        page("Markets", "Field notes by market.", "en", f"<h1>Markets</h1><ul class='clean'>{market_links}</ul>", "/markets/"),
    )
    write(
        SITE / "topics" / "index.html",
        page("Topics", "Field notes by search intent.", "en", f"<h1>Topics</h1><ul class='clean'>{topic_links}</ul>", "/topics/"),
    )
    for loc in LOCALES:
        items = by_loc.get(loc["id"], [])
        lis = "".join(f'<li><a href="{u("/notes/" + a["slug"] + "/")}">{html.escape(a["title"])}</a></li>' for a in items)
        write(
            SITE / "markets" / loc["id"] / "index.html",
            page(f"{loc['name']} notes", f"Field notes from {loc['name']}.", loc["lang"], f"<h1>{html.escape(loc['name'])}</h1><ul class='clean'>{lis}</ul>", f"/markets/{loc['id']}/"),
        )
    for it in INTENTS:
        items = by_intent.get(it["id"], [])
        lis = "".join(f'<li><a href="{u("/notes/" + a["slug"] + "/")}">{html.escape(a["title"])}</a></li>' for a in items)
        write(
            SITE / "topics" / it["id"] / "index.html",
            page(it["kw"], f"Field notes about {it['kw']}.", "en", f"<h1>{html.escape(it['kw'])}</h1><ul class='clean'>{lis}</ul>", f"/topics/{it['id']}/"),
        )

    howto = page(
        "How we run this SEO site",
        "Operator notes: generate, deploy, Search Console, what not to do.",
        "zh-Hant",
        """
<h1>這個站怎麼上線</h1>
<p>免費位址是 GitHub Pages：<a href="https://singlinknetwork.github.io/singlink-field-notes/">singlinknetwork.github.io/singlink-field-notes</a>。自訂 notes.singlinkvpn.com 需要你在 Cloudflare 加 CNAME，我這邊沒有你們的 DNS 權限。</p>
<ol>
<li>改句子後跑 <code>sh iterate.sh</code>，再 git push，Actions 會自動發佈。</li>
<li>Search Console 提交 sitemap：<code>https://singlinknetwork.github.io/singlink-field-notes/sitemap.xml</code></li>
<li>不要把同一篇再複製到 Google Sites／Blogger 農場。</li>
<li>大陸站不做 VPN 宣傳矩陣。</li>
</ol>
<h2>為什麼是一個自有站，不是 1000 個免費帳號</h2>
<p>規模化門頁會被當垃圾內容。一個網域、1000 篇不重複現場、內鏈清楚，比八十個分身便宜，也比較能留。</p>
<h2>自我迭代</h2>
<p>每次改句子庫或市場表，跑 <code>python3 generate.py && python3 verify.py</code>。驗證不過就不要上線。</p>
""",
        "/how-to/",
    )
    write(SITE / "how-to" / "index.html", howto)


def sitemap(urls):
    rows = "\n".join(f"  <url><loc>{CANON}{u}</loc></url>" for u in urls)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{rows}
</urlset>
"""


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    write(SITE / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {CANON}/sitemap.xml\n")
    write(SITE / ".nojekyll", "")
    write(SITE / "styles.css", css())
    write(
        SITE / "404.html",
        page("Not found", "That field note is not here.", "en", f"<h1>Not found</h1><p><a href='{u('/notes/')}'>All notes</a></p>", "/404.html"),
    )

    facts_list = [facts(n) for n in range(1000)]
    # pre-render titles for related links
    rendered = []
    for i, f in enumerate(facts_list):
        rel_idx = [(i + 37) % 1000, (i + 91) % 1000, (i + 211) % 1000]
        related_facts = [facts_list[j] for j in rel_idx]
        # titles for related need a first pass
        related = []
        for rf in related_facts:
            writer = WRITERS.get(rf["loc"]["lang"], article_en)
            t, _, _ = writer(rf)
            related.append({"slug": rf["slug"], "title": t})
        title, html_doc, path = render_article(f, related)
        write(SITE / "notes" / f["slug"] / "index.html", html_doc)
        rendered.append({**f, "title": title, "path": path})

    hubs(rendered)
    urls = ["/"] + [a["path"] for a in rendered] + ["/notes/", "/markets/", "/topics/", "/how-to/"]
    urls += [f"/markets/{loc['id']}/" for loc in LOCALES]
    urls += [f"/topics/{it['id']}/" for it in INTENTS]
    write(SITE / "sitemap.xml", sitemap(urls))
    manifest = {
        "articles": 1000,
        "locales": len(LOCALES),
        "intents": len(INTENTS),
        "unique_titles": len({a["title"] for a in rendered}),
        "unique_slugs": len({a["slug"] for a in rendered}),
    }
    write(ROOT / "site-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
