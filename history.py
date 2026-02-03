#!./env/bin/python3
import requests
from bs4 import BeautifulSoup
import random
import pandas as pd
import logging
from tqdm import tqdm
import time
import datetime
import argparse
import sys
import os
from collections import defaultdict
import matplotlib.pyplot as plt


def main():

    parser = argparse.ArgumentParser(
        description="Collect job postings data from Linkedin."
    )

    parser.add_argument(
        "-t",
        "--title",
        type=str,
        default="Software Developer",
        help="Job title to search for.",
    )

    parser.add_argument(
        "-l", "--location", type=str, required=True, help="Location to search in."
    )

    parser.add_argument(
        "--input",
        default="./results/",
        type=str,
        help="input path (defualt: ./results/)",
    )

    parser.add_argument(
        "--output", default="./img/", type=str, help="output path (defualt: ./img/)"
    )

    parser.add_argument(
        "--skip",
        default="./skip.csv",
        type=str,
        help="Path to skip file of company names to ingore (defualt: ./skip.csv)",
    )

    parser.add_argument(
        "--html",
        action="store_true",
        help="Make a html file to serve output (defualt: False)",
    )

    args = parser.parse_args()
    title = args.title
    location = args.location
    output = args.output
    input_path = args.input
    skip_file = args.skip
    save_to_html = args.html

    skip_companies = pd.read_csv(skip_file)["company_name"].to_list()
    print(skip_companies)

    if not os.path.exists(output):
        os.makedirs(output)

    output = f"{output}{location}-{title}/"
    if not os.path.exists(output):
        os.makedirs(output)

    count = 0
    for file in os.listdir(input_path):
        if file.endswith(".csv") and location in file:
            count += 1
    print(f"Total number of files for {location}: {count}")

    all_jobs_dfs = []
    for file in tqdm(os.listdir(input_path)):
        if file.endswith(".csv") and location in file and file.startswith("jobs_"):
            date = file.split("_")[-1].replace(".csv", "")
            df = pd.read_csv(os.path.join(input_path, file))
            df["date"] = date
            all_jobs_dfs.append(df)
    print(f"Total number of dataframes collected: {len(all_jobs_dfs)}")
    job_title = title
    place = location
    minimum_number_of_jobs = 0
    jobs_over_time = pd.concat(all_jobs_dfs)
    jobs_over_time_grouped = (
        jobs_over_time.groupby(["date", "company_name"])
        .size()
        .reset_index(name="job_count")
    )
    jobs_over_time_grouped = jobs_over_time_grouped[
        ~jobs_over_time_grouped["company_name"].isin(skip_companies)
    ]
    jobs_over_time_grouped = jobs_over_time_grouped[
        jobs_over_time_grouped["job_count"] >= minimum_number_of_jobs
    ]
    jobs_over_time_grouped = jobs_over_time_grouped.fillna(0)
    jobs_over_time_pivot = jobs_over_time_grouped.pivot(
        index="date", columns="company_name", values="job_count"
    ).fillna(0)
    jobs_over_time_pivot.plot(kind="line", figsize=(15, 8))
    plt.title(
        f'Number of Job Postings Over Time per Company in {location} for "{job_title}"'
    )
    plt.xlabel("Date")
    plt.ylabel("Number of Job Postings")
    plt.legend(title="Company Name", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    fig_job_posts = f"{output}{location}_{title}_job_posts.png"
    plt.savefig(fig_job_posts)

    minimum_number_of_application = 0
    applications_over_time = pd.concat(all_jobs_dfs)
    applications_over_time.groupby(["date", "company_name"])[
        "num_applicants"
    ].sum().reset_index(name="total_applications")
    applications_over_time_grouped = (
        applications_over_time.groupby(["date", "company_name"])["num_applicants"]
        .sum()
        .reset_index(name="total_applications")
    )
    applications_over_time_grouped = applications_over_time_grouped[
        ~applications_over_time_grouped["company_name"].isin(skip_companies)
    ]
    applications_over_time_grouped = applications_over_time_grouped[
        applications_over_time_grouped["total_applications"]
        >= minimum_number_of_application
    ]
    applications_over_time_pivot = applications_over_time_grouped.pivot(
        index="date", columns="company_name", values="total_applications"
    ).fillna(0)
    applications_over_time_pivot.plot(kind="line", figsize=(15, 8))
    plt.title(
        f'Number of Applications Over Time per Company in {place} (excluding well known consulting companies) for "{job_title}" '
    )
    plt.xlabel("Date")
    plt.ylabel("Number of Applications")
    plt.legend(title="Company Name", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    fig_applitactions = f"{output}{location}_{title}_applications.png"
    plt.savefig(fig_applitactions)

    minimum_number_of_jobs = 0
    jobs_over_time = pd.concat(all_jobs_dfs)
    jobs_over_time_grouped = (
        jobs_over_time.groupby(["date", "company_name"])
        .size()
        .reset_index(name="job_count")
    )
    jobs_over_time_grouped = jobs_over_time_grouped[
        jobs_over_time_grouped["company_name"].isin(skip_companies)
    ]
    jobs_over_time_grouped = jobs_over_time_grouped[
        jobs_over_time_grouped["job_count"] >= minimum_number_of_jobs
    ]
    jobs_over_time_grouped = jobs_over_time_grouped.fillna(0)
    jobs_over_time_pivot = jobs_over_time_grouped.pivot(
        index="date", columns="company_name", values="job_count"
    ).fillna(0)
    jobs_over_time_pivot.plot(kind="line", figsize=(15, 8))
    plt.title(
        f'Number of Job Postings Over Time per Company in {location} (skipped companies) for "{job_title}"'
    )
    plt.xlabel("Date")
    plt.ylabel("Number of Job Postings")
    plt.legend(title="Company Name", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    fig_job_posts_skipped = f"{output}{location}_{title}_job_posts_skipped.png"
    plt.savefig(fig_job_posts_skipped)


    if save_to_html:
        
        with open(f"{output}index.html", "w") as f:
            imgs = "\n".join([f'<img src="{p.replace(output, "./")}" alt="" srcset=""><br>' for p in [fig_job_posts, fig_applitactions, fig_job_posts_skipped]])
            html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Linkedin Job data </title>
</head>
<body>
    <h1>Linkedin Job data from {location}</h1>
    <br>
    {imgs}
</body>
</html>
            """
            f.write(html)


if __name__ == "__main__":
    main()
