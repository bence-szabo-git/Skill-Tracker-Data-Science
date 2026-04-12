# 📊 Data Science Skill Tracker

> A live, automated pipeline that monitors which technical skills are in demand across remote tech job postings — updated daily, visualized in real time.

🔗 **[View Live Dashboard](https://skill-tracker-data-science-bkb5wra6u9ybbyxzkdm6aa.streamlit.app/)** 

---

## 🧭 Overview

The job market doesn't announce when a skill becomes essential. This project tracks it quietly, every day, by fetching real job postings, extracting the skills they require, and surfacing trends over time through an interactive dashboard.

Built as a portfolio project, it demonstrates the full data science workflow end-to-end: data ingestion, HTML cleaning, NLP-based skill extraction, and interactive visualization — all running on free infrastructure, fully automated.

---

## 🏗️ Architecture

The project is organized as three independent layers, each reading from and writing to a flat file:

```
[pipeline.py]  →  jobs_raw.csv  →  [skills.py]  →  skills_data.csv  →  [app.py]
  Fetch & clean                    Score & classify                     Dashboard
  RemoteOK API                     Keyword + spaCy NLP                  Streamlit
        ↑
  GitHub Actions
  runs this daily
  at 06:00 UTC
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
├── jobs_raw.csv         # Raw job data (job_id, date, title, text, url)
├── skills_data.csv      # Scored skill data (binary + spaCy columns per skill)
│
├── requirements.txt     # Python dependencies
├── .gitignore
└── .github/
    └── workflows/
        └── daily_pipeline.yml   # GitHub Actions — runs pipeline daily at 06:00 UTC
```

---

## ⚙️ How It Works

### Stage 1 — Data Ingestion (`pipeline.py`)

Fetches job postings from the [RemoteOK public API](https://remoteok.com/api), filtering for data and tech-adjacent roles by keyword matching on job titles. For each posting it:

- Extracts `job_id`, `title`, `description`, and `url`
- Cleans HTML entities and tags from the description text
- Concatenates title and description into a single `text` field for richer NLP input
- Deduplicates by `job_id` across all historical runs — each job is stored exactly once, on the date it was first seen
- Appends new rows to `jobs_raw.csv`

### Stage 2 — Skill Extraction (`skills.py`)

Reads only unprocessed jobs — rows whose `job_id` does not yet exist in `skills_data.csv` — and scores them using two independent methods:

**Binary keyword matching** — checks whether skill-specific keywords literally appear in the lowercased text. Fast, precise, and fully interpretable.

**spaCy NLP scoring** — uses `en_core_web_sm` to extract named entities and noun chunks from the requirements section of each job description, then matches those against the skills list. Catches semantic variants and phrasing that simple keyword matching would miss.

Before running either method, a requirements section extractor isolates the most signal-rich part of each posting — searching for trigger phrases like "required", "qualifications", "experience with" — so the NLP model reads the relevant 1200 characters rather than the company introduction.

Each skill produces two columns in `skills_data.csv`:
- `{Skill}_binary` — 1 if a keyword variant is found in the full text, else 0
- `{Skill}_score` — 1 if spaCy entity/noun chunk extraction finds the skill in the requirements section, else 0

### Stage 3 — Dashboard (`app.py`)

A Streamlit application that reads `skills_data.csv` and `jobs_raw.csv` and presents three sections:

**Today's Top Skills** — a horizontal bar chart showing how many job postings from the most recent date mention each skill, ranked by frequency.

**Skill Trends Over Time** — an interactive line chart with markers showing daily skill mention counts over the full history of the dataset. Users can select which skills to compare via a multiselect widget.

**Drilldown** — a searchable table showing every job posting that mentions a selected skill, with the job title as a clickable link to the original posting on RemoteOK.

---

## 🤖 Automation

The pipeline runs automatically every day at **06:00 UTC** via GitHub Actions without any manual intervention. The workflow:

1. Checks out the repository on a fresh `ubuntu-latest` runner
2. Installs all dependencies from `requirements.txt` and downloads the spaCy model
3. Runs `pipeline.py` to fetch new job postings
4. Runs `skills.py` to score any unprocessed jobs
5. Commits updated `jobs_raw.csv` and `skills_data.csv` back to the repository
6. Streamlit Community Cloud picks up the new data automatically on the next dashboard visit

The workflow only commits when there are actual changes — if no new jobs were found, the commit is skipped to keep the history clean. It can also be triggered manually from the GitHub Actions tab at any time.

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

- Python 3.11+
- A GitHub Codespace or local environment
- No API keys required for the core pipeline — RemoteOK is fully open

### Installation

```bash
git clone https://github.com/your-username/ds-skill-tracker.git
cd ds-skill-tracker
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Running the Pipeline Manually

```bash
# Step 1 — fetch today's job postings
python pipeline.py

# Step 2 — extract skill signals (only processes new jobs)
python skills.py

# Step 3 — launch the dashboard locally
streamlit run app.py
```

---

## 📦 Dependencies

```
requests
pandas
spacy
streamlit
plotly
en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

---

## 💡 Design Decisions

**Why RemoteOK?** Most free job APIs — Jooble, Adzuna — truncate descriptions to 300–500 characters, which is insufficient for reliable NLP. RemoteOK provides full untruncated descriptions with no authentication required and a stable, consistent JSON structure.

**Why keyword matching as the primary signal?** During development, zero-shot classification models produced inflated confidence scores on long technical texts — almost any skill scored as plausible against a dense job description. Keyword matching proved more accurate for explicit technical skill detection. The spaCy layer adds value by catching semantic variants not covered by the keyword list.

**Why binary output instead of raw scores?** Storing confidence floats overstates precision. A binary column is more honest about what the model actually knows and produces cleaner, more interpretable visualizations.

**Why spaCy over HuggingFace hosted inference?** HuggingFace's free Inference API is blocked at the CDN level from GitHub Codespaces and Actions IP ranges, making it unreliable for automated pipelines. spaCy's `en_core_web_sm` installs directly from PyPI with no external API dependency, making the pipeline fully self-contained and immune to third-party outages.

**Why store URL in `jobs_raw.csv` separately from `skills_data.csv`?** The two files serve different purposes — raw job data and scored skill data. Keeping them separate and joining at query time in the dashboard follows a clean data model and avoids duplicating large text fields in the skills file.

---

## 🗺️ What's Built

- [x] Data ingestion from RemoteOK with job ID deduplication
- [x] HTML cleaning and requirements section extraction
- [x] Hybrid skill extraction — keyword matching and spaCy NLP
- [x] Incremental processing — only new jobs are scored on each run
- [x] Streamlit dashboard with snapshot bar chart, time-series line chart, and drilldown table
- [x] Clickable job title links to original postings in the drilldown section
- [x] Daily automation via GitHub Actions at 06:00 UTC
- [x] Deployed to Streamlit Community Cloud — always online

---

## 🔭 Future Development

**Add a second data source**
RemoteOK is limited to remote-first postings and occasionally obfuscates descriptions with spam-prevention tags. Adding The Muse API — which returns full, clean descriptions with no truncation — would broaden the dataset and reduce noise from any single source.

**Improve the requirements section extractor**
The current trigger-phrase approach occasionally starts the extraction window too late, missing skills mentioned early in the requirements block. A sentence-level classifier trained to identify requirement sentences would be more robust across diverse job description formats.

**Use actual posting dates**
Currently the `date` column reflects the day a job was first scraped, not when it was posted. RemoteOK returns an `epoch` timestamp per job. Using the actual posting date would make the time-series chart more meaningful for long-term trend analysis.

**Expand the skills list with role-specific clusters**
The current 15 skills were chosen for breadth at MVP stage. Adding role-specific clusters — a Data Engineering cluster covering Airflow, dbt, Kafka, and Redshift, or an MLOps cluster covering MLflow, Kubeflow, and Weights & Biases — would make the tracker more useful for targeted job searches.

**Salary trend correlation**
RemoteOK returns salary ranges for a subset of postings. Correlating salary data with skill demand over time would add a genuinely useful analytical layer — tracking not just which skills are in demand but which ones command a premium.

**Percentage view in dashboard**
Currently the charts show raw job counts. Normalizing by total jobs per day to show the percentage of postings mentioning each skill would make trends comparable across days with different total job volumes.

**Weekly digest via email or Slack**
A scheduled summary of the top trending skills, delivered via email or Slack webhook, would extend the project beyond the dashboard and demonstrate end-to-end data product thinking.

---

## 📄 License

MIT License — free to use, adapt, and build on.