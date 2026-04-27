from pathlib import Path
import sqlite3

import pandas as pd


def run_query(connection, query, output_path):
    df = pd.read_sql_query(query, connection)
    df.to_csv(output_path, index=False)
    print(f"Created: {output_path.name} | Shape: {df.shape}")


def main():
    db_path = Path("data/processed/marketing_campaigns.db")
    output_dir = Path("reports/sql_outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not db_path.exists():
        raise FileNotFoundError(
            "marketing_campaigns.db not found. Run src/create_sqlite_database.py first."
        )

    connection = sqlite3.connect(db_path)

    queries = {
        "executive_kpi_summary.csv": """
            SELECT
                ROUND(SUM(spend), 2) AS total_spend,
                ROUND(SUM(revenue), 2) AS total_revenue,
                ROUND(SUM(profit), 2) AS total_profit,
                SUM(impressions) AS total_impressions,
                SUM(clicks) AS total_clicks,
                SUM(conversions) AS total_conversions,
                COUNT(DISTINCT campaign_id) AS total_campaigns,
                COUNT(DISTINCT channel) AS total_channels,
                ROUND(SUM(revenue) / SUM(spend), 2) AS overall_roas,
                ROUND(SUM(clicks) * 1.0 / SUM(impressions), 4) AS overall_ctr,
                ROUND(SUM(spend) * 1.0 / SUM(clicks), 2) AS overall_cpc,
                ROUND(SUM(conversions) * 1.0 / SUM(clicks), 4) AS overall_conversion_rate,
                ROUND(SUM(spend) * 1.0 / SUM(conversions), 2) AS overall_cpa
            FROM cleaned_marketing_campaigns;
        """,

        "monthly_performance_trend.csv": """
            SELECT
                campaign_year_month,
                ROUND(SUM(spend), 2) AS total_spend,
                ROUND(SUM(revenue), 2) AS total_revenue,
                ROUND(SUM(profit), 2) AS total_profit,
                SUM(clicks) AS total_clicks,
                SUM(conversions) AS total_conversions,
                ROUND(SUM(revenue) / SUM(spend), 2) AS roas,
                ROUND(SUM(spend) * 1.0 / SUM(conversions), 2) AS cpa
            FROM cleaned_marketing_campaigns
            GROUP BY campaign_year_month
            ORDER BY campaign_year_month;
        """,

        "channel_performance.csv": """
            SELECT
                channel,
                ROUND(SUM(spend), 2) AS total_spend,
                ROUND(SUM(revenue), 2) AS total_revenue,
                ROUND(SUM(profit), 2) AS total_profit,
                SUM(impressions) AS impressions,
                SUM(clicks) AS clicks,
                SUM(conversions) AS conversions,
                COUNT(DISTINCT campaign_id) AS campaigns,
                ROUND(SUM(revenue) / SUM(spend), 2) AS roas,
                ROUND(SUM(clicks) * 1.0 / SUM(impressions), 4) AS ctr,
                ROUND(SUM(spend) * 1.0 / SUM(clicks), 2) AS cpc,
                ROUND(SUM(conversions) * 1.0 / SUM(clicks), 4) AS conversion_rate,
                ROUND(SUM(spend) * 1.0 / SUM(conversions), 2) AS cpa
            FROM cleaned_marketing_campaigns
            GROUP BY channel
            ORDER BY total_revenue DESC;
        """,

        "top_10_campaigns_by_revenue.csv": """
            SELECT
                campaign_name,
                channel,
                objective,
                ROUND(SUM(spend), 2) AS total_spend,
                ROUND(SUM(revenue), 2) AS total_revenue,
                ROUND(SUM(profit), 2) AS total_profit,
                SUM(conversions) AS conversions,
                ROUND(SUM(revenue) / SUM(spend), 2) AS roas,
                ROUND(SUM(spend) * 1.0 / SUM(conversions), 2) AS cpa
            FROM cleaned_marketing_campaigns
            GROUP BY campaign_name, channel, objective
            ORDER BY total_revenue DESC
            LIMIT 10;
        """,

        "top_10_campaigns_by_roas.csv": """
            SELECT
                campaign_name,
                channel,
                objective,
                ROUND(SUM(spend), 2) AS total_spend,
                ROUND(SUM(revenue), 2) AS total_revenue,
                ROUND(SUM(profit), 2) AS total_profit,
                SUM(conversions) AS conversions,
                ROUND(SUM(revenue) / SUM(spend), 2) AS roas,
                ROUND(SUM(spend) * 1.0 / SUM(conversions), 2) AS cpa
            FROM cleaned_marketing_campaigns
            GROUP BY campaign_name, channel, objective
            HAVING SUM(spend) >= 10000
            ORDER BY roas DESC
            LIMIT 10;
        """,

        "objective_performance.csv": """
            SELECT
                objective,
                ROUND(SUM(spend), 2) AS total_spend,
                ROUND(SUM(revenue), 2) AS total_revenue,
                ROUND(SUM(profit), 2) AS total_profit,
                SUM(clicks) AS clicks,
                SUM(conversions) AS conversions,
                ROUND(SUM(revenue) / SUM(spend), 2) AS roas,
                ROUND(SUM(spend) * 1.0 / SUM(conversions), 2) AS cpa,
                ROUND(SUM(conversions) * 1.0 / SUM(clicks), 4) AS conversion_rate
            FROM cleaned_marketing_campaigns
            GROUP BY objective
            ORDER BY total_revenue DESC;
        """,

        "region_performance.csv": """
            SELECT
                region,
                ROUND(SUM(spend), 2) AS total_spend,
                ROUND(SUM(revenue), 2) AS total_revenue,
                ROUND(SUM(profit), 2) AS total_profit,
                SUM(clicks) AS clicks,
                SUM(conversions) AS conversions,
                ROUND(SUM(revenue) / SUM(spend), 2) AS roas,
                ROUND(SUM(spend) * 1.0 / SUM(conversions), 2) AS cpa
            FROM cleaned_marketing_campaigns
            GROUP BY region
            ORDER BY total_revenue DESC;
        """,

        "device_performance.csv": """
            SELECT
                device,
                ROUND(SUM(spend), 2) AS total_spend,
                ROUND(SUM(revenue), 2) AS total_revenue,
                SUM(clicks) AS clicks,
                SUM(conversions) AS conversions,
                ROUND(SUM(revenue) / SUM(spend), 2) AS roas,
                ROUND(SUM(conversions) * 1.0 / SUM(clicks), 4) AS conversion_rate
            FROM cleaned_marketing_campaigns
            GROUP BY device
            ORDER BY total_revenue DESC;
        """,

        "audience_segment_performance.csv": """
            SELECT
                age_group,
                customer_segment,
                ROUND(SUM(spend), 2) AS total_spend,
                ROUND(SUM(revenue), 2) AS total_revenue,
                SUM(clicks) AS clicks,
                SUM(conversions) AS conversions,
                ROUND(SUM(revenue) / SUM(spend), 2) AS roas,
                ROUND(SUM(spend) * 1.0 / SUM(conversions), 2) AS cpa
            FROM cleaned_marketing_campaigns
            GROUP BY age_group, customer_segment
            ORDER BY total_revenue DESC;
        """
    }

    print("Running SQL analysis queries...\n")

    for file_name, query in queries.items():
        output_path = output_dir / file_name
        run_query(connection, query, output_path)

    connection.close()

    print("\nSQL analysis complete.")
    print("Files created in reports/sql_outputs.")


if __name__ == "__main__":
    main()