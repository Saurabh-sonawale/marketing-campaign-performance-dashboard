from pathlib import Path
import sqlite3

import pandas as pd


def load_csv_to_table(connection, csv_path, table_name):
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, connection, if_exists="replace", index=False)
    print(f"Table created: {table_name} | Rows: {len(df):,}")


def main():
    processed_dir = Path("data/processed")
    db_path = processed_dir / "marketing_campaigns.db"

    cleaned_path = processed_dir / "cleaned_marketing_campaigns.csv"

    if not cleaned_path.exists():
        raise FileNotFoundError(
            "cleaned_marketing_campaigns.csv not found. Run src/data_cleaning.py first."
        )

    print("Creating SQLite database...")
    print(f"Database path: {db_path}")

    connection = sqlite3.connect(db_path)

    csv_tables = {
        "cleaned_marketing_campaigns.csv": "cleaned_marketing_campaigns",
        "kpi_summary.csv": "kpi_summary",
        "channel_performance_summary.csv": "channel_performance_summary",
        "campaign_performance_summary.csv": "campaign_performance_summary",
        "monthly_performance_summary.csv": "monthly_performance_summary",
        "region_performance_summary.csv": "region_performance_summary",
        "device_performance_summary.csv": "device_performance_summary",
        "audience_segment_summary.csv": "audience_segment_summary",
    }

    for csv_file, table_name in csv_tables.items():
        csv_path = processed_dir / csv_file
        if csv_path.exists():
            load_csv_to_table(connection, csv_path, table_name)
        else:
            print(f"Skipped missing file: {csv_file}")

    print("\nDatabase validation summary:")

    validation_queries = {
        "row_count": """
            SELECT COUNT(*) 
            FROM cleaned_marketing_campaigns;
        """,
        "total_spend": """
            SELECT ROUND(SUM(spend), 2) 
            FROM cleaned_marketing_campaigns;
        """,
        "total_revenue": """
            SELECT ROUND(SUM(revenue), 2) 
            FROM cleaned_marketing_campaigns;
        """,
        "total_profit": """
            SELECT ROUND(SUM(profit), 2) 
            FROM cleaned_marketing_campaigns;
        """,
        "total_conversions": """
            SELECT SUM(conversions) 
            FROM cleaned_marketing_campaigns;
        """,
        "campaign_count": """
            SELECT COUNT(DISTINCT campaign_id) 
            FROM cleaned_marketing_campaigns;
        """,
        "channel_count": """
            SELECT COUNT(DISTINCT channel) 
            FROM cleaned_marketing_campaigns;
        """,
    }

    for metric_name, query in validation_queries.items():
        value = connection.execute(query).fetchone()[0]
        print(f"- {metric_name}: {value}")

    print("\nTop 5 channels by revenue:")

    top_channels = connection.execute(
        """
        SELECT
            channel,
            ROUND(SUM(revenue), 2) AS total_revenue,
            ROUND(SUM(spend), 2) AS total_spend,
            ROUND(SUM(revenue) / SUM(spend), 2) AS roas
        FROM cleaned_marketing_campaigns
        GROUP BY channel
        ORDER BY total_revenue DESC
        LIMIT 5;
        """
    ).fetchall()

    for channel, revenue, spend, roas in top_channels:
        print(f"- {channel}: Revenue ${revenue:,.2f} | Spend ${spend:,.2f} | ROAS {roas}")

    connection.close()

    print("\nSQLite database created successfully:")
    print(f"- {db_path}")


if __name__ == "__main__":
    main()