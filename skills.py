import os

import pandas as pd
import spacy

SKILLS = [
    "Python", "SQL", "Machine Learning", "Deep Learning",
    "NLP", "LLMs", "PyTorch", "TensorFlow", "Spark",
    "Docker", "Cloud", "Statistics", "dbt", "Tableau", "Power BI"
]

SKILL_KEYWORDS = {
    "Python":           ["python"],
    "SQL":              ["sql", "mysql", "postgresql", "postgres"],
    "Machine Learning": ["machine learning", "ml ", "sklearn", "scikit"],
    "Deep Learning":    ["deep learning", "neural network", "cnn", "rnn"],
    "NLP":              ["nlp", "natural language", "text mining", "spacy", "nltk"],
    "LLMs":             ["llm", "large language model", "gpt", "llama", "openai"],
    "PyTorch":          ["pytorch", "torch"],
    "TensorFlow":       ["tensorflow", "keras"],
    "Spark":            ["spark", "pyspark"],
    "Docker":           ["docker", "kubernetes", "k8s", "containeriz"],
    "Cloud":            ["aws", "azure", "gcp", "google cloud", "cloud"],
    "Statistics":       ["statistics", "statistical", "probability", "hypothesis"],
    "dbt":              ["dbt", "data build tool"],
    "Tableau":          ["tableau"],
    "Power BI":         ["power bi", "powerbi"]
}

CSV_INPUT = "jobs_raw.csv"
CSV_OUTPUT = "skills_data.csv"

print("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")


def extract_requirements_section(text):
    search_text = text.lower()
    triggers = [
        "required",
        "requirements",
        "qualifications",
        "you will need",
        "what you'll bring",
        "minimum",
        "experience with",
        "skills",
    ]
    for trigger in triggers:
        idx = search_text.find(trigger)
        if idx != -1:
            return text[idx: idx + 1200]
    return text[-1200:] if len(text) > 1200 else text


def binary_score(text):
    text_lower = text.lower()
    scores = {}
    for skill in SKILLS:
        found = any(keyword in text_lower for keyword in SKILL_KEYWORDS[skill])
        col_name = skill.replace(" ", "_") + "_binary"
        scores[col_name] = 1 if found else 0
    return scores


def spacy_score(text):
    requirements_text = extract_requirements_section(text)
    doc = nlp(requirements_text)
    extracted = [ent.text.lower() for ent in doc.ents]
    extracted += [chunk.text.lower() for chunk in doc.noun_chunks]

    scores = {}
    for skill in SKILLS:
        col_name = skill.replace(" ", "_") + "_score"
        skill_lower = skill.lower()
        keywords = [kw.lower() for kw in SKILL_KEYWORDS[skill]]
        matched = any(
            skill_lower in value or any(keyword in value for keyword in keywords)
            for value in extracted
        )
        scores[col_name] = 1 if matched else 0
    return scores, requirements_text


def build_columns_order():
    binary_cols = [skill.replace(" ", "_") + "_binary" for skill in SKILLS]
    score_cols = [skill.replace(" ", "_") + "_score" for skill in SKILLS]
    return ["job_id", "date", "title"] + binary_cols + score_cols


def load_jobs():
    if not os.path.exists(CSV_INPUT):
        print(f"Error: {CSV_INPUT} not found.")
        os._exit(1)
    return pd.read_csv(CSV_INPUT)


def save_results(results_df):
    if results_df.empty:
        return

    if os.path.exists(CSV_OUTPUT):
        existing_df = pd.read_csv(CSV_OUTPUT, dtype=str)
        combined_df = pd.concat([existing_df, results_df], ignore_index=True)
        deduped_df = combined_df.drop_duplicates(subset=["job_id"], keep="first")
        deduped_df.to_csv(CSV_OUTPUT, index=False)
    else:
        results_df.to_csv(CSV_OUTPUT, index=False)


def load_existing_job_ids():
    if not os.path.exists(CSV_OUTPUT):
        return set()
    existing_df = pd.read_csv(CSV_OUTPUT, dtype=str)
    return set(existing_df["job_id"].astype(str))


def main():
    jobs_df = load_jobs()
    total_jobs = len(jobs_df)
    
    existing_ids = load_existing_job_ids()
    jobs_df = jobs_df[~jobs_df["job_id"].astype(str).isin(existing_ids)]
    new_jobs = len(jobs_df)
    already_scored = total_jobs - new_jobs
    
    print(f"Total jobs in jobs_raw.csv: {total_jobs}")
    print(f"Already scored: {already_scored}")
    print(f"New jobs to process: {new_jobs}")
    
    if new_jobs == 0:
        print("No new jobs to process.")
        return
    
    records = []

    for index, row in enumerate(jobs_df.itertuples(index=False), start=1):
        job_id = str(getattr(row, "job_id", "") or "").strip()
        date = str(getattr(row, "date", "") or "").strip()
        title = str(getattr(row, "title", "") or "").strip()
        text = str(getattr(row, "text", "") or "").strip()

        binary_scores = binary_score(text)
        spacy_scores, requirements_text = spacy_score(text)

        record = {"job_id": job_id, "date": date, "title": title}
        record.update(binary_scores)
        record.update(spacy_scores)
        records.append(record)

        print(f"Processing job {index}/{new_jobs}: {title}")
        print(f"Requirements section sent to spaCy: {requirements_text}")

    if records:
        columns = build_columns_order()
        results_df = pd.DataFrame(records, columns=columns)
        save_results(results_df)


if __name__ == "__main__":
    main()
