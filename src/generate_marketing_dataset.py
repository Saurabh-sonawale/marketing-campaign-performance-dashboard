from pathlib import Path
import random

import numpy as np
import pandas as pd


def generate_campaign_name(channel, objective, campaign_number):
    return f"{channel} {objective} Campaign {campaign_number:02d}"


def main():
    random.seed(42)
    np.random.seed(42)

    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    output_path = raw_dir / "marketing_campaign_raw.csv"

    channels = ["Google Ads", "Facebook", "Instagram", "LinkedIn", "Email", "YouTube"]
    objectives = ["Awareness", "Lead Generation", "Sales", "Retargeting"]
    regions = ["Northeast", "South", "Midwest", "West", "International"]
    devices = ["Desktop", "Mobile", "Tablet"]
    age_groups = ["18-24", "25-34", "35-44", "45-54", "55+"]
    customer_segments = ["New Customers", "Returning Customers", "High Intent", "Price Sensitive"]

    channel_profiles = {
        "Google Ads": {"ctr": 0.045, "cpc": 1.80, "conversion_rate": 0.070, "avg_order_value": 125},
        "Facebook": {"ctr": 0.032, "cpc": 1.25, "conversion_rate": 0.045, "avg_order_value": 95},
        "Instagram": {"ctr": 0.038, "cpc": 1.10, "conversion_rate": 0.040, "avg_order_value": 85},
        "LinkedIn": {"ctr": 0.024, "cpc": 3.80, "conversion_rate": 0.060, "avg_order_value": 180},
        "Email": {"ctr": 0.085, "cpc": 0.35, "conversion_rate": 0.110, "avg_order_value": 75},
        "YouTube": {"ctr": 0.020, "cpc": 1.55, "conversion_rate": 0.030, "avg_order_value": 110},
    }

    rows = []
    dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")

    campaign_id = 1001

    for channel in channels:
        for objective in objectives:
            for campaign_number in range(1, 4):
                campaign_name = generate_campaign_name(channel, objective, campaign_number)

                base_budget = np.random.randint(150, 1200)
                profile = channel_profiles[channel]

                for campaign_date in dates:
                    if np.random.random() < 0.20:
                        continue

                    region = random.choice(regions)
                    device = random.choice(devices)
                    age_group = random.choice(age_groups)
                    customer_segment = random.choice(customer_segments)

                    seasonality = 1.0
                    if campaign_date.month in [10, 11, 12]:
                        seasonality = 1.25
                    elif campaign_date.month in [1, 2]:
                        seasonality = 0.85

                    spend = max(20, np.random.normal(base_budget, base_budget * 0.20)) * seasonality

                    cpc = max(0.10, np.random.normal(profile["cpc"], profile["cpc"] * 0.15))
                    clicks = int(spend / cpc)

                    ctr = max(0.002, np.random.normal(profile["ctr"], profile["ctr"] * 0.18))
                    impressions = int(clicks / ctr)

                    conversion_rate = max(
                        0.001,
                        np.random.normal(
                            profile["conversion_rate"],
                            profile["conversion_rate"] * 0.20
                        )
                    )
                    conversions = int(clicks * conversion_rate)

                    avg_order_value = max(
                        20,
                        np.random.normal(
                            profile["avg_order_value"],
                            profile["avg_order_value"] * 0.25
                        )
                    )
                    revenue = conversions * avg_order_value

                    rows.append(
                        {
                            "campaign_date": campaign_date,
                            "campaign_id": campaign_id,
                            "campaign_name": campaign_name,
                            "channel": channel,
                            "objective": objective,
                            "region": region,
                            "device": device,
                            "age_group": age_group,
                            "customer_segment": customer_segment,
                            "impressions": impressions,
                            "clicks": clicks,
                            "spend": round(spend, 2),
                            "conversions": conversions,
                            "revenue": round(revenue, 2),
                        }
                    )

                campaign_id += 1

    df = pd.DataFrame(rows)

    # Add a few duplicate rows to make the cleaning step realistic.
    duplicate_sample = df.sample(150, random_state=42)
    df = pd.concat([df, duplicate_sample], ignore_index=True)

    # Add a few missing values to make the cleaning step realistic.
    missing_index = df.sample(80, random_state=24).index
    df.loc[missing_index, "region"] = np.nan

    df.to_csv(output_path, index=False)

    print("Synthetic marketing campaign dataset created successfully.")
    print(f"Output file: {output_path}")
    print(f"Rows created: {len(df):,}")
    print(f"Columns created: {len(df.columns):,}")
    print("Columns:")
    for column in df.columns:
        print(f"- {column}")


if __name__ == "__main__":
    main()