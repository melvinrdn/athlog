import os
import sys
from datetime import timedelta
from fit_utils import (
    parse_running_fit_file,
    parse_cycling_fit_file,
    parse_swimming_fit_file,
)
import pandas as pd

def format_hms(seconds):
    return str(timedelta(seconds=int(seconds)))

def analyze_8020_zones(df, lthr, print_summary=True):
    zones = {
        "Z1": (0.72, 0.81),
        "Z2": (0.81, 0.90),
        "Zx": (0.90, 0.95),
        "Z3": (0.95, 1.00),
        "Zy": (1.00, 1.02),
        "Z4": (1.02, 1.05),
        "Z5": (1.05, float("inf")),
    }

    def classify_hr(hr):
        if pd.isna(hr):
            return None
        ratio = hr / lthr
        for zone, (low, high) in zones.items():
            if low <= ratio < high:
                return zone
        return None

    df = df.copy()
    df["hr_zone"] = df["heart_rate"].apply(classify_hr)
    df["dt"] = df["timestamp"].diff().dt.total_seconds().fillna(0)

    grouped = df.groupby("hr_zone")["dt"].sum()
    total_time = grouped.sum()
    percent = (grouped / total_time * 100).round(1)

    summary_df = (
        pd.DataFrame({
            "Zone": grouped.index,
            "Time": grouped.apply(format_hms),
            "Percent": percent.values,
        })
        .sort_values("Zone")
        .reset_index(drop=True)
    )

    easy = grouped.get("Z1", 0) + grouped.get("Z2", 0)
    intense = total_time - easy

    ratio_8020 = {
        "easy_percent": round(easy / total_time * 100, 1),
        "intense_percent": round(intense / total_time * 100, 1),
        "total_time": format_hms(total_time),
    }

    if print_summary:
        print(summary_df.to_string(index=False))
        print(f"\n80/20 - Easy: {ratio_8020['easy_percent']}%  |  Intense: {ratio_8020['intense_percent']}%  |  Total: {ratio_8020['total_time']}")

    return summary_df, ratio_8020

def analyze_weekly_all_sports(folder, lthr_run=174, lthr_bike=171):
    def analyze_sport(prefix, parser, lthr, name):
        total_easy = 0
        total_intense = 0
        total_time = 0

        print("\nAnalyse des seances de", name)
        print("-" * 60)

        for fname in sorted(os.listdir(folder)):
            if not (fname.endswith(".fit") and fname.startswith(prefix)):
                continue

            fpath = os.path.join(folder, fname)

            try:
                print(f"\nAnalyse de {fname}")
                df = parser(fpath)
                _, ratio = analyze_8020_zones(df, lthr=lthr, print_summary=True)

                easy = ratio["easy_percent"] / 100
                intense = ratio["intense_percent"] / 100
                duration = pd.to_timedelta(ratio["total_time"]).total_seconds()

                total_easy += duration * easy
                total_intense += duration * intense
                total_time += duration

                print(f"Termine : {fname}")
            except Exception as e:
                print(f"Erreur avec {fname} : {e}")

        return total_easy, total_intense, total_time

    def analyze_swimming():
        total = 0
        print("\nAnalyse des seances de natation")
        print("-" * 60)
        
        for fname in sorted(os.listdir(folder)):
            if not (fname.endswith(".fit") and fname.startswith("S")):
                continue

            fpath = os.path.join(folder, fname)
            try:
                print(f"\nAnalyse de {fname}")
                df = parse_swimming_fit_file(fpath)

                if df.empty:
                    print("Aucune donnee de temps")
                    continue

                duration = (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds()
                total += duration
                print(f"Duree: {format_hms(duration)}")
            except Exception as e:
                print(f"Erreur avec {fname} : {e}")

        return total

    e_run, i_run, t_run = analyze_sport("R", parse_running_fit_file, lthr_run, "course à pied")
    e_bike, i_bike, t_bike = analyze_sport("C", parse_cycling_fit_file, lthr_bike, "cyclisme")
    t_swim = analyze_swimming()

    total_easy = e_run + e_bike
    total_intense = i_run + i_bike
    total_time_8020 = t_run + t_bike
    total_time_all = total_time_8020 + t_swim

    print("\n" + "=" * 60)
    if total_time_8020 > 0:
        easy_pct = round(total_easy / total_time_8020 * 100, 1)
        intense_pct = round(total_intense / total_time_8020 * 100, 1)
        print("Bilan global (course + velo) :")
        print(f"Easy: {easy_pct}%  |  Intense: {intense_pct}%  |  Total: {format_hms(total_time_8020)}")

    print("\nVolume total hebdo (CAP + Velo + Natation) :")
    print(f"Total: {format_hms(total_time_all)}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python analyze_week.py /chemin/vers/le_dossier")
        sys.exit(1)

    folder = sys.argv[1]
    week_name = os.path.basename(os.path.normpath(folder))  # ex: 2025-W23
    log_path = os.path.join(folder, f"rapport_{week_name}.txt")

    print(log_path)  # pour le script bash
    analyze_weekly_all_sports(folder, lthr_run=174, lthr_bike=171)