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


def make_chartjs_config(df: pd.DataFrame, column_name_of_data: str, title: str) -> dict:
    plot_set = []
    labels = df["date"].unique().tolist()
    for c in df["company_name"].unique().tolist():
        comp_data = df[df["company_name"] == c]
        data = comp_data[column_name_of_data].to_list()
        if len(data) < len(labels):
            _tmp = []
            for d in labels:
                if not d in comp_data["date"].unique().tolist():
                    _tmp.append(0)
                else:
                    exsiting = (
                        comp_data[comp_data["date"] == d]
                        .iloc[0][column_name_of_data]
                        .item()
                    )
                    _tmp.append(exsiting)
            data = _tmp

        plot_set.append(
            {
                "label": c,
                "data": data,
            }
        )

    opt = {
        "scales": {"y": {"beginAtZero": "true"}},
        "plugins": {
            "title": {
                "display": "true",
                "text": title,
                "font": {"size": 30, "color": "black", "style": "italic"},
            }
        },
    }

    config = {
        "data": {
            "labels": labels,
            "datasets": plot_set,
        },
        "type": "line",
        "colorscheme": "tableau.ClassicLight10",
        "options": opt,
    }
    return config


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
        "--output", default="./www/", type=str, help="output path (defualt: ./www/)"
    )

    parser.add_argument(
        "--skip",
        default="./skip.csv",
        type=str,
        help="Path to skip file of company names to ingore (defualt: ./skip.csv)",
    )

    args = parser.parse_args()
    title = args.title
    location = args.location
    output = args.output
    input_path = args.input
    skip_file = args.skip

    skip_companies = pd.read_csv(skip_file)["company_name"].to_list()

    if not os.path.exists(output):
        os.makedirs(output)

    output = f"{output}{location}-{title}/"
    if not os.path.exists(output):
        os.makedirs(output)

    count = 0
    for file in os.listdir(input_path):
        if file.endswith(".csv") and location in file:
            count += 1

    all_jobs_dfs = []
    for file in tqdm(os.listdir(input_path)):
        if file.endswith(".csv") and location in file and file.startswith("jobs_"):
            date = file.split("_")[-1].replace(".csv", "")
            df = pd.read_csv(os.path.join(input_path, file))
            df["date"] = date
            all_jobs_dfs.append(df)

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
        jobs_over_time_grouped["job_count"] >= minimum_number_of_jobs
    ]
    jobs_over_time_grouped = jobs_over_time_grouped[
        ~jobs_over_time_grouped["company_name"].isin(skip_companies)
    ]

    config_num_job_postings = make_chartjs_config(
        jobs_over_time_grouped, "job_count", "number of job postings"
    )

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

    config_applications = make_chartjs_config(
        applications_over_time_grouped, "total_applications", "number of applications"
    )

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

    config_skipped = make_chartjs_config(jobs_over_time_grouped, "job_count", "skipped")

    charts_names = ["numjobs", "applicatons", "skipped"]
    charts_setups = [config_num_job_postings, config_applications, config_skipped]

    assert len(charts_names) == len(charts_setups), "missing config or unique name"

    html = f"""
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LinkedIn data {place} for {job_title} </title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js" integrity="sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI" crossorigin="anonymous"></script>
    </head>

    <body>
        <div class="container text-center">
          <div class="row">

            <div class="col">
            </div>

            <div class="col-8">
            <br>
            <h1 style="text-align: center;font-family: Arial, sans-serif;">
            Linkedin Job data from {place} for {job_title}</h1>
                {"<br><br>".join([f"<canvas id='{c}'></canvas>" for c in charts_names])}

            </div>

            <div class="col">
            </div>

          </div>
        </div>

        <script>
        {
            "\n".join([
            f"""
                new Chart(
                    document.getElementById('{charts_names[idx]}').getContext('2d'), 
                    {conf}
                );
            """ 
                for idx, conf in enumerate(charts_setups)
            ])
        }
        </script>

       <br>
       <br>
       <br>
       <br> 
       <br> 

    </body>

    </html>
    """.replace("True", "true")

    with open(f"{output}index.html", "w") as f:
        f.write(html)


if __name__ == "__main__":
    main()
