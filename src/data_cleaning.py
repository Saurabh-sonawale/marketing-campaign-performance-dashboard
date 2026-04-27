from pathlib import Path

import numpy as np
import pandas as pd


def safe_divide(numerator, denominator):
    return np.where(denominator == 0, 0, numerator / denominator)


def main():
    raw_path = Path("data/raw/marketing_campaign_raw.csv")
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)

    print("Loading raw marketing campaign dataset...")

    df = pd.read_csv(raw_path)

    print(f"Raw rows: {len(df):,}")
    print(f"Raw columns: {len(df.columns):,}")
    print("Raw columns:")
    for column in df.columns:
        print(f"- {column}")

    # Convert date column
    df["campaign_date"] = pd.to_datetime(df["campaign_date"], errors="coerce")

    # Remove duplicate rows
    duplicate_count = df.duplicated().sum()
    df = df.drop_duplicates()

    # Remove rows with missing campaign date
    df = df.dropna(subset=["campaign_date"])

    # Fill missing region values
    df["region"] = df["region"].fillna("Unknown")

    # Remove invalid metric rows
    df = df[
        (df["impressions"] > 0)
        & (df["clicks"] >= 0)
        & (df["spend"] >= 0)
        & (df["conversions"] >= 0)
        & (df["revenue"] >= 0)
    ]

    # Make sure numeric columns are numeric
    numeric_columns = [
        "impressions",
        "clicks",
        "spend",
        "conversions",
        "revenue",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    # Create calculated KPI columns
    df["ctr"] = safe_divide(df["clicks"], df["impressions"])
    df["cpc"] = safe_divide(df["spend"], df["clicks"])
    df["conversion_rate"] = safe_divide(df["conversions"], df["clicks"])
    df["cpa"] = safe_divide(df["spend"], df["conversions"])
    df["roas"] = safe_divide(df["revenue"], df["spend"])
    df["profit"] = df["revenue"] - df["spend"]

    # Create date columns for dashboard analysis
    df["campaign_year"] = df["campaign_date"].dt.year
    df["campaign_month"] = df["campaign_date"].dt.month
    df["campaign_month_name"] = df["campaign_date"].dt.month_name()
    df["campaign_year_month"] = df["campaign_date"].dt.to_period("M").dt.to_timestamp()
    df["campaign_day"] = df["campaign_date"].dt.day
    df["campaign_day_name"] = df["campaign_date"].dt.day_name()

    # Round calculated KPI columns
    rate_columns = ["ctr", "conversion_rate", "roas"]
    money_columns = ["spend", "revenue", "cpc", "cpa", "profit"]

    for column in rate_columns:
        df[column] = df[column].round(4)

    for column in money_columns:
        df[column] = df[column].round(2)

    # Export cleaned dataset
    cleaned_path = processed_dir / "cleaned_marketing_campaigns.csv"
    df.to_csv(cleaned_path, index=False)

    # KPI summary
    kpi_summary = pd.DataFrame(
        [
            {
                "total_spend": df["spend"].sum(),
                "total_revenue": df["revenue"].sum(),
                "total_profit": df["profit"].sum(),
                "total_impressions": df["impressions"].sum(),
                "total_clicks": df["clicks"].sum(),
                "total_conversions": df["conversions"].sum(),
                "campaign_count": df["campaign_id"].nunique(),
                "channel_count": df["channel"].nunique(),
                "region_count": df["region"].nunique(),
                "overall_ctr": df["clicks"].sum() / df["impressions"].sum(),
                "overall_cpc": df["spend"].sum() / df["clicks"].sum(),
                "overall_conversion_rate": df["conversions"].sum() / df["clicks"].sum(),
                "overall_cpa": df["spend"].sum() / df["conversions"].sum(),
                "overall_roas": df["revenue"].sum() / df["spend"].sum(),
            }
        ]
    ).round(4)

    kpi_summary.to_csv(processed_dir / "kpi_summary.csv", index=False)

    # Channel summary
    channel_summary = (
        df.groupby("channel", as_index=False)
        .agg(
            total_spend=("spend", "sum"),
            total_revenue=("revenue", "sum"),
            total_profit=("profit", "sum"),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum"),
            campaigns=("campaign_id", "nunique"),
        )
    )

    channel_summary["ctr"] = safe_divide(channel_summary["clicks"], channel_summary["impressions"])
    channel_summary["cpc"] = safe_divide(channel_summary["total_spend"], channel_summary["clicks"])
    channel_summary["conversion_rate"] = safe_divide(channel_summary["conversions"], channel_summary["clicks"])
    channel_summary["cpa"] = safe_divide(channel_summary["total_spend"], channel_summary["conversions"])
    channel_summary["roas"] = safe_divide(channel_summary["total_revenue"], channel_summary["total_spend"])

    channel_summary = channel_summary.round(4)
    channel_summary.to_csv(processed_dir / "channel_performance_summary.csv", index=False)

    # Campaign summary
    campaign_summary = (
        df.groupby(["campaign_id", "campaign_name", "channel", "objective"], as_index=False)
        .agg(
            total_spend=("spend", "sum"),
            total_revenue=("revenue", "sum"),
            total_profit=("profit", "sum"),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum"),
        )
    )

    campaign_summary["ctr"] = safe_divide(campaign_summary["clicks"], campaign_summary["impressions"])
    campaign_summary["conversion_rate"] = safe_divide(campaign_summary["conversions"], campaign_summary["clicks"])
    campaign_summary["cpa"] = safe_divide(campaign_summary["total_spend"], campaign_summary["conversions"])
    campaign_summary["roas"] = safe_divide(campaign_summary["total_revenue"], campaign_summary["total_spend"])

    campaign_summary = campaign_summary.round(4)
    campaign_summary.to_csv(processed_dir / "campaign_performance_summary.csv", index=False)

    # Monthly summary
    monthly_summary = (
        df.groupby("campaign_year_month", as_index=False)
        .agg(
            total_spend=("spend", "sum"),
            total_revenue=("revenue", "sum"),
            total_profit=("profit", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum"),
        )
    )

    monthly_summary["roas"] = safe_divide(monthly_summary["total_revenue"], monthly_summary["total_spend"])
    monthly_summary["cpa"] = safe_divide(monthly_summary["total_spend"], monthly_summary["conversions"])

    monthly_summary = monthly_summary.round(4)
    monthly_summary.to_csv(processed_dir / "monthly_performance_summary.csv", index=False)

    # Region summary
    region_summary = (
        df.groupby("region", as_index=False)
        .agg(
            total_spend=("spend", "sum"),
            total_revenue=("revenue", "sum"),
            total_profit=("profit", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum"),
        )
    )

    region_summary["roas"] = safe_divide(region_summary["total_revenue"], region_summary["total_spend"])
    region_summary = region_summary.round(4)
    region_summary.to_csv(processed_dir / "region_performance_summary.csv", index=False)

    # Device summary
    device_summary = (
        df.groupby("device", as_index=False)
        .agg(
            total_spend=("spend", "sum"),
            total_revenue=("revenue", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum"),
        )
    )

    device_summary["roas"] = safe_divide(device_summary["total_revenue"], device_summary["total_spend"])
    device_summary = device_summary.round(4)
    device_summary.to_csv(processed_dir / "device_performance_summary.csv", index=False)

    # Audience summary
    audience_summary = (
        df.groupby(["age_group", "customer_segment"], as_index=False)
        .agg(
            total_spend=("spend", "sum"),
            total_revenue=("revenue", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum"),
        )
    )

    audience_summary["roas"] = safe_divide(audience_summary["total_revenue"], audience_summary["total_spend"])
    audience_summary = audience_summary.round(4)
    audience_summary.to_csv(processed_dir / "audience_segment_summary.csv", index=False)

    print("\nData cleaning complete.")
    print(f"Duplicate rows removed: {duplicate_count:,}")
    print(f"Cleaned rows: {len(df):,}")
    print(f"Cleaned columns: {len(df.columns):,}")
    print("\nFiles created in data/processed:")
    print("- cleaned_marketing_campaigns.csv")
    print("- kpi_summary.csv")
    print("- channel_performance_summary.csv")
    print("- campaign_performance_summary.csv")
    print("- monthly_performance_summary.csv")
    print("- region_performance_summary.csv")
    print("- device_performance_summary.csv")
    print("- audience_segment_summary.csv")

    print("\nMain KPI values:")
    print(f"Total spend: ${df['spend'].sum():,.2f}")
    print(f"Total revenue: ${df['revenue'].sum():,.2f}")
    print(f"Total profit: ${df['profit'].sum():,.2f}")
    print(f"Total conversions: {df['conversions'].sum():,.0f}")
    print(f"Overall ROAS: {df['revenue'].sum() / df['spend'].sum():.2f}")


if __name__ == "__main__":
    main()