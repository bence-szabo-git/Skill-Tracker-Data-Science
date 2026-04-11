# 📊 Data Science Skill Tracker

> A live, automated pipeline that monitors which technical skills are in demand across remote data science job postings — updated daily, visualized in real time.

---

## 🧭 Overview

The job market doesn't announce when a skill becomes essential. This project tracks it quietly, every day, by fetching real job postings, extracting the skills they require, and surfacing trends over time through an interactive dashboard.

Built as a portfolio project, it demonstrates the full data science workflow end-to-end: data ingestion, text cleaning, NLP-based feature extraction, and interactive visualization — all running on free infrastructure.

---

## 🏗️ Architecture

The project is organized as three independent layers, each reading from and writing to a flat file:

```
[pipeline.py]  →  jobs_raw.csv  →  [skills.py]  →  skills_data.csv  →  [app.py]
  Fetch & clean                    Score & classify                     Dashboard
  RemoteOK API                     Keyword + HuggingFace                Streamlit
```

Each layer can be run and debugged independently, which makes the pipeline easy to maintain and extend.

---

## 📁 Project Structure

```
ds-skill-tracker/
│
├── pipeline.py          # Fetches job postings from RemoteOK, cleans HTML, saves to CSV
├── skills.py            # Extracts skill signals using hybrid NLP, saves scored data
├── app.py               # Streamlit dashboard for visualization
│
├── jobs_raw.csv         # Raw job data (job_id, date, title, text)
├── skills_data.csv      # Scored skill data (binary + HF columns per skill)
│
├── requirements.txt     # Python dependencies
├── .gitignore
└── .github/
    └── workflows/       # GitHub Actions for daily automation (coming soon)
```

---

## ⚙️ How It Works

### Stage 1 — Data Ingestion (`pipeline.py`)

Fetches up to 50 job postings per run from the [RemoteOK public API](https://remoteok.com/api), filtering for data-adjacent roles by keyword matching on titles. For each posting it:

- Extracts the `job_id`, `title`, and full `description`
- Cleans HTML entities and tags from the description text
- Concatenates title and description into a single `text` field for richer NLP input
- Deduplicates by `job_id` across all historical runs — each job is stored exactly once, on the date it was first seen
- Appends new rows to `jobs_raw.csv`

### Stage 2 — Skill Extraction (`skills.py`)

For each job in `jobs_raw.csv`, scores the presence of 15 target data science skills using two independent methods:

**Binary keyword matching** — checks whether skill-specific keywords literally appear in the lowercased text. Fast, interpretable, and precise for explicit mentions.

**HuggingFace zero-shot classification** — runs `facebook/bart-large-mnli` against the text with each skill as a candidate label (`multi_label=True`). Scores above 0.90 are treated as a positive signal. Catches semantic variants and implied skills that keyword matching would miss.

Each skill produces two columns in `skills_data.csv`:
- `{Skill}_binary` — 1 if keyword found, else 0
- `{Skill}_score` — 1 if HF confidence > 0.85, else 0

### Stage 3 — Dashboard (`app.py`)

A Streamlit application that reads `skills_data.csv` and presents:

- A time-series line chart showing how skill demand evolves day by day
- A snapshot bar chart of today's most in-demand skills
- A toggle between binary and HF-scored views

---

## 🎯 Skills Tracked

| Skill | Keywords Used |
|---|---|
| Python | python |
| SQL | sql, mysql, postgresql, postgres |
| Machine Learning | machine learning, ml, sklearn, scikit |
| Deep Learning | deep learning, neural network, cnn, rnn |
| NLP | nlp, natural language, text mining, spacy, nltk |
| LLMs | llm, large language model, gpt, llama, openai |
| PyTorch | pytorch, torch |
| TensorFlow | tensorflow, keras |
| Spark | spark, pyspark |
| Docker | docker, kubernetes, k8s, containeriz |
| Cloud | aws, azure, gcp, google cloud, cloud |
| Statistics | statistics, statistical, probability, hypothesis |
| dbt | dbt, data build tool |
| Tableau | tableau |
| Power BI | power bi, powerbi |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A GitHub Codespace or local environment
- No API keys required — RemoteOK is fully open

### Installation

```bash
git clone https://github.com/your-username/ds-skill-tracker.git
cd ds-skill-tracker
pip install -r requirements.txt
```

### Running the Pipeline

```bash
# Step 1 — fetch today's job postings
python pipeline.py

# Step 2 — extract skill signals
python skills.py

# Step 3 — launch the dashboard
streamlit run app.py
```

> **Note:** The first run of `skills.py` will download the `facebook/bart-large-mnli` model (~1.6 GB). Subsequent runs use the cached version and are significantly faster.

---

## 📦 Dependencies

```
requests
pandas
transformers
torch
streamlit
```

---

## 🗺️ Roadmap

- [x] Data ingestion from RemoteOK with deduplication
- [x] HTML cleaning pipeline
- [x] Hybrid skill extraction (keyword + zero-shot NLP)
- [x] Binary and confidence-scored output columns
- [ ] Streamlit dashboard with time-series visualization
- [ ] Daily automation via GitHub Actions
- [ ] Deployment to Streamlit Community Cloud
- [ ] Expand skill list and refine keyword variants
- [ ] Add secondary data source (Adzuna or The Muse)

---

## 💡 Design Decisions

**Why RemoteOK?** Most free job APIs (Jooble, Adzuna) truncate descriptions to 300–500 characters, which is insufficient for reliable NLP. RemoteOK provides full descriptions with no authentication required.

**Why hybrid scoring?** Zero-shot classification alone produces inflated confidence scores on long technical texts — almost any skill sounds plausible against a dense job description. Keyword matching is more precise for explicit technical skills. The two methods together are more informative than either alone, and the gap between them is itself a signal worth tracking.

**Why binary output?** Storing raw confidence floats overstates precision. A threshold-based binary column is more honest about what the model actually knows, and produces cleaner visualizations.

---

## 📄 License

MIT License — free to use, adapt, and build on.