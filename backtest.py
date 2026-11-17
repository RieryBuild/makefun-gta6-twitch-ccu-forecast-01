"""Backtest for the GTA VI Twitch CCU forecaster (main.py).

Two out-of-sample checks, both scored with the exact pinball loss from
RULES.txt Scoring (mean over hours x levels of 2*max(tau*d, (tau-1)*d),
d = ln(y) - ln(q)):

1. Leave-one-out over the comparables: every comparable launch with a
   complete release day becomes a pseudo-case (its hour 1 as "known", its
   hours 2..24 as truth, the other comparables as its training set) and is
   forecast by main.forecast_case.  This is the honest, leakage-free check:
   the launch being forecast is never in its own training set.

2. The four practice cases (p00-p03), scored against their true release-day
   curves.  The truth files are NOT in this repository: pass their directory
   with --truth-dir.  Each file is the SullyGnome "Average viewers" series
   for the launch month, from which the release day's 24 hourly values are
   read (hour 1 is cross-checked against the case's known print).

A starter (persistence baseline) implementation is included for comparison
only; it is scored through the same code path.

Usage:
    python3 backtest.py [--kit <kit-dir>] [--truth-dir <dir>]
"""

import argparse
import json
import math
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import main as entry

Z = entry.Z
LEVELS = entry.LEVELS
KIT = Path.home() / "workspace" / "makefun-work" / "gta6-twitch-ccu-forecast-01-kit"


def parse_time(text):
    return datetime.fromisoformat(str(text).replace("Z", "+00:00"))


def pinball(truth_hours, forecast):
    """truth_hours: 23 values for hours 2..24. Returns (loss, miss%, cov)."""
    rows = {row["hour"]: row["q"] for row in forecast["hours"]}
    total = 0.0
    count = 0
    log_miss = []
    covered = 0
    for i, y in enumerate(truth_hours):
        h = i + 2
        y = max(1.0, float(y))
        qs = rows[h]
        for tau, q in zip(LEVELS, qs):
            d = math.log(y) - math.log(max(1e-9, float(q)))
            total += 2.0 * max(tau * d, (tau - 1.0) * d)
            count += 1
        log_miss.append(abs(math.log(y) - math.log(float(qs[2]))))
        if qs[0] <= y <= qs[4]:
            covered += 1
    loss = total / count
    miss = 100.0 * (math.exp(sum(log_miss) / len(log_miss)) - 1.0)
    return loss, miss, covered / len(truth_hours)


def starter_forecast(p1):
    hours = []
    for h in range(2, 25):
        qs = [entry.round2_half_up(p1 * math.exp(z * 0.15 * math.sqrt(h - 1))) for z in Z]
        hours.append({"hour": h, "q": qs})
    return {"hours": hours}


def comparable_as_case(name, day_start, hourly, others):
    """Build a pseudo-case dict for one launch, training on `others`."""
    comps = []
    for other_name, other_start, other_hourly in others:
        comps.append(
            {
                "name": other_name,
                "day_start": other_start,
                "hourly": [
                    {"from": (parse_time(other_start) + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ"), "viewers": v}
                    for i, v in enumerate(other_hourly)
                ],
            }
        )
    return {
        "known": [{"hour": 1, "viewers": hourly[0], "channels": None, "reads": 1}],
        "forecast": [{"hour": h} for h in range(2, 25)],
        "comparables": comps,
    }


def load_comparable_curves(kit_dir):
    case = json.loads((kit_dir / "input" / "p00.in").read_text(encoding="utf-8"))
    curves = []
    for comp in case["comparables"]:
        start = parse_time(comp["day_start"])
        by_hour = {}
        for point in comp["hourly"]:
            when = parse_time(point["from"])
            off = int((when - start).total_seconds() // 3600)
            if 0 <= off < 24 and point["viewers"] and point["viewers"] > 0:
                by_hour[off + 1] = float(point["viewers"])
        if len(by_hour) == 24:
            curves.append((comp["name"], comp["day_start"], [by_hour[h] for h in range(1, 25)]))
    return curves


def practice_truth(truth_dir, case_id, day):
    """Read a launch month's SullyGnome series and return release-day hours."""
    data = json.loads((Path(truth_dir) / f"{case_id}.json").read_text(encoding="utf-8"))
    labels = data["data"]["labels"]
    series = next(d for d in data["data"]["datasets"] if "Average" in d["label"])["data"]
    idx = labels.index(day + " 00:00")
    return [float(v) for v in series[idx : idx + 24]]


def run_loo(curves):
    rows = []
    for i, (name, start, hourly) in enumerate(curves):
        others = [c for j, c in enumerate(curves) if j != i]
        pseudo = comparable_as_case(name, start, hourly, others)
        t0 = time.perf_counter()
        forecast = entry.forecast_case(pseudo)
        ms = (time.perf_counter() - t0) * 1000.0
        loss, miss, cov = pinball(hourly[1:], forecast)
        s_loss, _, _ = pinball(hourly[1:], starter_forecast(hourly[0]))
        rows.append((name, hourly[0], loss, miss, cov, s_loss, ms))
    return rows


def run_practice(kit_dir, truth_dir):
    rows = []
    specs = [
        ("p00", "2026-09-15"),
        ("p01", "2018-10-26"),
        ("p02", "2022-11-09"),
        ("p03", "2023-10-20"),
    ]
    for case_id, day in specs:
        case = json.loads((kit_dir / "input" / f"{case_id}.in").read_text(encoding="utf-8"))
        truth = practice_truth(truth_dir, case_id, day)
        assert truth[0] == case["known"][0]["viewers"], f"{case_id}: truth hour 1 mismatch"
        t0 = time.perf_counter()
        forecast = entry.forecast_case(case)
        ms = (time.perf_counter() - t0) * 1000.0
        loss, miss, cov = pinball(truth[1:], forecast)
        s_loss, s_miss, s_cov = pinball(truth[1:], starter_forecast(truth[0]))
        rows.append((case_id + " " + case["game"]["name"], truth[0], loss, miss, cov, s_loss, ms))
        rows[-1] = rows[-1] + (s_miss, s_cov)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kit", default=str(KIT))
    parser.add_argument("--truth-dir", default="/tmp/practice-truth")
    args = parser.parse_args()
    kit_dir = Path(args.kit)

    curves = load_comparable_curves(kit_dir)
    print(f"comparable curves with a complete release day: {len(curves)}")
    loo = run_loo(curves)
    print("\nLEAVE-ONE-OUT over comparables (forecast vs starter, same pseudo-cases)")
    print(f"{'launch':38s} {'p1':>9s} {'loss':>7s} {'miss%':>6s} {'cov':>5s} {'starter':>7s} {'ms':>6s}")
    for name, p1, loss, miss, cov, s_loss, ms in loo:
        print(f"{name[:38]:38s} {p1:9.0f} {loss:7.4f} {miss:6.1f} {cov:5.2f} {s_loss:7.4f} {ms:6.1f}")
    mean_loss = sum(r[2] for r in loo) / len(loo)
    mean_starter = sum(r[5] for r in loo) / len(loo)
    mean_miss = sum(r[3] for r in loo) / len(loo)
    mean_cov = sum(r[4] for r in loo) / len(loo)
    print(f"LOO MEAN loss {mean_loss:.4f} (starter {mean_starter:.4f})  miss {mean_miss:.1f}%  cov {mean_cov:.3f}")

    truth_dir = Path(args.truth_dir)
    if truth_dir.is_dir():
        prac = run_practice(kit_dir, truth_dir)
        print("\nPRACTICE CASES (true SullyGnome release-day curves)")
        print(f"{'case':38s} {'p1':>9s} {'loss':>7s} {'miss%':>6s} {'cov':>5s} {'starter':>7s}")
        for row in prac:
            print(f"{row[0][:38]:38s} {row[1]:9.0f} {row[2]:7.4f} {row[3]:6.1f} {row[4]:5.2f} {row[5]:7.4f}")
        print(f"PRACTICE MEAN loss {sum(r[2] for r in prac)/len(prac):.4f} "
              f"(starter {sum(r[5] for r in prac)/len(prac):.4f})  "
              f"miss {sum(r[3] for r in prac)/len(prac):.1f}%  "
              f"cov {sum(r[4] for r in prac)/len(prac):.3f}")
    else:
        print(f"\n(truth dir {truth_dir} not found: practice scoring skipped)")


if __name__ == "__main__":
    main()
