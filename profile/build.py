"""Profil SVG'lerini üretir: header.svg (A3 · tek çizgi) ve link-*.svg (B1 · rozetler).

Çalıştırma:  python profile/build.py
Gerekenler:  pip install fonttools brotli

GitHub README'deki SVG'ler <img> olarak gösterilir: JS çalışmaz, dış dosya
yüklenmez. Bu yüzden animasyon SVG içindeki CSS'te, yazı tipi (Departure Mono)
her dosyaya yalnızca kullandığı harflerle gömülür.
Renkler oguzhd.com'un "Tayf" paletinden (prizma-portfolio/web/src/theme/presets.ts).
"""
import base64
import io
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
FONT = HERE / "fonts" / "DepartureMono-Regular.woff2"

# Koyu: oguzhd.com'un "Tayf" paleti. Açık: aynı tayfın koyulaştırılmış hâli
# (grafit/lavanta denendi, 12.10.2026'da GitHub'a yakın ilk zeminlere dönüldü)
# (beyaz zeminde okunsun diye); beyaz ışık açık zeminde görünmez, ink rengine döner.
PALETTES = {
    "dark": dict(ground="#070A12", line="#1C2436", ink="#E4E9F4", dim="#98A2BA", faint="#7C879F",
                 lead="#22D3EE", light="#FFFFFF", star="#98A2BA",
                 acc=["#A78BFA", "#60A5FA", "#22D3EE", "#4ADE80", "#FACC15", "#FB923C", "#F87171"]),
    "light": dict(ground="#F7F9FC", line="#D8DEE9", ink="#0F1420", dim="#4A5468", faint="#5F6A80",
                  lead="#0891B2", light="#0891B2", star="#B4BDCC",
                  acc=["#7C3AED", "#2563EB", "#0891B2", "#16A34A", "#CA8A04", "#EA580C", "#DC2626"]),
}
# acc: mor → kırmızı (kısa dalga boyundan uzuna), sitedeki sırayla.

ADV = 350 / 550  # Departure Mono: her harf 0.636 em (22 px → 14 px)


def font_css(text: str) -> str:
    """Yalnızca `text` içindeki harflerle küçültülmüş, base64 gömülü @font-face."""
    font = TTFont(FONT)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = []
    opts.name_IDs = []
    opts.notdef_outline = False
    sub = subset.Subsetter(opts)
    sub.populate(text=text + " ")
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:DM;src:url(data:font/woff2;base64,{b64}) format('woff2')}}"


BASE_CSS = (
    "text{font-family:DM,ui-monospace,monospace;font-synthesis:none}"
    "@keyframes fade{from{opacity:0}}"
    "@keyframes up{from{opacity:0;transform:translateY(10px)}}"
    "@keyframes draw{from{stroke-dashoffset:1}}"
    "@keyframes wipe{from{transform:translateX(0)}}"
    ".d{stroke-dasharray:1;stroke-dashoffset:0}"
    # Hareket azaltılmışsa animasyon yok; her öğe zaten son karesinde durur.
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)


def svg(w, h, text, css, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'fill="none" role="img" aria-label="{title}"><title>{title}</title>'
        f"<style>{font_css(text)}{BASE_CSS}{css}</style>{body}</svg>\n"
    )


# ── A3 · Tek çizgi ─────────────────────────────────────────────────────────
# Ad beyaz ışık gibi: altındaki çizgi adın bittiği yerde yedi tona ayrılır.
# Açılıştan sonra her 7 saniyede bir ışık çizgi boyunca akar, tayf bir an parlar.
def header(P):
    W, H = 840, 220
    name, role, site = "Oğuz Han Duran", "junior developer · database → api → ui", "OGUZHD.COM"
    nx, ny, ns = 48, 96, 44
    sx, sy, ex = nx + round(len(name) * ns * ADV), 128, 792  # ayrılma noktası = adın sonu
    rx, ry = 48, 184
    period, loop0 = 7, 3.2

    letters = "".join(
        f'<text x="{nx + i * ns * ADV:.1f}" y="{ny}" font-size="{ns}" fill="{P["ink"]}" '
        f'style="animation:up .6s {0.05 + i * 0.035:.3f}s cubic-bezier(.2,.7,.2,1) backwards">{ch}</text>'
        for i, ch in enumerate(name) if ch != " "
    )
    ends = [sy + 15 - i * 5 for i in range(7)]  # mor en çok kırılır → en altta
    grads = "".join(
        f'<linearGradient id="g{i}" gradientUnits="userSpaceOnUse" x1="{sx}" x2="{ex}" y1="0" y2="0">'
        f'<stop stop-color="{c}" stop-opacity=".45"/><stop offset="1" stop-color="{c}"/></linearGradient>'
        for i, c in enumerate(P["acc"])
    )
    fan = "".join(
        f'<line class="d" pathLength="1" x1="{sx}" y1="{sy}" x2="{ex}" y2="{y}" stroke="url(#g{i})" stroke-width="1.5" '
        f'style="animation:draw .9s {1.05 + i * 0.05:.2f}s cubic-bezier(.2,.7,.2,1) backwards,'
        f'flash {period}s {loop0 + 0.55 + i * 0.05:.2f}s ease-out infinite"/>'
        f'<circle cx="{ex}" cy="{y}" r="1.5" fill="{P["acc"][i]}" '
        f'style="animation:fade .3s {1.8 + i * 0.05:.2f}s backwards,flash {period}s {loop0 + 0.8 + i * 0.05:.2f}s ease-out infinite"/>'
        for i, y in enumerate(ends)
    )
    stars = "".join(
        f'<circle cx="{x}" cy="{y}" r="1" fill="{P["star"]}" style="animation:tw {2.6 + k * 0.7:.1f}s {k * 0.5:.1f}s ease-in-out infinite alternate"/>'
        for k, (x, y) in enumerate([(612, 34), (700, 58), (548, 186), (760, 196), (480, 30), (812, 150)])
    )
    css = (
        "@keyframes tw{to{opacity:.15}}"
        "@keyframes flash{0%{opacity:1}4%{opacity:1;filter:brightness(1.6)}14%,100%{opacity:1;filter:none}}"
        # Işık çizgi boyunca akar: kısa parlak parça 0'dan 1'e kayar, sonra bekler.
        "@keyframes run{0%{stroke-dashoffset:.1}9%,100%{stroke-dashoffset:-1}}"
        "@keyframes glint{0%,6%{opacity:0;transform:scale(.4)}9%{opacity:1;transform:scale(1)}20%,100%{opacity:0;transform:scale(.4)}}"
        f".w{{animation:draw .6s .55s ease-in backwards}}"
        f".run{{stroke-dasharray:.1 1.2;stroke-dashoffset:.1;animation:run {period}s {loop0}s linear infinite}}"
        f".gl{{opacity:0;transform-box:fill-box;transform-origin:center;animation:glint {period}s {loop0}s ease-out infinite}}"
        f".cv{{transform:translateX({len(role) * 22 * ADV + 8:.0f}px);animation:wipe .9s 1.5s steps({len(role)}) backwards}}"
        ".u{animation:fade .6s 2.3s backwards}"
    )
    body = (
        f'<defs>{grads}<clipPath id="c"><rect width="{W}" height="{H}" rx="12"/></clipPath></defs>'
        f'<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{P["ground"]}"/>{stars}'
        f"{letters}"
        f'<text class="u" x="{ex}" y="{ny}" font-size="11" letter-spacing="2" text-anchor="end" fill="{P["faint"]}">{site}</text>'
        f'<line class="d w" pathLength="1" x1="{nx}" y1="{sy}" x2="{sx}" y2="{sy}" stroke="{P["ink"]}" stroke-width="2"/>'
        f'<line class="run" pathLength="1" x1="{nx}" y1="{sy}" x2="{sx}" y2="{sy}" stroke="{P["light"]}" stroke-width="3" stroke-linecap="round"/>'
        f"{fan}"
        f'<path class="gl" d="M{sx} {sy - 7}V{sy + 7}M{sx - 7} {sy}H{sx + 7}" stroke="{P["light"]}" stroke-width="1.5" stroke-linecap="round"/>'
        f'<text x="{rx}" y="{ry}" font-size="22" fill="{P["dim"]}">{role}</text>'
        f'<rect class="cv" x="{rx - 4}" y="{ry - 22}" width="{len(role) * 22 * ADV + 12:.0f}" height="30" fill="{P["ground"]}"/>'
        f'</g><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="11.5" stroke="{P["line"]}"/>'
    )
    return svg(W, H, name + role + site, css, body, f"{name} — junior developer")


# ── Teknoloji tayfı ────────────────────────────────────────────────────────
# Başlıktaki tayf burada dört banda iner: her bant bir renk, üstünde o işin araçları.
# Işık başlıktaki akış bittikten sonra bantlara geçer (aynı 7 sn'lik döngü).
BANDS = [  # (bant, araçlar, tayf sırası, dalga boyu)
    ("backend", "python · fastapi · django · node.js", 0, 410),
    ("frontend", "typescript · react · next.js · qt", 2, 490),
    ("infra", "docker · rabbitmq · postgresql · redis", 4, 580),
    ("hardware", "esp32 · sensors · firebase", 6, 660),
]


def stack(P):
    W, top, step = 840, 100, 44
    H = top + step * (len(BANDS) - 1) + 44
    lx, tx, period, loop0 = 110, 236, 7, 4.3
    rows, grads = "", ""
    for i, (band, tools, ci, nm) in enumerate(BANDS):
        c, y = P["acc"][ci], top + i * step
        ly, d = y - 8, 0.25 + i * 0.12
        grads += (f'<linearGradient id="s{i}" gradientUnits="userSpaceOnUse" x1="0" x2="{lx}" y1="0" y2="0">'
                  f'<stop stop-color="{c}" stop-opacity="0"/><stop offset="1" stop-color="{c}"/></linearGradient>')
        tw = len(tools) * 22 * ADV
        rows += (
            f'<line class="d" pathLength="1" x1="0" y1="{ly}" x2="{lx}" y2="{ly}" stroke="url(#s{i})" stroke-width="1.5" '
            f'style="animation:draw .7s {d:.2f}s cubic-bezier(.2,.7,.2,1) backwards"/>'
            f'<line class="run" pathLength="1" x1="0" y1="{ly}" x2="{lx}" y2="{ly}" stroke="{P["light"]}" stroke-width="2.5" stroke-linecap="round" '
            f'style="animation-delay:{loop0 + i * 0.08:.2f}s"/>'
            f'<circle cx="{lx}" cy="{ly}" r="2.5" fill="{c}" style="animation:fade .3s {d + 0.6:.2f}s backwards,flash {period}s {loop0 + 0.7 + i * 0.08:.2f}s ease-out infinite"/>'
            f'<g style="animation:fade .4s {d + 0.6:.2f}s backwards"><text x="{lx + 16}" y="{y - 10}" font-size="11" letter-spacing="2" fill="{c}">{band.upper()}</text>'
            f'<text x="{lx + 16}" y="{y + 3}" font-size="11" fill="{P["faint"]}">{nm} nm</text></g>'
            f'<text x="{tx}" y="{y}" font-size="22" fill="{P["ink"]}">{tools}</text>'
            f'<rect x="{tx - 4}" y="{y - 22}" width="{tw + 12:.0f}" height="30" fill="{P["ground"]}" '
            f'style="transform:translateX({tw + 8:.0f}px);animation:wipe .7s {d + 0.75:.2f}s steps({len(tools)}) backwards"/>'
        )
    css = (
        "@keyframes flash{0%{filter:none}4%{filter:brightness(1.6)}14%,100%{filter:none}}"
        "@keyframes run{0%{stroke-dashoffset:.1}9%,100%{stroke-dashoffset:-1}}"
        f".run{{stroke-dasharray:.1 1.2;stroke-dashoffset:.1;animation:run {period}s linear infinite}}"
        ".e{animation:fade .5s .1s backwards}"
    )
    body = (
        f'<defs>{grads}<clipPath id="c"><rect width="{W}" height="{H}" rx="12"/></clipPath></defs>'
        f'<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{P["ground"]}"/>'
        f'<text class="e" x="48" y="44" font-size="11" letter-spacing="2" fill="{P["faint"]}">STACK</text>'
        f"{rows}</g>"
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="11.5" stroke="{P["line"]}"/>'
    )
    text = "STACK nm0123456789" + "".join(b.upper() + t for b, t, _, _ in BANDS)
    return svg(W, H, text, css, body, "Stack: " + "; ".join(f"{b}: {t}" for b, t, _, _ in BANDS))


# ── B1 · Rozetler ──────────────────────────────────────────────────────────
# Simgeler 7×7 piksel; 2 px'lik hücre, 22 px'teki Departure Mono pikseline eşit.
ICONS = {
    "globe": ["..###..", ".#.#.#.", "#..#..#", "#######", "#..#..#", ".#.#.#.", "..###.."],
    "in":    [".......", "#.#....", ".......", "#.#.##.", "#.##..#", "#.#...#", "#.#...#"],
    "mail":  [".......", "#######", "##...##", "#.#.#.#", "#..#..#", "#.....#", "#######"],
}


def chip(P, label, icon, ci, title):
    color = P["lead"] if ci is None else P["acc"][ci]
    h, pad, cell = 44, 16, 2
    w = round(pad + 7 * cell + 12 + len(label) * 22 * ADV + pad)
    oy = (h - 7 * cell) // 2
    px = "".join(
        f'<rect x="{pad + c * cell}" y="{oy + r * cell}" width="{cell}" height="{cell}" fill="{color}" '
        f'style="animation:fade .2s {0.3 + (r + c) * 0.04:.2f}s backwards"/>'
        for r, row in enumerate(ICONS[icon]) for c, ch in enumerate(row) if ch == "#"
    )
    body = (
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="8" fill="{P["ground"]}" stroke="{P["line"]}"/>'
        f"{px}"
        f'<text x="{pad + 7 * cell + 12}" y="29" font-size="22" fill="{P["ink"]}">{label}</text>'
    )
    return svg(w, h, label, "", body, title)


def main():
    for mode, P in PALETTES.items():
        sfx = "" if mode == "dark" else "-light"
        files = {
            "header": header(P),
            "stack": stack(P),
            "link-site": chip(P, "oguzhd.com", "globe", None, "oguzhd.com"),
            "link-linkedin": chip(P, "linkedin", "in", 1, "LinkedIn"),
            "link-mail": chip(P, "e-mail", "mail", 0, "E-mail"),
        }
        for name, content in files.items():
            out = HERE / f"{name}{sfx}.svg"
            out.write_text(content, encoding="utf-8")
            print(f"{out.name:24} {len(content.encode()) / 1024:5.1f} KB")


if __name__ == "__main__":
    main()
