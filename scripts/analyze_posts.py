#!/usr/bin/env python3
"""Analyze creator posts against rolling personal baselines.

Usage:
    python scripts/analyze_posts.py POST_LOG.csv

Design choices:
- Standard library only.
- Baseline = up to 10 earlier posts with the same platform and format.
- Uses medians to reduce distortion from one viral post.
- Does not claim to infer platform algorithms.
- Heuristic anomaly labels are prompts for review, not causal conclusions.
"""

from __future__ import annotations

import csv
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

NUMERIC_FIELDS = {
    "views",
    "impressions",
    "clicks",
    "likes",
    "saves",
    "comments",
    "shares",
    "follows",
    "profile_visits",
    "leads",
    "sales",
    "avg_watch_seconds",
    "high_intent_comments",
}
PERCENT_FIELDS = {"completion_rate"}
DERIVED_METRICS = [
    "views",
    "ctr",
    "completion_rate",
    "save_rate",
    "comment_rate",
    "high_intent_comment_rate",
    "share_rate",
    "follow_rate",
    "intent_rate",
]


def to_float(value: str | None, *, percent: bool = False) -> Optional[float]:
    if value is None:
        return None
    raw = value.strip()
    if raw == "":
        return None
    had_percent = raw.endswith("%")
    raw = raw.replace(",", "").removesuffix("%")
    try:
        number = float(raw)
    except ValueError:
        return None
    if percent and (had_percent or number > 1):
        return number / 100.0
    return number


def safe_rate(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def median(values: Iterable[Optional[float]]) -> Optional[float]:
    clean = [value for value in values if value is not None]
    return statistics.median(clean) if clean else None


def ratio(value: Optional[float], baseline: Optional[float]) -> Optional[float]:
    if value is None or baseline in (None, 0):
        return None
    return value / baseline


def parse_date(value: object) -> datetime:
    text = str(value or "")
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    return datetime.max


def load_rows(path: Path) -> List[Dict[str, object]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row")

        rows: List[Dict[str, object]] = []
        for position, raw in enumerate(reader):
            row: Dict[str, object] = dict(raw)
            row["_position"] = position
            for field in NUMERIC_FIELDS:
                row[field] = to_float(raw.get(field))
            for field in PERCENT_FIELDS:
                row[field] = to_float(raw.get(field), percent=True)

            views = row.get("views") if isinstance(row.get("views"), (int, float)) else None
            impressions = row.get("impressions") if isinstance(row.get("impressions"), (int, float)) else None
            clicks = row.get("clicks") if isinstance(row.get("clicks"), (int, float)) else None
            likes = row.get("likes") if isinstance(row.get("likes"), (int, float)) else None
            saves = row.get("saves") if isinstance(row.get("saves"), (int, float)) else None
            comments = row.get("comments") if isinstance(row.get("comments"), (int, float)) else None
            high_intent_comments = (
                row.get("high_intent_comments")
                if isinstance(row.get("high_intent_comments"), (int, float))
                else None
            )
            shares = row.get("shares") if isinstance(row.get("shares"), (int, float)) else None
            follows = row.get("follows") if isinstance(row.get("follows"), (int, float)) else None

            row["ctr"] = safe_rate(clicks, impressions)
            row["like_rate"] = safe_rate(likes, views)
            row["save_rate"] = safe_rate(saves, views)
            row["comment_rate"] = safe_rate(comments, views)
            row["high_intent_comment_rate"] = safe_rate(high_intent_comments, views)
            row["share_rate"] = safe_rate(shares, views)
            row["follow_rate"] = safe_rate(follows, views)
            intent_total = sum(value or 0.0 for value in (saves, comments, shares, follows))
            row["intent_rate"] = safe_rate(intent_total, views)
            rows.append(row)

    rows.sort(key=lambda item: (parse_date(item.get("date")), int(item.get("_position", 0))))
    return rows


def comparable_key(row: Dict[str, object]) -> str:
    return f"{row.get('platform') or 'unknown'}::{row.get('format') or 'unknown'}"


def classify_anomalies(performance: Dict[str, Dict[str, Optional[float]]]) -> List[str]:
    def r(metric: str) -> Optional[float]:
        return performance.get(metric, {}).get("ratio_to_baseline")

    anomalies: List[str] = []
    ctr = r("ctr")
    completion = r("completion_rate")
    views = r("views")
    saves = r("save_rate")
    deep_comments = r("high_intent_comment_rate")
    intent = r("intent_rate")
    follow = r("follow_rate")

    if ctr is not None and completion is not None:
        if ctr >= 1.25 and completion <= 0.80:
            anomalies.append("HIGH_ENTRY_LOW_CONSUMPTION")
        if ctr <= 0.80 and completion >= 1.25:
            anomalies.append("LOW_ENTRY_HIGH_CONSUMPTION")
    if views is not None and intent is not None and views >= 1.50 and intent <= 0.75:
        anomalies.append("HIGH_REACH_LOW_INTENT")
    if saves is not None and saves >= 1.50 and (
        (ctr is not None and ctr <= 0.80) or (views is not None and views <= 0.80)
    ):
        anomalies.append("LOW_ENTRY_HIGH_SAVE")
    if deep_comments is not None and deep_comments >= 1.50 and (
        views is None or 0.80 <= views <= 1.25
    ):
        anomalies.append("NORMAL_REACH_DEEP_COMMENTS")
    if intent is not None and intent >= 1.50:
        anomalies.append("HIGH_INTENT_SIGNAL")
    if follow is not None and follow >= 1.50:
        anomalies.append("HIGH_FOLLOW_CONVERSION")
    return anomalies


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python analyze_posts.py POST_LOG.csv", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    try:
        rows = load_rows(path)
    except (OSError, ValueError) as exc:
        print(f"Could not read CSV: {exc}", file=sys.stderr)
        return 2

    if not rows:
        print(json.dumps({"posts": 0, "message": "No post rows found."}, ensure_ascii=False, indent=2))
        return 0

    history: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    analyzed_posts: List[Dict[str, object]] = []

    for row in rows:
        key = comparable_key(row)
        prior = history[key][-10:]
        baseline = {
            metric: median(
                item.get(metric) if isinstance(item.get(metric), (int, float)) else None
                for item in prior
            )
            for metric in DERIVED_METRICS
        }

        performance: Dict[str, Dict[str, Optional[float]]] = {}
        for metric in DERIVED_METRICS:
            value = row.get(metric) if isinstance(row.get(metric), (int, float)) else None
            performance[metric] = {
                "value": value,
                "baseline_median": baseline[metric],
                "ratio_to_baseline": ratio(value, baseline[metric]),
            }

        analyzed_posts.append(
            {
                "post_id": row.get("post_id"),
                "date": row.get("date"),
                "platform": row.get("platform"),
                "format": row.get("format"),
                "node_id": row.get("node_id"),
                "pillar": row.get("pillar"),
                "angle": row.get("angle"),
                "title": row.get("title"),
                "comparable_prior_posts": len(prior),
                "small_sample_warning": len(prior) < 5,
                "performance": performance,
                "anomalies": classify_anomalies(performance),
            }
        )
        history[key].append(row)

    pillar_items: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    node_items: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    for item in analyzed_posts:
        pillar_items[str(item.get("pillar") or "unassigned")].append(item)
        node_items[str(item.get("node_id") or "unassigned")].append(item)

    def summarize(items: List[Dict[str, object]]) -> Dict[str, object]:
        ratios: List[float] = []
        for item in items:
            performance = item.get("performance")
            if not isinstance(performance, dict):
                continue
            intent = performance.get("intent_rate")
            if isinstance(intent, dict):
                value = intent.get("ratio_to_baseline")
                if isinstance(value, (int, float)):
                    ratios.append(float(value))
        strong = sum(value >= 1.25 for value in ratios)
        return {
            "post_count": len(items),
            "comparable_post_count": len(ratios),
            "median_intent_ratio": median(ratios),
            "posts_above_1_25x_intent_baseline": strong,
            "repeatable_signal": len(ratios) >= 2 and strong >= 2,
            "note": "Repeatable signal is a review prompt, not proof of platform causality.",
        }

    output = {
        "posts": len(rows),
        "baseline_method": "rolling median of up to 10 earlier posts with the same platform and format",
        "pillar_summary": {key: summarize(items) for key, items in pillar_items.items()},
        "node_summary": {key: summarize(items) for key, items in node_items.items()},
        "post_analysis": analyzed_posts,
        "heuristic_note": "1.25x and 0.80x labels are anomaly prompts, not universal success thresholds.",
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
