import os

import pandas as pd
import torch
from transformers import pipeline

SKILL_KEYWORDS = {
    "Python": ["python"],
    "SQL": ["sql", "mysql", "postgresql", "postgres"],
    "Machine Learning": ["machine learning", "ml ", "sklearn", "scikit"],
    "Deep Learning": ["deep learning", "neural network", "cnn", "rnn"],
    "NLP": ["nlp", "natural language", "text mining", "spacy", "nltk"],
    "LLMs": ["llm", "large language model", "gpt", "llama", "openai"],
    "PyTorch": ["pytorch", "torch"],
    "TensorFlow": ["tensorflow", "keras"],
    "Spark": ["spark", "pyspark"],
    "Docker": ["docker", "kubernetes", "k8s", "containeriz"],
    "Cloud": ["aws", "azure", "gcp", "google cloud", "cloud"],
    "Statistics": ["statistics", "statistical", "probability", "hypothesis"],
    "dbt": ["dbt", "data build tool"],
    "Tableau": ["tableau"],
    "Power BI": ["power bi", "powerbi"],
}

SKILLS = list(SKILL_KEYWORDS.keys())
CSV_INPUT = "jobs_raw.csv"
CSV_OUTPUT = "skills_data.csv"


def load_jobs():
    if not os.path.exists(CSV_INPUT):
        print(f"Error: {CSV_INPUT} not found.")
        os._exit(1)
    return pd.read_csv(CSV_INPUT)


def build_classifier():
    return pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=-1,
    )


def compute_binary_scores(text):
    """Check if any keyword variants for each skill appear in the text."""
    text_lower = text.lower()
    scores = {}
    for skill in SKILLS:
        found = any(keyword in text_lower for keyword in SKILL_KEYWORDS[skill])
        col_name = skill.replace(" ", "_") + "_binary"
        scores[col_name] = 1 if found else 0
    return scores


def compute_hf_scores(classifier, text):
    """Run zero-shot classifier and return 1 if score > 0.90, else 0."""
    result = classifier(text, candidate_labels=SKILLS, multi_label=True)
    score_map = dict(zip(result["labels"], result["scores"]))
    scores = {}
    for skill in SKILLS:
        col_name = skill.replace(" ", "_") + "_score"
        scores[col_name] = 1 if score_map.get(skill, 0.0) > 0.90 else 0
    return scores


def build_columns_order():
    """Return the expected column order: job_id, date, title, all _binary, all _score."""
    binary_cols = [s.replace(" ", "_") + "_binary" for s in SKILLS]
    score_cols = [s.replace(" ", "_") + "_score" for s in SKILLS]
    return ["job_id", "date", "title"] + binary_cols + score_cols


def save_results(results_df):
    """Save results with deduplication on job_id."""
    if not results_df.empty:
        if os.path.exists(CSV_OUTPUT):
            existing_df = pd.read_csv(CSV_OUTPUT, dtype=str)
            combined_df = pd.concat([existing_df, results_df], ignore_index=True)
            deduped_df = combined_df.drop_duplicates(subset=["job_id"], keep="first")
            deduped_df.to_csv(CSV_OUTPUT, index=False)
        else:
            results_df.to_csv(CSV_OUTPUT, index=False)


def main():
    jobs_df = load_jobs()
    classifier = build_classifier()
    records = []
    total_jobs = len(jobs_df)

    for index, row in enumerate(jobs_df.itertuples(index=False), start=1):
        job_id = str(getattr(row, "job_id", "") or "").strip()
        date = str(getattr(row, "date", "") or "").strip()
        title = str(getattr(row, "title", "") or "").strip()
        text = str(getattr(row, "text", "") or "").strip()

        print(f"Processing job {index}/{total_jobs}: {title}")

        binary_scores = compute_binary_scores(text)
        hf_scores = compute_hf_scores(classifier, text)

        record = {"job_id": job_id, "date": date, "title": title}
        record.update(binary_scores)
        record.update(hf_scores)
        records.append(record)

    if records:
        columns = build_columns_order()
        results_df = pd.DataFrame(records, columns=columns)
        save_results(results_df)


if __name__ == "__main__":
    main()
