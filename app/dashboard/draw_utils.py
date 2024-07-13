import time

import pandas as pd


def format_df_time(df: pd.DataFrame, time_range: float | None = None) -> pd.DataFrame:
    if time_range is not None:
        df = df[df["timestamp"] > time.time() - time_range]
    df["time"] = pd.to_datetime(df["timestamp"], unit="s")
    df.drop(columns=["timestamp"], inplace=True)
    return df
