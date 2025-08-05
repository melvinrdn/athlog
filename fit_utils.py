import os
from fitparse import FitFile
import pandas as pd

def generate_activity_filename(fitfile):
    name = None
    for msg in fitfile.get_messages("workout"):
        name = msg.get_value("wkt_name")
        if name:
            break
    for msg in fitfile.get_messages("session"):
        sport = msg.get_value("sport") or "UnknownSport"
        start_time = msg.get_value("start_time")
        if start_time:
            date_str = start_time.strftime("%Y-%m-%d")
            prefix = name if name else sport.capitalize()
            return f"{prefix}_{date_str}.fit"
    return "UnknownActivity.fit"

def rename_fit_file(filepath):
    fitfile = FitFile(filepath)
    new_name = generate_activity_filename(fitfile)
    dirpath = os.path.dirname(filepath)
    new_path = os.path.join(dirpath, new_name)

    if os.path.basename(filepath) == new_name:
        print(f"Skipped (already named): {new_name}")
        return

    base, ext = os.path.splitext(new_path)
    counter = 1
    while os.path.exists(new_path):
        new_path = f"{base}_{counter}{ext}"
        counter += 1

    os.rename(filepath, new_path)
    print(f"Renamed: {os.path.basename(filepath)} to {os.path.basename(new_path)}")

def batch_rename_fit_files(folder):
    for fname in os.listdir(folder):
        if fname.lower().endswith(".fit"):
            fullpath = os.path.join(folder, fname)
            try:
                rename_fit_file(fullpath)
            except Exception as e:
                print(f"Skipped {fname} due to error: {e}")

def parse_running_fit_file(filepath):
    fitfile = FitFile(filepath)
    rows = []

    for record in fitfile.get_messages("record"):
        row = {}
        for field in record:
            if field.name and field.value is not None:
                row[field.name] = field.value
        rows.append(row)

    df = pd.DataFrame(rows)

    cols = [
        "timestamp",
        "heart_rate",
        "enhanced_speed",
        "cadence",
        "distance",
        "power",
        "position_lat",
        "position_long",
        "altitude",
        "enhanced_altitude",
    ]
    df = df[[col for col in cols if col in df.columns]]

    if "timestamp" in df.columns:
        df = df.sort_values("timestamp").reset_index(drop=True)

    if "enhanced_speed" in df.columns:
        df["pace_min_per_km"] = df["enhanced_speed"].apply(
            lambda s: (1000 / s) / 60 if s and s > 0 else None
        )

    return df

def parse_cycling_fit_file(filepath):
    fitfile = FitFile(filepath)
    records = []

    for msg in fitfile.get_messages("record"):
        record = {}
        for field in msg:
            record[field.name] = field.value
        records.append(record)

    df = pd.DataFrame(records)

    keep_cols = ["timestamp", "heart_rate", "cadence", "speed", "power"]
    df = df[[col for col in keep_cols if col in df.columns]]

    df = df.dropna(subset=["timestamp"]).copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


def parse_swimming_fit_file(filepath):
    fitfile = FitFile(filepath)
    timestamps = []

    for msg in fitfile.get_messages("record"):
        ts = msg.get_value("timestamp")
        if ts:
            timestamps.append(ts)

    if len(timestamps) < 2:
        return pd.DataFrame()  # séance vide

    df = pd.DataFrame({"timestamp": pd.to_datetime(timestamps)})
    return df



if __name__ == "__main__":
    folder_path = "/mnt/ssd/personnel/sport/backup_garmin/triathlon_prep_21-11-2025_not_completed"
    batch_rename_fit_files(folder_path)
    print("Batch renaming completed.")
