"""Summarize the SWE-rebench-V2 task pool used by the ladder and memory experiments.

Prints: overall size, the 2025+ pool by files changed in the reference fix,
repos with at least 10 tasks, and the image registries referenced.

Usage:
    uv run --with duckdb python scripts/swerebench_pool.py
"""

import json
import urllib.request

import duckdb

DATASET = "PrimeIntellect/SWE-rebench-V2-Filtered-Verified"
PARQUET_INDEX = f"https://datasets-server.huggingface.co/parquet?dataset={DATASET}"
FILES_CHANGED = "(length(patch) - length(replace(patch, 'diff --git', ''))) / 10"


def source() -> str:
    with urllib.request.urlopen(PARQUET_INDEX) as response:
        files = json.load(response)["parquet_files"]
    urls = [f["url"] for f in files if f["split"] == "train"]
    return "read_parquet([" + ",".join(f"'{url}'" for url in urls) + "])"


def main() -> None:
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    src = source()
    total = con.execute(f"select count(*), count(distinct repo) from {src}").fetchone()
    print(f"all: {total[0]} tasks, {total[1]} repos")
    recent = con.execute(
        f"select count(*), count(distinct repo) from {src} where created_at >= '2025-01-01'"
    ).fetchone()
    print(f"2025+: {recent[0]} tasks, {recent[1]} repos")
    strata = con.execute(
        f"""
        with p as (select {FILES_CHANGED} as files from {src} where created_at >= '2025-01-01')
        select case when files <= 1 then '1 file' when files <= 4 then '2-4 files' else '5+ files' end,
               count(*)
        from p group by 1 order by 1
        """
    ).fetchall()
    for name, count in strata:
        print(f"  {name}: {count}")
    sequences = con.execute(
        f"""
        with c as (select repo, count(*) as n from {src} group by repo)
        select count(*), sum(n) from c where n >= 10
        """
    ).fetchone()
    print(f"repos with >= 10 tasks: {sequences[0]} repos, {sequences[1]} tasks")
    registries = con.execute(
        f"select split_part(image_name, '/', 1), count(*) from {src} group by 1 order by 2 desc"
    ).fetchall()
    print(f"image registries: {registries}")


if __name__ == "__main__":
    main()
