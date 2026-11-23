"""Static profile cards in the same night-chessboard style as the stats cards.

  assets/work.svg        "current position": what I work on
  assets/proj-*.svg      one clickable card per featured project
  assets/stack.svg       "the army": the tech stack, ranked like chess pieces

    pip install fonttools && python assets/make_cards.py
The content lives in this file: edit it and re-run. It doesn't change daily, so the stats Action skips it.
Brand logos: Simple Icons paths (CC0) in assets/fonts/brands.json; the brands are trademarks of their owners.
"""
import html
import json
import os

from make_stats import (CREAM, DEFS, FONTS, GOLD, HERE, INK, LAV, MUTED, PAWN, REDUCED, TWINKLE, esc, font_face,
                        piece, stars_svg, text_width)

with open(os.path.join(FONTS, "brands.json"), encoding="utf-8") as _f:
    BRANDS = json.load(_f)
WEIGHT = {"Black": 900, "Bold": 700, "Regular": 400}
BLACK_PIECE = "#120f3a"


class Card:
    """Collects SVG parts, CSS and every rendered string (for font subsetting)."""

    def __init__(self, w: int, h: int, title: str, label: str, seed: int = 1):
        self.w, self.h, self.title, self.label, self.seed = w, h, title, label, seed
        self.parts: list[str] = []
        self.css: list[str] = []
        self.text: list[str] = []

    def t(self, s: str) -> str:
        self.text.append(s)
        return esc(s)

    def add(self, *svg: str) -> None:
        self.parts.extend(svg)

    def text_block(self, x: float, y: float, s: str, width: float, size: float, weight: str = "Bold",
                   fill: str = CREAM, lh: float | None = None) -> float:
        """Word-wrapped text; returns the height used."""
        words, rows, cur = s.split(), [], ""
        for w in words:
            cand = f"{cur} {w}".strip()
            if cur and text_width(cand, size, weight) > width:
                rows.append(cur)
                cur = w
            else:
                cur = cand
        rows += [cur] if cur else []
        lh = lh or size * 1.36
        spans = "".join(f'<tspan x="{x:.0f}" dy="{0 if i == 0 else lh:.1f}">{self.t(r)}</tspan>' for i, r in enumerate(rows))
        self.add(f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}" font-weight="{WEIGHT[weight]}" fill="{fill}">{spans}</text>')
        return len(rows) * lh

    def header(self, kicker: str, title: str, x: int = 40, size: int = 24, width: float = 0) -> None:
        self.add(f'<text x="{x}" y="44" class="k">{self.t(kicker)}</text>')
        width = width or self.w - 2 * x
        while size > 16 and text_width(title, size, "Black") > width:
            size -= 1
        self.add(f'<text x="{x}" y="76" font-size="{size}" font-weight="900" fill="{CREAM}">{self.t(title)}</text>')

    def heckler(self, x: float, y: float, quips: list[str], max_w: float, size: float = 13.5, step: int = 3) -> None:
        """Googly pawn (base at x, y) with a speech bubble that cycles through quips."""
        qsize = size
        bw = max(text_width(q, qsize) for q in quips) + 30
        if bw > max_w:
            qsize, bw = qsize * (max_w - 30) / (bw - 30), max_w
        bx0, bh = x + 40, 32
        by0 = y - 58
        n = len(quips)
        self.add(f'<g transform="translate({x:.0f},{y:.0f}) scale(.44)"><g class="bob">{PAWN}</g></g>',
                 f'<path d="M{bx0 + 12},{by0} h{bw - 24:.0f} a12,12 0 0 1 12,12 v{bh - 24} a12,12 0 0 1 -12,12 '
                 f'h-{bw - 24:.0f} a12,12 0 0 1 -12,-12 v-2 l-12,4 l12,-14 v{36 - bh} a12,12 0 0 1 12,-12 Z" '
                 f'fill="#fff" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>',
                 "<g>" + "".join(f'<text class="q" x="{bx0 + bw / 2:.0f}" y="{by0 + 21}" text-anchor="middle" '
                                 f'font-size="{qsize:.1f}" style="animation-delay:{i * step}s">{self.t(q)}</text>'
                                 for i, q in enumerate(quips)) + "</g>")
        self.css.append(f".q{{font-weight:700;fill:{INK};opacity:0;animation:q {n * step}s step-end infinite}}"
                        f"@keyframes q{{0%{{opacity:1}}{100 / n:.3f}%,100%{{opacity:0}}}}"
                        "@media (prefers-reduced-motion:reduce){.q:first-of-type{opacity:1}}")

    def render(self) -> str:
        txt = "".join(self.text) + "0123456789"
        css = (font_face("Black", 900, txt) + font_face("Bold", 700, txt) + font_face("Regular", 400, txt)
               + "text{font-family:L,Lato,'Segoe UI',sans-serif}"
               + f".k{{font-weight:700;font-size:12px;letter-spacing:3px;fill:{GOLD}}}"
               + "@keyframes bob{0%,80%,100%{transform:none}86%{transform:translateY(-20px)}93%{transform:scale(1.06,.92)}}"
               + ".bob{animation:bob 3.4s ease-in-out infinite}"
               + "".join(self.css) + TWINKLE + REDUCED)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
                f'role="img" aria-label="{html.escape(self.label)}"><title>{esc(self.title)}</title>'
                f"<style>{css}</style><defs>{DEFS}</defs>"
                f'<rect width="{self.w}" height="{self.h}" rx="22" fill="url(#bg)"/>'
                f'<rect width="{self.w}" height="{self.h}" rx="22" fill="url(#chk)" opacity=".035"/>'
                f"{stars_svg(self.w, 70, self.w // 22, self.seed)}" + "\n".join(self.parts) + "</svg>\n")


def panel(x: float, y: float, w: float, h: float) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#0b0f2e" fill-opacity=".6" stroke="#fff" stroke-opacity=".12"/>'


# --- work: current position ---------------------------------------------------------------------------
def work_svg() -> str:
    c = Card(900, 436, "What I work on",
             "What I work on. AI Engineer at the Research Institute of Posts and Telecommunications since March 2025: "
             "multi-agent systems (LangGraph pipelines, 110+ chatbots in production), retrieval and search on Qdrant and "
             "FastAPI, and model distillation into local open-weights models. Undergraduate researcher with the University "
             "of Luxembourg since March 2026: multi-step agents that turn UI designs into working HTML/CSS/JavaScript.", seed=12)
    c.header("WHAT I WORK ON · CURRENT POSITION", "Two boards, one player.")
    c.add(panel(28, 96, 562, 248), panel(604, 96, 268, 248))
    c.add(piece("♚", 58, 140, 30, white=True),
          f'<text x="82" y="124" font-size="19" font-weight="900" fill="{CREAM}">{c.t("AI Engineer")}</text>')
    c.text_block(82, 142, "Research Institute of Posts and Telecommunications · Mar 2025 – present", 490, 12, "Regular", MUTED)
    y = 178
    for ch, label, desc in [
        ("♞", "Multi-agent systems", "LangGraph pipelines with parallel steps, fallbacks and real-time streaming. 110+ chatbots in production."),
        ("♝", "Retrieval & search", "Vector and keyword search services on Qdrant and FastAPI, profiled and tuned for low latency."),
        ("♛", "Model distillation", "Fine-tuning local open-weights models on production chats to replace paid cloud-LLM calls."),
    ]:
        c.add(piece(ch, 58, y + 4, 20))
        c.add(f'<text x="82" y="{y}" font-size="13.5" font-weight="700" fill="{CREAM}">{c.t(label)}</text>')
        y += 17 + c.text_block(82, y + 17, desc, 490, 12.5, "Regular", LAV, lh=16) + 10
    c.add(piece("♜", 632, 138, 28, white=True))
    h = c.text_block(656, 122, "Undergraduate Researcher", 200, 15.5, "Black", CREAM)
    h += c.text_block(656, 124 + h, "University of Luxembourg · Mar 2026 – present", 200, 12, "Regular", MUTED)
    y = 140 + h + 12
    c.add(piece("♝", 632, y + 4, 20),
          f'<text x="656" y="{y}" font-size="13.5" font-weight="700" fill="{CREAM}">{c.t("UI2Code agents")}</text>')
    c.text_block(656, y + 17, "Multi-step agents that turn UI designs into working HTML/CSS/JS: refinement loops, "
                 "visual feedback, stopping policies.", 196, 12.5, "Regular", LAV, lh=16)
    c.heckler(58, 418, ["110+ bots in production. Zero of them play chess. Yet.",
                        "Distilled a cloud LLM into a local one. The API bill felt that.",
                        "Agents that write UI code. Pixel-perfect? Pixel-ish.",
                        "Two boards at once. Time control: blitz."], max_w=520)
    return c.render()


# --- projects: one clickable card each ---------------------------------------------------------------
PROJECTS = [
    ("energy", "♞", "AGENTS · TEXT2SQL", "Energy Copilot", "Ask your house how much the fridge costs.",
     ["11-node LangGraph agent: the LLM fills a query plan, code compiles it to parameterized SQL.",
      "sqlglot guard, read-only, one home; every number traces back to a query row.",
      "11 skills, 25 tools on bge-m3 + pgvector HNSW: skill hit@1 1.0, tool P/R 0.786 / 0.964."],
     ["Python", "FastAPI", "TimescaleDB", "pgvector", "LangGraph"]),
    ("receipts", "♜", "DOCUMENT AI", "Receipt Reader", "Photo in, structured receipt out, in about 0.25 s.",
     ["OpenCV cleanup → GPU PaddleOCR → LayoutLMv3 fields and line items → spending categories.",
      "SROIE field F1 0.65 → 0.83; fully-correct receipts 44% → 61%.",
      "Multi-agent error analysis caught 4 training-label bugs, each fix tested in its own worktree."],
     ["PyTorch", "LayoutLMv3", "PaddleOCR", "FastAPI", "React"]),
    ("vector", "♝", "FROM SCRATCH", "Vector Search Engine", "Search by meaning, every index written by hand.",
     ["HNSW in NumPy + Numba, no FAISS or hnswlib: deletes, filters, hnswlib-level recall.",
      "0.98 recall@10 at 0.15 ms on 120k embeddings, 60× faster than exact search.",
      "Same eval vs a pure-Python HNSW: recall@10 0.91 vs 0.62, ~240× faster."],
     ["Python", "NumPy", "Numba", "sentence-transformers"]),
    ("ytb", "♟", "FINE-TUNING", "YouTube Summarizer", "A 0.6B model watches YouTube so you don't have to.",
     ["Qwen3-0.6B turns a link into notes: overview, key points in order, takeaway.",
      "Captions or local faster-whisper; long videos split into ≤2,048-token parts.",
      "Fine-tuning it and scoring faithfulness on a 50-transcript golden set (in progress)."],
     ["PyTorch", "Hugging Face", "FastAPI"]),
    ("finance", "♛", "CHAT BOTS · FULL-STACK", "Zalo + Telegram Finance App", "Text the bot \"pho 45k\" and it lands in your budget.",
     ["Telegram and Zalo bots: a line of text or a receipt photo becomes a draft you confirm.",
      "Wallets, categories, monthly budgets with alerts, stats; Vietnamese and English.",
      "Built solo in 29 reviewed PRs: 366 automated tests, 33 bugs found and fixed.",
      "Live: sochitieu-btl.vercel.app"],
     ["React", "TypeScript", "Express", "MongoDB", "PaddleOCR"]),
]


def project_svg(slug, ch, kicker, title, tagline, bullets, stack) -> str:
    c = Card(440, 300, title, f"{title}: {tagline} " + " ".join(bullets) + " Stack: " + ", ".join(stack) + ".", seed=20 + len(title))
    c.add(f'<g transform="translate(46,78)"><g class="bob">{piece(ch, 0, 0, 44)}</g></g>')
    c.add(f'<text x="84" y="40" class="k">{c.t(kicker)}</text>',
          f'<text x="84" y="66" font-size="21" font-weight="900" fill="{CREAM}">{c.t(title)}</text>')
    y = 88 + c.text_block(84, 88, tagline, 330, 13, "Bold", LAV, lh=16) + 18
    for b in bullets:
        c.add(f'<rect x="30" y="{y - 8}" width="7" height="7" fill="{GOLD}" transform="rotate(45 33.5 {y - 4.5})"/>')
        y += c.text_block(46, y, b, 368, 12.5, "Regular", CREAM, lh=16) + 7
    x = 28
    for s in stack:
        w = text_width(s, 10.5) + 16
        c.add(f'<rect x="{x:.0f}" y="258" width="{w:.0f}" height="20" rx="10" fill="none" stroke="#fff" stroke-opacity=".25"/>',
              f'<text x="{x + w / 2:.0f}" y="272" text-anchor="middle" font-size="10.5" font-weight="700" fill="{MUTED}">{c.t(s)}</text>')
        x += w + 6
    c.add(f'<text x="414" y="40" text-anchor="end" font-size="12" font-weight="900" fill="{GOLD}">{c.t("open repo →")}</text>')
    return c.render()


# --- stack: the army ------------------------------------------------------------------------------------
ARMY = [
    ("♛", "Languages", "the royal family", [("python", "Python"), ("typescript", "TypeScript"), ("openjdk", "Java"),
                                            ("cplusplus", "C++"), ("dotnet", "C#")]),
    ("♞", "AI / LLM", "the attack", [("pytorch", "PyTorch"), ("numpy", "NumPy"), ("huggingface", "Hugging Face"),
                                     ("langgraph", "LangGraph"), ("langchain", "LangChain"), ("opencv", "OpenCV"),
                                     ("paddlepaddle", "PaddleOCR")]),
    ("♜", "Backend & data", "the castle", [("fastapi", "FastAPI"), ("postgresql", "PostgreSQL"), (None, "pgvector"),
                                            ("qdrant", "Qdrant"), ("pydantic", "Pydantic")]),
    ("♝", "Frontend & apps", "the flank", [("react", "React"), ("streamlit", "Streamlit")]),
    ("♟", "Tools", "the pawn structure", [("git", "Git"), ("pytest", "Pytest"), (None, "tree-sitter"), ("kaggle", "Kaggle")]),
]


def logo_tile(slug, x: float, y: float) -> str:
    if slug is None:
        return f'<rect x="{x}" y="{y}" width="30" height="30" rx="8" fill="#2a2470"/>' + piece("♟", x + 15, y + 25, 19)
    b = BRANDS[slug]
    r, g, bl = (int(b["hex"][i:i + 2], 16) for i in (0, 2, 4))
    ink = "#1b1838" if 0.2126 * r + 0.7152 * g + 0.0722 * bl > 150 else "#fff"
    return (f'<rect x="{x}" y="{y}" width="30" height="30" rx="8" fill="#{b["hex"]}"/>'
            f'<g transform="translate({x + 7},{y + 7}) scale({16 / 24:.4f})"><path d="{b["path"]}" fill="{ink}"/></g>')


def stack_svg() -> str:
    rows, y, x0, x1 = [], 104, 236, 870
    for ch, cat, role, items in ARMY:
        x, line, tiles = x0, 0, []
        for slug, name in items:
            w = 30 + 10 + text_width(name, 12.5) + 12
            if x + w > x1:
                x, line = x0, line + 1
            tiles.append((slug, name, x, y + line * 38, w))
            x += w + 8
        rows.append((ch, cat, role, y, tiles))
        y += max(48, (line + 1) * 38) + 14
    H = y + 70
    c = Card(900, H, "Tech stack: the army",
             "Tech stack, ranked like chess pieces. Languages: Python, TypeScript, Java, C++, C#. AI and LLM: PyTorch, NumPy, "
             "Hugging Face, LangGraph, LangChain, OpenCV, PaddleOCR. Backend and data: FastAPI, PostgreSQL, pgvector, Qdrant, "
             "Pydantic. Frontend and apps: React, Streamlit. Tools: Git, Pytest, tree-sitter, Kaggle.", seed=31)
    c.header("TECH STACK · THE ARMY", "Every piece I play with.")
    for ch, cat, role, ry, tiles in rows:
        c.add(piece(ch, 54, ry + 27, 26),
              f'<text x="78" y="{ry + 14}" font-size="14" font-weight="700" fill="{CREAM}">{c.t(cat)}</text>',
              f'<text x="78" y="{ry + 31}" font-size="11.5" font-weight="400" fill="{MUTED}">{c.t(role)}</text>')
        for slug, name, tx, ty, w in tiles:
            c.add(f'<rect x="{tx:.0f}" y="{ty}" width="{w:.0f}" height="30" rx="8" fill="#0b0f2e" fill-opacity=".75" stroke="#fff" stroke-opacity=".14"/>',
                  logo_tile(slug, tx, ty),
                  f'<text x="{tx + 40:.0f}" y="{ty + 20}" font-size="12.5" font-weight="700" fill="{CREAM}">{c.t(name)}</text>')
    c.heckler(58, H - 18, ["Python is the queen. Obviously.", "LangGraph AND LangChain. Agents all the way down.",
                           "7 AI pieces, 2 frontend. We know where the love goes.", "C# showed up. Nobody asked, but welcome."],
              max_w=520)
    return c.render()


def main() -> None:
    out = {"work.svg": work_svg(), "stack.svg": stack_svg()}
    for p in PROJECTS:
        out[f"proj-{p[0]}.svg"] = project_svg(*p)
    for name, svg in out.items():
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"wrote assets/{name} ({len(svg) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
