"""Count oolong-synth questions and context windows per split, source dataset, and context length.

Reads only small columns from the Hugging Face parquet conversion over HTTP range requests.

Usage:
    uv run --with duckdb python scripts/oolong_counts.py
"""

import json
import urllib.request

import duckdb

PARQUET_INDEX = "https://datasets-server.huggingface.co/parquet?dataset=oolongbench/oolong-synth"
BUCKETS = (32768, 131072, 262144)


def parquet_urls(split: str) -> list[str]:
    with urllib.request.urlopen(PARQUET_INDEX) as response:
        files = json.load(response)["parquet_files"]
    return [f["url"] for f in files if f["split"] == split]


def main() -> None:
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    for split in ("validation", "test"):
        urls = parquet_urls(split)
        source = "read_parquet([" + ",".join(f"'{url}'" for url in urls) + "])"
        print(f"== {split}: {len(urls)} parquet files")
        totals = con.execute(
            f"""
            select dataset, count(*) as rows, count(distinct context_len) as buckets,
                   min(context_len) as shortest, max(context_len) as longest
            from {source} group by dataset order by dataset
            """
        ).fetchall()
        for row in totals:
            print("   ", row)
        buckets = ",".join(str(b) for b in BUCKETS)
        per_bucket = con.execute(
            f"""
            select dataset, context_len, count(*) as questions,
                   count(distinct context_window_id) as windows
            from {source} where context_len in ({buckets})
            group by 1, 2 order by 1, 2
            """
        ).fetchall()
        for row in per_bucket:
            print("       ", row)


if __name__ == "__main__":
    main()
