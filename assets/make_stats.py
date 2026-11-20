"""Generate the two stats cards for the profile README.

  assets/stats.svg  "match report": the GitHub year as a chess game, a made-up dev Elo,
                    languages as chess pieces, and a pawn that heckles the numbers
  assets/munch.svg  a googly-eyed pawn hops across the contribution calendar and eats
                    every active day

    pip install fonttools && GITHUB_TOKEN=... python assets/make_stats.py
    # or, with the gh CLI:  python -c "import sys; sys.path.insert(0,'assets'); import make_stats as m; print(m.QUERY)" > q.graphql
    #   gh api graphql -F query=@q.graphql -f login=dangnguyenducanh > s.json && STATS_JSON=s.json python assets/make_stats.py
Runs daily in .github/workflows/stats.yml. Data comes from the GitHub GraphQL API.
Fonts: Lato subsets in assets/fonts (SIL OFL 1.1); chess pieces are DejaVu Sans outlines.
"""
import base64
import datetime
import html
import io
import json
import os
import random
import urllib.request

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

LOGIN = os.environ.get("STATS_LOGIN", "dangnguyenducanh")
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
GOLD, CREAM, LAV, MUTED, INK = "#fcd34d", "#fff7ed", "#c7d2fe", "#a5b4fc", "#1e1b4b"
ROLES = ["queen: does everything", "rook: holds the walls", "bishop: comes in sideways",
         "knight: weird but works", "pawn: promotes someday"]

QUERY = """query($login: String!) { user(login: $login) {
  followers { totalCount }
  repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
    totalCount
    nodes { stargazerCount languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } } } }
  contributionsCollection { totalCommitContributions totalPullRequestContributions totalIssueContributions
    contributionCalendar { totalContributions weeks { contributionDays { date contributionCount contributionLevel } } } } } }"""


# --- data ----------------------------------------------------------------------------------
def fetch() -> dict:
    if os.environ.get("STATS_JSON"):  # local runs: a saved response from `gh api graphql -F query=@... -f login=...`
        with open(os.environ["STATS_JSON"], encoding="utf-8") as f:
            return json.load(f)["data"]["user"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json",
                 "User-Agent": "profile-stats-card"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors"):
        raise SystemExit(f"GraphQL errors: {body['errors']}")
    return body["data"]["user"]


def summarize(u: dict) -> dict:
    cal = u["contributionsCollection"]["contributionCalendar"]
    weeks = [sorted(w["contributionDays"], key=lambda d: d["date"]) for w in cal["weeks"]]
    days = [d for w in weeks for d in w]
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    sizes, colors = {}, {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            sizes[name] = sizes.get(name, 0) + e["size"]
            colors[name] = e["node"]["color"] or "#8b8b8b"
    total = sum(sizes.values()) or 1
    s = {
        "contribs": cal["totalContributions"],
        "commits": u["contributionsCollection"]["totalCommitContributions"],
        "prs": u["contributionsCollection"]["totalPullRequestContributions"],
        "issues": u["contributionsCollection"]["totalIssueContributions"],
        "repos": u["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "followers": u["followers"]["totalCount"],
        "active": sum(1 for d in days if d["contributionCount"]),
        "longest": longest,
        "weeks": weeks,
        "langs": [(n, 100 * b / total, colors[n]) for n, b in sorted(sizes.items(), key=lambda kv: -kv[1])[:5]],
    }
    # dev Elo: a deliberately made-up formula, labelled as such on the card
    s["elo"] = 800 + s["contribs"] + 2 * s["prs"] + 20 * s["stars"] + 3 * s["repos"] + 10 * s["followers"]
    s["title"] = next(t for limit, t in [(1000, "patzer"), (1200, "club player"), (1500, "cafe hustler"),
                                          (1800, "self-declared CM"), (2100, "FM energy"),
                                          (10 ** 9, "GM of git push")] if s["elo"] < limit)
    return s


# --- drawing helpers -------------------------------------------------------------------------
def font_face(weight: str, css_weight: int, text: str) -> str:
    font = TTFont(os.path.join(FONTS, f"Lato-{weight}-latin.ttf"), recalcTimestamp=False)
    sub = Subsetter(Options())
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:L;font-weight:{css_weight};src:url(data:font/ttf;base64,{b64}) format('truetype')}}"


_metrics: dict = {}


def text_width(text: str, size: float, weight: str = "Bold") -> float:
    if weight not in _metrics:
        f = TTFont(os.path.join(FONTS, f"Lato-{weight}-latin.ttf"))
        _metrics[weight] = (f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm)
    cmap, hmtx, upm = _metrics[weight]
    return sum(hmtx[cmap[ord(c)]][0] for c in text if ord(c) in cmap) * size / upm


with open(os.path.join(FONTS, "pieces.json"), encoding="utf-8") as _f:
    PIECES = json.load(_f)


def piece(ch: str, x: float, y: float, h: float, fill: str = GOLD) -> str:
    """Chess piece glyph, bottom-center at (x, y), h px tall."""
    p = PIECES[ch]
    x0, y0, x1, y1 = p["bounds"]
    k = h / (y1 - y0)
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({k:.5f},{-k:.5f}) translate({-(x0 + x1) / 2:.1f},{-y0:.1f})">'
            f'<path d="{p["d"]}" fill="{fill}"/></g>')


PAWN = ('<path d="M-40,0 Q-42,-16 -27,-20 L27,-20 Q42,-16 40,0 Z M-22,-20 Q-12,-40 -12,-58 L12,-58 Q12,-40 22,-20 Z" '
        'fill="url(#pf)" stroke="#1e1b4b" stroke-width="3.5" stroke-linejoin="round"/>'
        '<ellipse cx="0" cy="-60" rx="24" ry="6.5" fill="url(#pf)" stroke="#1e1b4b" stroke-width="3.5"/>'
        '<circle cx="0" cy="-88" r="27" fill="url(#pf)" stroke="#1e1b4b" stroke-width="3.5"/>'
        '<circle cx="-10" cy="-92" r="9.5" fill="#fff" stroke="#1e1b4b" stroke-width="2.4"/>'
        '<circle cx="11" cy="-92" r="9.5" fill="#fff" stroke="#1e1b4b" stroke-width="2.4"/>'
        '<circle cx="-7" cy="-90" r="4.6" fill="#111"/><circle cx="14" cy="-90" r="4.6" fill="#111"/>'
        '<ellipse cx="-17" cy="-77" rx="5.5" ry="3" fill="#f9a8d4" opacity=".85"/>'
        '<ellipse cx="18" cy="-77" rx="5.5" ry="3" fill="#f9a8d4" opacity=".85"/>'
        '<path d="M-5,-76 Q0.5,-70 6,-76" fill="none" stroke="#1e1b4b" stroke-width="2.6" stroke-linecap="round"/>')

DEFS = ('<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#060a22"/>'
        '<stop offset=".6" stop-color="#16195a"/><stop offset="1" stop-color="#2a1f63"/></linearGradient>'
        '<linearGradient id="pf" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff"/>'
        '<stop offset=".6" stop-color="#ede9fe"/><stop offset="1" stop-color="#b9b2ef"/></linearGradient>'
        '<pattern id="chk" width="48" height="48" patternUnits="userSpaceOnUse">'
        '<rect width="24" height="24" fill="#fff"/><rect x="24" y="24" width="24" height="24" fill="#fff"/></pattern>')

TWINKLE = "@keyframes tw{0%,100%{opacity:.2}50%{opacity:1}}.tw{animation:tw 3.2s ease-in-out infinite}"
REDUCED = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def stars_svg(w: int, h: int, n: int, seed: int) -> str:
    rng = random.Random(seed)
    return "".join(f'<circle class="tw" cx="{rng.uniform(0, w):.0f}" cy="{rng.uniform(4, h):.0f}" r="{rng.uniform(.6, 1.5):.1f}" '
                   f'fill="#fff" style="animation-delay:-{rng.uniform(0, 3):.1f}s"/>' for _ in range(n))


def plural(n: int, word: str) -> str:
    return f"{n:,} {word}{'' if n == 1 else 's'}"


def esc(s: str) -> str:
    return html.escape(s, quote=False)


# --- card 1: match report ----------------------------------------------------------------------
def stats_svg(s: dict) -> str:
    W, H = 900, 380
    cells = [("♟", s["contribs"], "moves played", "contributions"), ("♞", s["commits"], "commits pushed", "last 12 months"),
             ("♝", s["prs"], "gambits offered", "pull requests"), ("♜", s["repos"], "castles built", "public repos, all time"),
             ("♛", s["stars"], "crowns won", "stars, all time"), ("♚", s["longest"], "longest streak", "days in a row")]
    top_name, top_pct, _ = s["langs"][0] if s["langs"] else ("code", 0, "")
    quips = [
        f"{plural(s['contribs'], 'move')} in 12 months. The board is warming up.",
        "0 stars. Playing for the love of the game." if s["stars"] == 0 else f"{s['stars']} stars. The crowd goes mild.",
        f"{top_name} at {top_pct:.0f}%. Predictable opening. Solid, though." if s["langs"] else "No languages yet. A blank board. Thrilling.",
        f"{plural(s['issues'], 'issue')} filed. Reports his own blunders. Respect." if s["issues"] else "0 issues. Flawless, or nobody's looking.",
        f"Elo {s['elo']:,}? I made that formula up. Still counts.",
        "0 followers. Be the first, it's free." if s["followers"] == 0 else f"{plural(s['followers'], 'follower')}. Fan club growing.",
    ]
    n, step = len(quips), 3

    # languages as a 16x2 board: 32 squares split by share among the top 5 (each gets at least one)
    raw = [32 * p / (sum(p for _, p, _ in s["langs"]) or 1) for _, p, _ in s["langs"]]
    counts = [max(1, int(r)) for r in raw]
    while raw and sum(counts) < 32:
        counts[max(range(len(raw)), key=lambda i: raw[i] - counts[i])] += 1
    while sum(counts) > 32:
        counts[counts.index(max(counts))] -= 1
    fills = [c for (_, _, c), k in zip(s["langs"], counts) for _ in range(k)]
    sq, bx, by = 18, 576, 214
    board = "".join(
        f'<rect x="{bx + (i % 16) * sq}" y="{by + (i // 16) * sq}" width="{sq}" height="{sq}" fill="{f}"/>'
        + (f'<rect x="{bx + (i % 16) * sq}" y="{by + (i // 16) * sq}" width="{sq}" height="{sq}" fill="#000" opacity=".22"/>'
           if (i % 16 + i // 16) % 2 else "")
        for i, f in enumerate(fills))
    legend = "".join(
        f'<rect x="{bx}" y="{262 + i * 21}" width="10" height="10" rx="2" fill="{c}"/>'
        f'<text x="{bx + 18}" y="{271 + i * 21}" class="sm"><tspan fill="{CREAM}">{esc(name)} {pct:.1f}%</tspan>'
        + (f'<tspan fill="{MUTED}"> · {esc(ROLES[i])}</tspan>' if text_width(f"{name} {pct:.1f}% · {ROLES[i]}", 12) < 280 else "")
        + '</text>'
        for i, (name, pct, c) in enumerate(s["langs"]))

    pieces_block = (f'<text x="576" y="204" class="k">THE PIECES</text>{board}'
                    f'<rect x="{bx}" y="{by}" width="{16 * sq}" height="{2 * sq}" fill="none" stroke="{GOLD}" stroke-opacity=".6"/>{legend}'
                    if s["langs"] else "")
    grid = []
    for i, (ch, val, label, sub) in enumerate(cells):
        x, y = 40 + (i % 3) * 170, 104 + (i // 3) * 82
        grid.append(f'{piece(ch, x + 13, y + 34, 30)}'
                    f'<text x="{x + 36}" y="{y + 30}" class="val">{val:,}</text>'
                    f'<text x="{x + 36}" y="{y + 50}" class="lbl">{esc(label)}</text>'
                    f'<text x="{x + 36}" y="{y + 66}" class="sub">{esc(sub)}</text>')

    # speech bubble next to the pawn, sized to the longest quip
    qsize = 14.0
    bw = max(text_width(q, qsize) for q in quips) + 32
    if bw > 440:  # shrink long quips instead of running into the languages column
        qsize, bw = qsize * 408 / (bw - 32), 440
    bx0, by0, bh = 124, 292, 34
    bubble = (f'<path d="M{bx0 + 12},{by0} h{bw - 24:.0f} a12,12 0 0 1 12,12 v{bh - 24} a12,12 0 0 1 -12,12 '
              f'h-{bw - 24:.0f} a12,12 0 0 1 -12,-12 v-2 l-12,4 l12,-14 v{36 - bh} a12,12 0 0 1 12,-12 Z" '
              f'fill="#fff" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>')
    msgs = "".join(f'<text class="q" x="{bx0 + bw / 2:.0f}" y="{by0 + 22}" text-anchor="middle" font-size="{qsize:.1f}" '
                   f'style="animation-delay:{i * step}s">{esc(q)}</text>' for i, q in enumerate(quips))
    elo_title = f"dev Elo · {s['title']}"
    ew = text_width(elo_title.upper(), 12) + 3 * len(elo_title)
    elo_fit = ' textLength="266" lengthAdjust="spacingAndGlyphs"' if ew > 266 else ""
    text_all = ("MATCH REPORT · LAST 12 MONTHS" + f"{LOGIN} vs. the year" + "".join(l + u for _, _, l, u in cells)
                + "".join(quips) + elo_title.upper() + "(formula entirely made up)THE PIECES" + "".join(ROLES)
                + "".join(n for n, _, _ in s["langs"]) + "0123456789,.% ·")
    css = (font_face("Black", 900, text_all) + font_face("Bold", 700, text_all) + font_face("Regular", 400, text_all)
           + "text{font-family:L,Lato,'Segoe UI',sans-serif}"
           + f".k{{font-weight:700;font-size:12px;letter-spacing:3px;fill:{GOLD}}}"
           + f".val{{font-weight:900;font-size:30px;fill:{CREAM}}}.lbl{{font-weight:700;font-size:13px;fill:{LAV}}}"
           + f".sub{{font-weight:400;font-size:11.5px;fill:{MUTED}}}.sm{{font-weight:700;font-size:12px}}"
           + f".q{{font-weight:700;font-size:14px;fill:{INK};opacity:0;animation:q {n * step}s step-end infinite}}"
           + f"@keyframes q{{0%{{opacity:1}}{100 / n:.3f}%,100%{{opacity:0}}}}"
           + "@keyframes bob{0%,80%,100%{transform:none}86%{transform:translateY(-22px)}93%{transform:scale(1.06,.92)}}"
           + ".bob{animation:bob 3s ease-in-out infinite;transform-origin:0 0}"
           + TWINKLE + REDUCED + "@media (prefers-reduced-motion:reduce){.q:first-of-type{opacity:1}}")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Match report for {LOGIN}: {s['contribs']} contributions, {s['commits']} commits, {s['prs']} pull requests, {s['repos']} public repos, {s['stars']} stars, longest streak {s['longest']} days. Top language {esc(top_name)}.">
<title>Match report</title><style>{css}</style><defs>{DEFS}</defs>
<rect width="{W}" height="{H}" rx="22" fill="url(#bg)"/>
<rect width="{W}" height="{H}" rx="22" fill="url(#chk)" opacity=".035"/>
{stars_svg(W, 90, 40, 3)}
<text x="40" y="44" class="k">MATCH REPORT · LAST 12 MONTHS</text>
<text x="40" y="76" font-weight="900" font-size="26" fill="{CREAM}">{esc(LOGIN)} <tspan fill="{GOLD}">vs.</tspan> the year</text>
{''.join(grid)}
<rect x="556" y="96" width="306" height="84" rx="14" fill="#0b0f2e" fill-opacity=".7" stroke="#fff" stroke-opacity=".14"/>
<text x="576" y="120" class="k"{elo_fit}>{esc(elo_title.upper())}</text>
<text x="576" y="160" font-weight="900" font-size="34" fill="{GOLD}">{s['elo']:,}</text>
<text x="{576 + text_width(f"{s['elo']:,}", 34, 'Black') + 12:.0f}" y="158" class="sub">(formula entirely made up)</text>
{pieces_block}
<g transform="translate(78,358) scale(.5)"><g class="bob">{PAWN}</g></g>
{bubble}
<g>{msgs}</g>
</svg>
"""


# --- card 2: the pawn eats the contribution graph ------------------------------------------------
def munch_svg(s: dict) -> str:
    W, H, cell, gap = 900, 206, 13, 3
    step = cell + gap
    weeks = s["weeks"]
    x0, y0 = (W - len(weeks) * step + gap) / 2, 74
    level = {"FIRST_QUARTILE": "#6d5fd3", "SECOND_QUARTILE": "#9d8ff0", "THIRD_QUARTILE": "#f5c451", "FOURTH_QUARTILE": "#fde68a"}
    base, food = [], []
    for c, week in enumerate(weeks):
        # snake through the board: down one week, up the next
        for d in (week if c % 2 == 0 else reversed(week)):
            r = (datetime.date.fromisoformat(d["date"]).weekday() + 1) % 7  # GitHub rows start on Sunday
            x, y = x0 + c * step, y0 + r * step
            base.append(f'<rect x="{x:.0f}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{"#221d63" if (c + r) % 2 else "#1a1752"}"/>')
            if d["contributionCount"]:
                food.append((x, y, level.get(d["contributionLevel"], "#6d5fd3")))
    hop, rest = 0.42, 3.2
    T = (len(food) + 1) * hop + rest
    px, py = x0 - 12, y0 + 3.5 * step
    frames = [f"0%{{transform:translate({px:.1f}px,{py:.1f}px)}}"]
    squares, eat = [], []
    for k, (x, y, color) in enumerate(food):
        cx, cy = x + cell / 2, y + cell / 2
        land, mid = (k + 1) * hop / T * 100, (k + .5) * hop / T * 100
        frames.append(f"{mid:.3f}%{{transform:translate({(px + cx) / 2:.1f}px,{min(py, cy) - 12:.1f}px)}}")
        frames.append(f"{land:.3f}%{{transform:translate({cx:.1f}px,{cy:.1f}px)}}")
        squares.append(f'<rect class="f" x="{x:.0f}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{color}" style="animation-name:e{k}"/>')
        eat.append(f"@keyframes e{k}{{0%{{opacity:1}}{land:.3f}%,100%{{opacity:0}}}}")
        px, py = cx, cy
    frames.append(f"100%{{transform:translate({px:.1f}px,{py:.1f}px)}}")
    burp_at = (len(food) + .6) * hop / T * 100
    title = "the pawn eats my contribution graph"
    stats = (f"{plural(s['contribs'], 'contribution')} · {plural(s['active'], 'active day')} · "
             f"longest streak {plural(s['longest'], 'day')}")
    text_all = title + stats + "burp. all gone." + "0123456789·"
    css = (font_face("Black", 900, text_all) + font_face("Bold", 700, text_all)
           + "text{font-family:L,Lato,'Segoe UI',sans-serif}"
           + f".f{{animation-duration:{T:.2f}s;animation-timing-function:step-end;animation-iteration-count:infinite}}"
           + "".join(eat)
           + f".walk{{transform:translate({x0 - 12:.1f}px,{y0 + 3.5 * step:.1f}px);animation:walk {T:.2f}s ease-in-out infinite}}"
           + f"@keyframes walk{{{''.join(frames)}}}"
           + f".burp{{opacity:0;animation:burp {T:.2f}s step-end infinite}}"
           + f"@keyframes burp{{0%{{opacity:0}}{burp_at:.3f}%{{opacity:1}}}}"
           + TWINKLE + REDUCED)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Animated: a googly-eyed pawn hops across {LOGIN}'s contribution calendar and eats all {s['active']} active days ({s['contribs']} contributions).">
<title>The pawn eats my contribution graph</title><style>{css}</style><defs>{DEFS}</defs>
<rect width="{W}" height="{H}" rx="22" fill="url(#bg)"/>
{stars_svg(W, 54, 24, 5)}
{piece("♟", 50, 48, 24)}
<text x="70" y="44" font-weight="900" font-size="19" fill="{CREAM}">{esc(title)}</text>
<text x="{W - 40}" y="44" text-anchor="end" font-weight="700" font-size="12.5" fill="{MUTED}">{esc(stats)}</text>
{''.join(base)}
{''.join(squares)}
<g class="walk"><g transform="translate(0,6) scale(.22)">{PAWN}</g>
<g class="burp" transform="translate({0 if px > 130 else 128},0)"><rect x="-114" y="-46" width="100" height="24" rx="8" fill="#fff" stroke="{INK}" stroke-width="2"/>
<text x="-64" y="-29" text-anchor="middle" font-weight="900" font-size="12" fill="{INK}">burp. all gone.</text></g></g>
</svg>
"""


def main() -> None:
    s = summarize(fetch())
    for name, svg in (("stats.svg", stats_svg(s)), ("munch.svg", munch_svg(s))):
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"wrote assets/{name} ({len(svg) / 1024:.0f} KB)")
    print({k: v for k, v in s.items() if k != "weeks"})


if __name__ == "__main__":
    main()
