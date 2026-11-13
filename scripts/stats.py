#!/usr/bin/env python3
"""Read Fileloka's anonymous counters from Workers Analytics Engine.

    export CF_ACCOUNT_ID=...     # Cloudflare dashboard, right-hand sidebar
    export CF_API_TOKEN=...      # API token with "Account Analytics: Read"
    python3 scripts/stats.py           # last 7 days
    python3 scripts/stats.py 30        # last 30 days

No dependencies. Rows are written by functions/api/e.js as
blob1=event, blob2=tool or slot, blob3=path, blob4=lang, blob5=country, blob6=device.
Counts use SUM(_sample_interval), which stays correct if Cloudflare samples.
"""
import json
import os
import sys
import urllib.error
import urllib.request

DATASET = os.environ.get("CF_DATASET", "fileloka_events")


def query(sql):
    acct, token = os.environ.get("CF_ACCOUNT_ID"), os.environ.get("CF_API_TOKEN")
    if not acct or not token:
        sys.exit("Set CF_ACCOUNT_ID and CF_API_TOKEN first (see the top of this file).")
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{acct}/analytics_engine/sql",
        data=(sql + " FORMAT JSON").encode(),
        headers={"Authorization": f"Bearer {token}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r).get("data", [])
    except urllib.error.HTTPError as e:
        sys.exit(f"Cloudflare answered {e.code}: {e.read().decode(errors='replace')[:400]}")


def table(title, rows, cols):
    print(f"\n{title}")
    if not rows:
        print("  (no data yet)")
        return
    widths = [max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in cols]
    print("  " + "  ".join(c.upper().ljust(w) for c, w in zip(cols, widths)))
    for r in rows:
        print("  " + "  ".join(str(r.get(c, "")).ljust(w) for c, w in zip(cols, widths)))


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    if not 1 <= days <= 90:
        sys.exit("Days must be between 1 and 90.")
    since = f"timestamp > NOW() - INTERVAL '{days}' DAY"
    n = "SUM(_sample_interval) AS n"
    print(f"Fileloka, last {days} days  (dataset: {DATASET})")

    table("Events", query(
        f"SELECT blob1 AS event, {n} FROM {DATASET} WHERE {since} GROUP BY event ORDER BY n DESC"),
        ["event", "n"])
    table("Most opened pages", query(
        f"SELECT blob3 AS path, {n} FROM {DATASET} WHERE {since} AND blob1 = 'pv' GROUP BY path ORDER BY n DESC LIMIT 15"),
        ["path", "n"])
    table("Tools that finished a job", query(
        f"SELECT blob2 AS tool, {n} FROM {DATASET} WHERE {since} AND blob1 = 'use' GROUP BY tool ORDER BY n DESC LIMIT 15"),
        ["tool", "n"])
    table("Clicks on the money slot", query(
        f"SELECT blob2 AS slot, blob3 AS path, {n} FROM {DATASET} WHERE {since} AND blob1 = 'out' GROUP BY slot, path ORDER BY n DESC LIMIT 15"),
        ["slot", "path", "n"])
    table("Countries (page views)", query(
        f"SELECT blob5 AS country, {n} FROM {DATASET} WHERE {since} AND blob1 = 'pv' GROUP BY country ORDER BY n DESC LIMIT 10"),
        ["country", "n"])
    table("Phone vs computer (page views)", query(
        f"SELECT blob6 AS device, {n} FROM {DATASET} WHERE {since} AND blob1 = 'pv' GROUP BY device ORDER BY n DESC"),
        ["device", "n"])
    print("\npv = page opened, open = tool opened from the home page, use = tool finished,")
    print("dl = download clicked, out = money slot clicked. use / pv per tool page is the number to watch.")


if __name__ == "__main__":
    main()
