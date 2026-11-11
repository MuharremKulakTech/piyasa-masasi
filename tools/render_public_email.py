"""Piyasa Masası abone e-postası (herkese açık sürüm).
Kullanım: python3 render_public_email.py public/data/latest.json cikti.html
Kişisel içerik yok: sepet, puan, takip listesi bu e-postada yer almaz.
"""
import json, sys, html

SITE = "https://piyasa-masasi.netlify.app"
OR, DK = "#c2410c", "#9a3412"
d = json.load(open(sys.argv[1], encoding="utf-8"))
out = sys.argv[2]
e = lambda s: html.escape(str(s if s is not None else ""))

IMG = {"logo": 0, "canli": 1, "piyasalar": 2}  # inline attachment order; haber-N = 2 + N
def img(key, alt, w=552, href=None):
    src = f"cid:att{IMG[key] if key in IMG else 2 + int(key.split('-')[1])}"
    tag = f'<img src="{src}" width="{w}" alt="{e(alt)}" style="display:block;width:100%;max-width:{w}px;height:auto;border:0;border-radius:10px;">'
    return f'<a href="{href}" style="text-decoration:none;">{tag}</a>' if href else tag

def button(label, href, sub=""):
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:14px;"><tr><td align="center" bgcolor="{OR}" style="background:{OR};border-radius:10px;">'
            f'<a href="{href}" style="display:block;padding:15px 10px;color:#ffffff;font-size:18px;font-weight:bold;text-decoration:none;">{e(label)}</a></td></tr></table>'
            + (f'<p style="font-size:13px;color:#555;text-align:center;margin:8px 0 0;">{e(sub)}</p>' if sub else ""))

def pct(c):
    if c is None or c == "":
        return ""
    c = float(c)
    col = "#15803d" if c > 0 else ("#b91c1c" if c < 0 else "#555555")
    s = ("+" if c > 0 else "−" if c < 0 else "") + "%" + f"{abs(c):.2f}".replace(".", ",")
    return f'<span style="color:{col};font-weight:bold;">{s}</span>'

def num(v):
    if isinstance(v, (int, float)):
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return e(v)

def section(title, body):
    return (f'<tr><td style="padding:28px 24px 0 24px;"><div style="font-size:13px;font-weight:bold;color:{OR};'
            f'letter-spacing:1px;text-transform:uppercase;border-bottom:2px solid {OR};padding-bottom:6px;">{e(title)}</div>'
            f'{body}</td></tr>')

TD = "padding:9px 0;border-bottom:1px solid #eeeeee;"
def row(name, sub, val, chg):
    return (f'<tr><td style="{TD}"><b>{e(name)}</b>' + (f'<br><span style="color:#777;font-size:12px;">{e(sub)}</span>' if sub else "") +
            f'</td><td align="right" style="{TD}white-space:nowrap;padding-left:8px;">{val}<br>{pct(chg)}</td></tr>')

def table(rows):
    return '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="font-size:14px;">' + "".join(rows) + "</table>"

news = d.get("news", [])
quick = (d.get("ozet3") or [n["title"] for n in news[:3]])[:3]
quick_html = "".join(
    f'<tr><td valign="top" style="padding:6px 10px 6px 0;width:28px;"><div style="width:26px;height:26px;line-height:26px;border-radius:13px;background:{OR};color:#fff;text-align:center;font-weight:bold;font-size:13px;">{i+1}</div></td>'
    f'<td style="padding:6px 0;font-size:16px;line-height:1.4;font-weight:bold;color:#111;">{e(t)}</td></tr>' for i, t in enumerate(quick))

parts = []
mk = [row(i["name"], "", num(i.get("value")), i.get("chg")) for i in d.get("indices", [])]
mk += [row(m["name"], "", e(m.get("value")), m.get("chg")) for m in d.get("macro", [])]
mk += [row(c.get("name"), "", ("$" + num(c["price"])) if c.get("price") is not None else "—", c.get("chg")) for c in d.get("crypto", [])]
parts.append(section("Piyasalar · önceki kapanış", '<div style="margin-top:14px;">' + img("piyasalar", "Endeks, emtia ve kriptoda günlük değişim grafiği") + "</div>"))
parts.append(section("Canlı izle", '<div style="margin-top:14px;">' + img("canli", "Dolar/TL, Euro/TL, gram altın ve ABD hisselerini portalda canlı izle", href=SITE + "/#fiyatlar") + "</div>" +
    button("Canlı fiyatları portalda izle →", SITE + "/#fiyatlar", "Dolar/TL, Euro/TL, gram altın ve ABD hisselerinin dolar ve TL fiyatlarını bu portaldan anlık izleyebilirsiniz.")))

cards = ""
for i, n in enumerate(news[:6]):
    tick = " · ".join(n.get("tickers", [])[:4])
    cards += (f'<div style="padding:16px 0;border-bottom:1px solid #eeeeee;">'
              + f'<div style="margin-bottom:12px;">{img(f"haber-{i+1}", n.get("sector") or "Haber", href=SITE + f"/#haber-{i+1}")}</div>'
              + f'<div style="font-size:18px;font-weight:bold;color:#111;line-height:1.3;">{e(n["title"])}</div>'
              f'<p style="font-size:14px;line-height:1.55;color:#333;margin:6px 0 6px;">{e(n.get("summary",""))}</p>'
              + (f'<p style="font-size:14px;line-height:1.5;color:{DK};margin:0;"><b>Bu ne demek?</b> {e(n["anlami"])}</p>' if n.get("anlami") else "")
              + f'<p style="margin:8px 0 0;"><a href="{SITE}/#haber-{i+1}" style="font-size:13px;color:{DK};">Canlı grafiğiyle sitede oku →</a></p></div>')
parts.append(section("Günün haberleri", cards))

men = [b for b in d.get("bigcaps", []) if b.get("note")][:8]
if men:
    parts.append(section("Dev şirketlerde gündem", table([
        f'<tr><td valign="top" style="{TD}width:62px;font-family:Menlo,monospace;font-weight:bold;color:#111;">{e(b["ticker"])}</td>'
        f'<td style="{TD}font-size:13px;color:#444;"><b style="color:#111;">{e(b.get("name",""))}</b> · {e(b["note"])}</td></tr>' for b in men])))

t = d.get("term") or {}
if t.get("name"):
    parts.append(section("Günün terimi",
        f'<div style="background:#fff1e6;border-radius:10px;padding:14px 16px;margin-top:12px;"><div style="font-size:17px;font-weight:bold;color:#111;">{e(t["name"])}</div>'
        f'<p style="font-size:14px;line-height:1.5;color:#333;margin:6px 0 0;">{e(t.get("text",""))}</p></div>'))

cal = "".join(f'<p style="font-size:14px;line-height:1.5;margin:10px 0;"><b>{e(c["day"])}</b><br>' + "<br>".join("• " + e(i) for i in c.get("items", [])) + "</p>" for c in d.get("calendar", []))
if cal:
    parts.append(section("Takvim", cal))

dt = d.get("asOfLabel", d.get("date", ""))
H = f'''<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f2f2f2;"><tr><td align="center" style="padding:16px 8px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:600px;background:#ffffff;font-family:Arial,Helvetica,sans-serif;color:#1a1a1a;">
<tr><td align="center" bgcolor="{OR}" style="background:{OR};padding:12px 16px;"><a href="{SITE}/#fiyatlar" style="color:#1a1a1a;font-size:15px;font-weight:bold;text-decoration:underline;">Canlı fiyatlar: Dolar/TL, Euro/TL, gram altın ve ABD hisseleri</a></td></tr>
<tr><td bgcolor="#000000" style="background:#000000;padding:0;"><a href="{SITE}" style="text-decoration:none;"><img src="cid:att0" width="600" alt="PiyasaMasası · ABD borsası, sade Türkçe ile" style="display:block;width:100%;max-width:600px;height:auto;border:0;"></a></td></tr>
<tr><td style="padding:22px 24px 0 24px;"><div style="font-size:14px;color:#555555;"><b>Günün Özeti</b> | {e(dt)}</div>
<div style="border-top:2px solid #dddddd;margin:14px 0 16px 0;"></div>
<div style="font-size:28px;line-height:1.25;font-weight:bold;color:#111111;">{e(d.get("headline"))}</div>
<div style="font-size:12px;font-weight:bold;letter-spacing:1px;color:{OR};text-transform:uppercase;margin:22px 0 6px;">30 saniyede bugün</div>
<table role="presentation" cellpadding="0" cellspacing="0" border="0">{quick_html}</table>
<p style="font-size:15px;line-height:1.55;color:#333333;margin:16px 0 20px 0;">{e(d.get("summary"))}</p>
{button("Portala git: fiyatları canlı izle →", SITE, "Haberlerin canlı grafiklerini, Dolar/TL'yi ve gram altını bu portaldan anlık takip edebilirsiniz.")}</td></tr>
<tr><td style="padding:14px 24px 0 24px;"><div style="background:#fff1e6;border-radius:8px;padding:10px 12px;font-size:12px;color:#333;">Bu bülten yalnızca haber ve bilgi amaçlıdır; <b>yatırım tavsiyesi değildir</b>.</div></td></tr>
{"".join(parts)}
<tr><td style="padding:24px 24px 0 24px;">{button("Piyasa Masası portalını aç →", SITE)}</td></tr>
<tr><td style="padding:28px 24px 24px 24px;"><div style="border-top:1px solid #dddddd;padding-top:14px;font-size:12px;line-height:1.6;color:#888888;">
<b style="color:#555;">Yasal uyarı:</b> Piyasa Masası, ABD piyasalarıyla ilgili kamuya açık haberlerin Türkçe özetidir. Buradaki bilgi ve yorumlar yatırım danışmanlığı kapsamında değildir ve hiçbir menkul kıymetin alım-satımı için öneri niteliği taşımaz.<br><br>
Bu e-postayı Piyasa Masası'na abone olduğun için aldın. Bülteni bırakmak için bu e-postayı "abonelikten çık" yazarak yanıtlaman yeterli.<br>
Hazırlayan: Muharrem Kulak · <a href="{SITE}" style="color:#888;">piyasa-masasi.netlify.app</a></div></td></tr>
</table></td></tr></table>'''
open(out, "w", encoding="utf-8").write(H)
print("ok", len(H))
