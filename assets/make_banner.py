"""Generate assets/banner.svg: animated profile banner.

Night sky over an endless chessboard; a googly-eyed pawn (the "agent") bounces and talks,
a knight hops in L-moves, stars twinkle. Pure SVG + CSS keyframes, fonts embedded as
subsets, so it renders inside GitHub's <img> sandbox (no external requests).

    pip install fonttools && python assets/make_banner.py
Fonts: Lato (SIL OFL) for text; the knight is DejaVu Sans' U+265E outline.
"""
import base64
import html
import io
import os
import random

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

W, H = 1200, 540
HORIZON, CX, F = 345, 860, 600  # board perspective: vanishing point (CX, HORIZON), focal F
LATO = "/usr/share/fonts/truetype/lato/Lato-{}.ttf"
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

TAGLINE = "CHESS PLAYER  ·  NOW AI ENGINEER"
HELLO = "Hello, I'm"
NAME1, NAME2 = "DANG NGUYEN", "DUC ANH"
LABEL = "A.K.A. HARRY WILSON  ·  NOW PLAYING AS"
ROLES = ["AI Engineer", "Multi-agent builder", "RAG & Text2SQL wrangler", "HNSW-from-scratch nerd"]
PILL_A, PILL_B = "now", "  ·  AI Engineer @ RIPT  ·  UI2Code research w/ Uni Luxembourg"
BUBBLE = ["thinking…", "calling tools…", "retrieving…", "checkmate!"]
GOLD, CREAM, LAV = "#fcd34d", "#fff7ed", "#c7d2fe"


# --- fonts -------------------------------------------------------------------
def subset(path, text):
    font = TTFont(path)
    s = Subsetter(Options())
    s.populate(text=text)
    s.subset(font)
    return font


def font_face(family, weight, font):
    buf = io.BytesIO()
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return (f"@font-face{{font-family:{family};font-weight:{weight};"
            f"src:url(data:font/ttf;base64,{b64}) format('truetype');}}")


def width(font, text, size):
    """Advance width in px (no kerning; close enough for layout)."""
    cmap, hmtx, upm = font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm
    return sum(hmtx[cmap[ord(c)]][0] for c in text) * size / upm


# --- geometry ----------------------------------------------------------------
def proj(x, z):
    return CX + F * x / z, HORIZON + F / z


def board():
    polys = []
    z, row = 2.4, 0
    while F / z - F / (z + 1) > 1.2:  # stop once rows are thinner than ~1px
        for i in range(-40, 40):
            if (i + row) % 2:
                continue
            pts = [proj(i, z), proj(i + 1, z), proj(i + 1, z + 1), proj(i, z + 1)]
            xs = [p[0] for p in pts]
            if max(xs) < 0 or min(xs) > W:
                continue
            polys.append(" ".join(f"{x:.1f},{y:.1f}" for x, y in pts))
        z, row = z + 1, row + 1
    return "".join(f'<polygon points="{p}"/>' for p in polys)


def knight_path(height):
    f = TTFont(DEJAVU)
    gs = f.getGlyphSet()
    g = gs[f.getBestCmap()[0x265E]]
    bp = BoundsPen(gs)
    g.draw(bp)
    x0, y0, x1, y1 = bp.bounds
    pen = SVGPathPen(gs)
    g.draw(pen)
    k = height / (y1 - y0)
    return pen.getCommands(), f"scale({k:.5f},{-k:.5f}) translate({-(x0 + x1) / 2:.1f},{-y0:.1f})"


def sparkle(r):
    a = r * 0.22
    return f"M0,{-r} L{a},{-a} L{r},0 L{a},{a} L0,{r} L{-a},{a} L{-r},0 L{-a},{-a} Z"


# --- animation keyframes ------------------------------------------------------
KNIGHT = [(1.5, 6.5), (3.5, 7.5), (2.5, 9.5), (0.5, 8.5)]  # 4 L-moves that close a loop
PAWN = (-0.5, 4.5)
ZREF = 6.5


def knight_keyframes():
    """8s loop: knight holds on square i for 17.5% then hops to square i+1 by 25%."""
    pos = []
    for x, z in KNIGHT:
        sx, sy = proj(x, z)
        pos.append(f"translate({sx:.1f}px,{sy:.1f}px) scale({ZREF / z:.3f})")
    move, hop = [], []
    for i in range(4):
        t = i * 25
        move.append(f"{t}%,{t + 17.5}%{{transform:{pos[i]}}}")
        hop.append(f"{t}%,{t + 17.5}%{{transform:translateY(0)}} {t + 21.25}%{{transform:translateY(-38px)}}")
    move.append(f"100%{{transform:{pos[0]}}}")
    hop.append("100%{transform:translateY(0)}")

    # the pawn's pupils turn toward the square the knight is landing on
    px, _ = proj(*PAWN)

    def gaze(k):
        dx = max(-3.5, min(3.5, (proj(*KNIGHT[k])[0] - px) / 50))
        return f"{{transform:translate({dx:.1f}px,-2.5px)}}"

    look = [f"0%,17.5%{gaze(0)}"]
    for i in range(4):
        t = i * 25
        end = f"{t + 42.5}%" if i < 3 else "100%"
        look.append(f"{t + 22}%,{end}{gaze((i + 1) % 4)}")
    return ("@keyframes kmove{" + " ".join(move) + "}\n@keyframes khop{" + " ".join(hop) + "}\n"
            "@keyframes look{" + " ".join(look) + "}")


def main():
    rng = random.Random(7)
    black = subset(LATO.format("Black"), NAME1 + NAME2 + "".join(ROLES))
    bold = subset(LATO.format("Bold"), TAGLINE + LABEL + PILL_A + PILL_B + "".join(BUBBLE))
    regular = subset(LATO.format("Regular"), HELLO)
    kpath, ktf = knight_path(118)

    stars = "".join(
        f'<circle class="tw" cx="{rng.uniform(0, W):.0f}" cy="{rng.uniform(8, HORIZON - 30):.0f}" '
        f'r="{rng.uniform(0.7, 1.8):.1f}" style="animation-delay:-{rng.uniform(0, 4):.1f}s"/>'
        for _ in range(70))
    sparkles = "".join(
        f'<g transform="translate({x},{y})"><path class="tw" d="{sparkle(r)}" '
        f'style="animation-delay:-{d}s"/></g>'
        for x, y, r, d in [(640, 60, 7, 0.4), (760, 150, 5, 1.6), (980, 210, 6, 2.4),
                           (560, 205, 4, 0.9), (1160, 230, 5, 3.1), (880, 52, 4, 2.0)])

    name2_w = width(black, NAME2, 84)
    pill_w = width(bold, PILL_A + PILL_B, 15) + 76
    px, py = proj(*PAWN)
    k0x, k0y = proj(*KNIGHT[0])

    # speech bubble: one message per knight hop (2s each), synced with the 8s knight loop
    bubble = "".join(
        f'<text class="msg m{i}" x="-92" y="-149" text-anchor="middle" '
        f'style="animation-delay:{i * 2}s">{html.escape(m)}</text>' for i, m in enumerate(BUBBLE))
    roles = "".join(
        f'<text class="role r{i}" x="72" y="395" style="animation-delay:{1.2 + i * 3}s">{html.escape(r)}</text>'
        for i, r in enumerate(ROLES))

    css = f"""
{font_face('LB', 900, black)}
{font_face('LB', 700, bold)}
{font_face('LB', 400, regular)}
text{{font-family:LB,Lato,'Segoe UI',system-ui,sans-serif}}
.tw{{fill:#fff;animation:tw 3.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes tw{{0%,100%{{opacity:.25;transform:scale(.6)}}50%{{opacity:1;transform:scale(1.15)}}}}
.fade{{opacity:0;animation:fade .9s ease-out forwards}}
@keyframes fade{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
.role{{opacity:0;fill:{GOLD};font-weight:900;font-size:30px;animation:flip 12s cubic-bezier(.2,.8,.2,1) infinite}}
@keyframes flip{{0%{{opacity:0;transform:translateY(22px)}}4%,21%{{opacity:1;transform:none}}25%,100%{{opacity:0;transform:translateY(-18px)}}}}
.msg{{opacity:0;font-weight:700;font-size:15px;fill:#1e1b4b;animation:msg 8s step-end infinite}}
@keyframes msg{{0%{{opacity:1}}25%,100%{{opacity:0}}}}
.kmove{{animation:kmove 8s ease-in-out infinite}}
.khop{{animation:khop 8s ease-in-out infinite}}
.look{{animation:look 8s ease-in-out infinite}}
{knight_keyframes()}
.bob{{animation:bob 2s ease-in-out infinite}}
@keyframes bob{{0%,78%,100%{{transform:none}}84%{{transform:translateY(-20px) scale(.96,1.05)}}91%{{transform:scale(1.08,.9)}}95%{{transform:none}}}}
.shadow{{animation:shadow 2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes shadow{{0%,78%,100%{{transform:none;opacity:.45}}84%{{transform:scale(.7);opacity:.25}}}}
.blink{{animation:blink 4.3s infinite;transform-box:fill-box;transform-origin:center}}
@keyframes blink{{0%,93%,100%{{transform:none}}96%{{transform:scaleY(.1)}}}}
.shoot{{opacity:0;animation:shoot 9s ease-in 2s infinite}}
@keyframes shoot{{0%{{opacity:0;transform:translate(330px,40px)}}2%{{opacity:1}}10%{{opacity:0;transform:translate(640px,150px)}}100%{{opacity:0;transform:translate(640px,150px)}}}}
.moon{{animation:glow 5s ease-in-out infinite}}
@keyframes glow{{50%{{opacity:.55}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.fade,.r0,.m0{{opacity:1}}.kmove{{transform:translate({k0x:.1f}px,{k0y:.1f}px)}}}}
"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Dang Nguyen Duc Anh (Harry Wilson): chess player turned AI Engineer building multi-agent systems, RAG and Text2SQL agents. Now: AI Engineer at RIPT, UI2Code research with the University of Luxembourg.">
<title>Dang Nguyen Duc Anh</title>
<style>{css}</style>
<defs>
<clipPath id="card"><rect width="{W}" height="{H}" rx="26"/></clipPath>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#060a22"/><stop offset=".45" stop-color="#16195a"/>
<stop offset=".64" stop-color="#4b2a82"/><stop offset=".7" stop-color="#8b3f8f"/></linearGradient>
<linearGradient id="fog" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#7a3d8e"/><stop offset=".35" stop-color="#3a2873" stop-opacity=".75"/>
<stop offset="1" stop-color="#1a1650" stop-opacity="0"/></linearGradient>
<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#060a22" stop-opacity=".82"/><stop offset=".55" stop-color="#060a22" stop-opacity="0"/></linearGradient>
<radialGradient id="halo"><stop offset="0" stop-color="#fde68a" stop-opacity=".45"/><stop offset="1" stop-color="#fde68a" stop-opacity="0"/></radialGradient>
<linearGradient id="pawn" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#ffffff"/><stop offset=".6" stop-color="#ede9fe"/><stop offset="1" stop-color="#b9b2ef"/></linearGradient>
<linearGradient id="trail" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>
<mask id="crescent"><circle cx="1098" cy="92" r="34" fill="#fff"/><circle cx="1113" cy="82" r="30" fill="#000"/></mask>
<filter id="ts" x="-10%" y="-30%" width="120%" height="160%"><feDropShadow dx="0" dy="2" stdDeviation="5" flood-color="#050816" flood-opacity=".9"/></filter>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<circle class="moon" cx="1098" cy="92" r="95" fill="url(#halo)"/>
<circle cx="1098" cy="92" r="34" fill="#fef3c7" mask="url(#crescent)"/>
{stars}
<g fill="{GOLD}">{sparkles}</g>
<g class="shoot"><line x1="-120" y1="-42" x2="0" y2="0" stroke="url(#trail)" stroke-width="2.2" stroke-linecap="round"/></g>
<rect y="{HORIZON}" width="{W}" height="{H - HORIZON}" fill="#1a1650"/>
<g fill="#7468d6" fill-opacity=".5">{board()}</g>
<rect y="{HORIZON}" width="{W}" height="120" fill="url(#fog)"/>
<rect y="{HORIZON - 1}" width="{W}" height="2" fill="#f9a8d4" opacity=".55"/>
<rect width="{W}" height="{H}" fill="url(#fade)"/>

<g class="kmove"><ellipse cx="0" cy="2" rx="38" ry="8" fill="#050816" opacity=".45"/>
<g class="khop"><g transform="{ktf}"><path d="{kpath}" fill="#120f3a" stroke="{GOLD}" stroke-width="2.2" vector-effect="non-scaling-stroke"/></g>
<g class="blink"><circle cx="-14" cy="-86" r="7.5" fill="#fff" stroke="#120f3a" stroke-width="2"/></g><circle class="look" cx="-14" cy="-86" r="3.6" fill="#111"/></g></g>

<g transform="translate({px:.1f},{py:.1f})">
<ellipse class="shadow" cx="0" cy="2" rx="42" ry="9" fill="#050816"/>
<g class="bob">
<path d="M-40,0 Q-42,-16 -27,-20 L27,-20 Q42,-16 40,0 Z M-22,-20 Q-12,-40 -12,-58 L12,-58 Q12,-40 22,-20 Z" fill="url(#pawn)" stroke="#1e1b4b" stroke-width="3" stroke-linejoin="round"/>
<ellipse cx="0" cy="-60" rx="24" ry="6.5" fill="url(#pawn)" stroke="#1e1b4b" stroke-width="3"/>
<circle cx="0" cy="-88" r="27" fill="url(#pawn)" stroke="#1e1b4b" stroke-width="3"/>
<g class="blink"><circle cx="-10" cy="-92" r="9.5" fill="#fff" stroke="#1e1b4b" stroke-width="2.2"/><circle cx="11" cy="-92" r="9.5" fill="#fff" stroke="#1e1b4b" stroke-width="2.2"/></g>
<g class="look"><circle cx="-10" cy="-92" r="4.6" fill="#111"/><circle cx="11" cy="-92" r="4.6" fill="#111"/></g>
<ellipse cx="-17" cy="-77" rx="5.5" ry="3" fill="#f9a8d4" opacity=".8"/><ellipse cx="18" cy="-77" rx="5.5" ry="3" fill="#f9a8d4" opacity=".8"/>
<path d="M-5,-76 Q0.5,-70 6,-76" fill="none" stroke="#1e1b4b" stroke-width="2.4" stroke-linecap="round"/>
<path d="M-170,-176 h156 a12,12 0 0 1 12,12 v20 a12,12 0 0 1 -12,12 h-30 l10,14 l-24,-14 h-112 a12,12 0 0 1 -12,-12 v-20 a12,12 0 0 1 12,-12 Z" fill="#fff" stroke="#1e1b4b" stroke-width="2.4" stroke-linejoin="round"/>
{bubble}
</g></g>

<g filter="url(#ts)">
<g class="fade" style="animation-delay:.1s"><path d="{sparkle(6)}" transform="translate(78,86)" fill="{GOLD}"/>
<text x="94" y="91" fill="{GOLD}" font-weight="700" font-size="14" letter-spacing="4">{TAGLINE}</text></g>
<text class="fade" style="animation-delay:.25s" x="72" y="150" fill="{LAV}" font-weight="400" font-size="32">{HELLO}</text>
<text class="fade" style="animation-delay:.4s" x="70" y="236" fill="{CREAM}" font-weight="900" font-size="84" letter-spacing="1">{NAME1}</text>
<g class="fade" style="animation-delay:.55s"><text x="70" y="318" fill="{CREAM}" font-weight="900" font-size="84" letter-spacing="1">{NAME2}</text>
<circle cx="{70 + name2_w + 22:.0f}" cy="308" r="9" fill="{GOLD}"/></g>
<text class="fade" style="animation-delay:.8s" x="72" y="356" fill="#a5b4fc" font-weight="700" font-size="13" letter-spacing="3">{LABEL}</text>
{roles}
<g transform="translate(72,428)"><g class="fade" style="animation-delay:1s">
<rect width="{pill_w:.0f}" height="42" rx="21" fill="#0b0f2e" fill-opacity=".72" stroke="#fff" stroke-opacity=".28"/>
<g transform="translate(25,30) scale(.2)" fill="{GOLD}"><path d="M-40,0 Q-42,-16 -27,-20 L27,-20 Q42,-16 40,0 Z M-22,-20 Q-12,-40 -12,-58 L12,-58 Q12,-40 22,-20 Z"/><ellipse cx="0" cy="-60" rx="24" ry="6.5"/><circle cx="0" cy="-88" r="27"/></g>
<text x="46" y="26.5" font-weight="700" font-size="15" fill="#e0e7ff"><tspan fill="{GOLD}">{PILL_A}</tspan>{PILL_B}</text></g></g>
</g>
</g>
</svg>
"""
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banner.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {out} ({len(svg) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
