<div align="center">
<h1>Hi there, I'm Dang Nguyen Duc Anh</h1>
<p><i>Friends abroad call me <b>Harry Wilson</b></i></p>
<p><b>AI Engineer building multi-agent systems, RAG platforms & Text2SQL agents</b></p>

<p>
<a href="https://www.linkedin.com/in/dangnguyenducanh"><img src="https://img.shields.io/badge/LinkedIn-Dang%20Nguyen%20Duc%20Anh-blue?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
<a href="mailto:ducanhdn.ptit@gmail.com"><img src="https://img.shields.io/badge/Email-ducanhdn.ptit-red?style=for-the-badge&logo=gmail&logoColor=white" alt="Email" /></a>
</p>

<table style="border: none;">
<tr>
<td align="center">
<p><b>AI Engineer @ Research Institute of Posts and Telecommunications</b></p>
<p><i>B.S. Information Technology @ PTIT, Hanoi · GPA 3.7/4.0</i></p>
<p><i>Undergraduate Researcher (AI Agents · UI2Code) with University of Luxembourg</i></p>
<img src="https://img.shields.io/badge/Focus-Agentic%20AI-orange?style=flat-square" />
<img src="https://img.shields.io/badge/Production-110%2B%20bots-brightgreen?style=flat-square" />
<img src="https://img.shields.io/badge/Based%20in-Hanoi%2C%20VN-blue?style=flat-square" />
</td>
</tr>
</table>
</div>

<hr />

## About me

I grew up as a chess player. For years my evenings were spent over a board, calculating lines, studying openings and learning to lose gracefully. Chess taught me to think several moves ahead, to stay patient in complicated positions and to treat every mistake as something to study rather than something to hide.

Programming found me through the same curiosity. The first time I wrote code that actually worked, it felt like solving a puzzle where I also got to design the board. I came to love building things: small scripts at first, then web apps, then systems that could reason on their own. I stopped playing seriously, but the habit of calculating before moving never left.

Today I'm an **AI Engineer at the Research Institute of Posts and Telecommunications**, where I build multi-agent LLM systems and retrieval platforms that run more than 110 chatbots in production. I'm also an undergraduate researcher with the **University of Luxembourg**, studying how AI agents turn UI designs into working code, while finishing my B.S. in Information Technology at **PTIT** in Hanoi. In a way I'm still playing chess, only now the pieces are agents and the goal is to make them think well together.

Happy to talk about LangGraph, RAG, Text2SQL, document AI and agent evaluation.

<hr />

## What I've built at work

**MASS Chatbot v2 — enterprise multi-agent chatbot & retrieval platform**
- Built on **FastAPI + LangGraph + Qdrant**, serving **110+ production bots** with SSE streaming.
- Cut documentation-search latency from **~16 ms → ~7 ms** and keyword query latency from **95 ms → 5 ms**.
- Distilled cloud-LLM conversational policies into a local open-weights model (full fine-tuning on **110k+ chat messages**), saving **$1k+/month** in API costs.

<hr />

## Featured projects

### [Environmental Text2SQL](https://github.com/dangnguyenducanh/environmental-text2sql-)
> *Ask questions about household energy use in plain language.*
- End-to-end **Text2SQL agents** for behaviour recommendations and electricity-usage analysis on NILM sensor data.
- Hybrid tool/skill retrieval (**PgVector + BM25**): skill precision/recall **1.0 / 1.0**, tool precision/recall **0.786 / 0.964** across 50+ skills and tools.
- **Stack:** FastAPI · PostgreSQL (time-scaled) · LangGraph

### Receipt Reader
> *Photo in, structured receipt out, in about 0.25 s.*
- Pipeline: OpenCV preprocessing → GPU PaddleOCR → **LayoutLMv3** field & line-item extraction → spending categories.
- Benchmarked rules, CRF, RoBERTa and LayoutLMv3; raised SROIE field F1 from **0.65 → 0.83** and fully-correct receipts from **44% → 61%**.
- Multi-agent error analysis found **4 training-label bugs**, each fix tested in its own git worktree.
- **Stack:** PyTorch · LayoutLMv3 · PaddleOCR · FastAPI · PostgreSQL · React

### [YouTube Summarizer](https://github.com/dangnguyenducanh/ytb)
- Fine-tuned **Qwen3 0.6B** to summarize YouTube transcripts, benchmarked for faithfulness on a golden set of 50 transcripts.
- **Stack:** PyTorch · Hugging Face

<hr />

## Tech Stack

<div align="center">

**Languages**<br />
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" />
<img src="https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white" />
<img src="https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=cplusplus&logoColor=white" />
<img src="https://img.shields.io/badge/C%23-512BD4?style=for-the-badge&logo=dotnet&logoColor=white" />

**AI / LLM**<br />
<img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" />
<img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white" />
<img src="https://img.shields.io/badge/Hugging%20Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black" />
<img src="https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" />
<img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" />
<img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" />
<img src="https://img.shields.io/badge/PaddleOCR-0062B0?style=for-the-badge" />

**Backend & Data**<br />
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
<img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
<img src="https://img.shields.io/badge/PgVector-336791?style=for-the-badge&logo=postgresql&logoColor=white" />
<img src="https://img.shields.io/badge/Qdrant-DC244C?style=for-the-badge" />
<img src="https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white" />

**Frontend & Apps**<br />
<img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
<img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />

**Tools**<br />
<img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" />
<img src="https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" />
<img src="https://img.shields.io/badge/Tree--sitter-2E7D32?style=for-the-badge" />
<img src="https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white" />

</div>

<hr />

## GitHub Stats

<div align="center">
<img height="165" src="https://github-readme-stats.vercel.app/api?username=dangnguyenducanh&show_icons=true&theme=transparent&hide_border=true" />
<img height="165" src="https://github-readme-stats.vercel.app/api/top-langs/?username=dangnguyenducanh&layout=compact&theme=transparent&hide_border=true" />
</div>

<br />

<div align="center">
<sub>Vietnamese (native) · English (IELTS 6.0) — open to AI Engineer (LLM) roles and research collaborations. Feel free to reach out!</sub>
</div>
