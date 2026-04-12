import html
import os
import re

import pandas as pd
import requests

API_URL = "https://remoteok.com/api"
HEADERS = {"User-Agent": "skill-tracker-portfolio-project"}
CSV_FILE = "jobs_raw.csv"
KEYWORDS = [
    r"\bdata\b",
    r"\banalyst\b",
    r"\bscientist\b",
    r"machine learning",
    r"\bai\b",
    r"\bnlp\b",
    r"\bengineer\b",
]


def clean_text(text):
    if not isinstance(text, str):
        text = ""

    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_jobs():
    response = requests.get(API_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list):
        return []
    return data[1:]


def matches_position(position):
    if not isinstance(position, str):
        return False

    position_lower = position.lower()
    for keyword in KEYWORDS:
        if "machine learning" == keyword:
            if "machine learning" in position_lower:
                return True
        elif re.search(keyword, position_lower):
            return True
    return False


def transform_jobs(jobs):
    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    records = []

    for job in jobs:
        position = job.get("position", "") or ""
        if not matches_position(position):
            continue

        job_id = str(job.get("id", "") or "").strip()
        title = position.strip()
        description = job.get("description", "") or ""
        cleaned_description = clean_text(description)
        text = f"{title}. {cleaned_description}".strip()
        url = job.get("url", "") or ""

        records.append({"job_id": job_id, "date": today, "title": title, "text": text, "url": url})

    return records


def save_jobs(records):
    if not records:
        return 0, 0

    new_df = pd.DataFrame(records, columns=["job_id", "date", "title", "text", "url"])
    if os.path.exists(CSV_FILE):
        existing_df = pd.read_csv(CSV_FILE, dtype=str)
        existing_ids = set(existing_df["job_id"].fillna("").astype(str))
        filtered_df = new_df[~new_df["job_id"].astype(str).isin(existing_ids)]
        filtered_df = filtered_df.drop_duplicates(subset=["job_id"], keep="first")
        already_existing = len(new_df) - len(filtered_df)

        if not filtered_df.empty:
            filtered_df.to_csv(CSV_FILE, index=False, mode="a", header=False)

        return len(filtered_df), already_existing

    new_df.to_csv(CSV_FILE, index=False)
    return len(new_df), 0


def main():
    jobs = fetch_jobs()
    records = transform_jobs(jobs)
    fetched_count = len(jobs)
    matched_count = len(records)
    added_rows, already_existing = save_jobs(records)

    print(f"Fetched {fetched_count} jobs.")
    print(f"Matched {matched_count} jobs.")
    print(f"Already in dataset: {already_existing} job{'s' if already_existing != 1 else ''}.")
    print(f"Added {added_rows} new row{'s' if added_rows != 1 else ''}.")


if __name__ == "__main__":
    main()
