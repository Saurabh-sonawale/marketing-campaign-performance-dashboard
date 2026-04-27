from pathlib import Path

import pandas as pd


def money(value):
    return f"${value:,.2f}"


def percent(value):
    return f"{value * 100:.2f}%"


def main():
    output_dir = Path("reports/sql_outputs")
    report_path = Path("reports/business_insights.md")

    executive = pd.read_csv(output_dir / "executive_kpi_summary.csv").iloc[0]
    channel = pd.read_csv(output_dir / "channel_performance.csv")
    top_revenue_campaigns = pd.read_csv(output_dir / "top_10_campaigns_by_revenue.csv")
    top_roas_campaigns = pd.read_csv(output_dir / "top_10_campaigns_by_roas.csv")
    objective = pd.read_csv(output_dir / "objective_performance.csv")
    region = pd.read_csv(output_dir / "region_performance.csv")
    device = pd.read_csv(output_dir / "device_performance.csv")

    best_channel_revenue = channel.sort_values("total_revenue", ascending=False).iloc[0]
    best_channel_roas = channel.sort_values("roas", ascending=False).iloc[0]
    best_campaign_revenue = top_revenue_campaigns.iloc[0]
    best_campaign_roas = top_roas_campaigns.iloc[0]
    best_objective = objective.sort_values("total_revenue", ascending=False).iloc[0]
    best_region = region.sort_values("total_revenue", ascending=False).iloc[0]
    best_device = device.sort_values("total_revenue", ascending=False).iloc[0]

    report = f"""# Business Insights Report

## Marketing Campaign Performance Dashboard

This report summarizes marketing campaign performance across spend, revenue, conversions, ROAS, CPA, CTR, channels, campaigns, objectives, regions, devices, and audience segments.

---

## Executive KPI Summary

| Metric | Value |
|---|---:|
| Total Spend | {money(executive["total_spend"])} |
| Total Revenue | {money(executive["total_revenue"])} |
| Total Profit | {money(executive["total_profit"])} |
| Total Impressions | {executive["total_impressions"]:,.0f} |
| Total Clicks | {executive["total_clicks"]:,.0f} |
| Total Conversions | {executive["total_conversions"]:,.0f} |
| Total Campaigns | {executive["total_campaigns"]:,.0f} |
| Total Channels | {executive["total_channels"]:,.0f} |
| Overall ROAS | {executive["overall_roas"]:.2f} |
| Overall CTR | {percent(executive["overall_ctr"])} |
| Overall CPC | {money(executive["overall_cpc"])} |
| Overall Conversion Rate | {percent(executive["overall_conversion_rate"])} |
| Overall CPA | {money(executive["overall_cpa"])} |

---

## Key Business Insights

### 1. Email generated the strongest revenue performance

The highest revenue channel was **{best_channel_revenue["channel"]}**, generating **{money(best_channel_revenue["total_revenue"])}** in revenue from **{money(best_channel_revenue["total_spend"])}** in spend.

### 2. Email also produced the strongest ROAS

The highest ROAS channel was **{best_channel_roas["channel"]}**, with a ROAS of **{best_channel_roas["roas"]:.2f}**.

This means each dollar spent on this channel generated approximately **${best_channel_roas["roas"]:.2f}** in revenue.

### 3. The top revenue campaign was a major growth driver

The top campaign by revenue was **{best_campaign_revenue["campaign_name"]}**, generating **{money(best_campaign_revenue["total_revenue"])}**.

### 4. The highest ROAS campaign was highly efficient

The strongest campaign by ROAS was **{best_campaign_roas["campaign_name"]}**, with a ROAS of **{best_campaign_roas["roas"]:.2f}**.

### 5. Campaign objective performance was not equal

The strongest objective by revenue was **{best_objective["objective"]}**, generating **{money(best_objective["total_revenue"])}**.

### 6. Regional performance was concentrated

The highest revenue region was **{best_region["region"]}**, generating **{money(best_region["total_revenue"])}**.

### 7. Device performance showed clear differences

The strongest device category by revenue was **{best_device["device"]}**, generating **{money(best_device["total_revenue"])}**.

---

## Business Recommendations

### 1. Increase investment in high-ROAS channels

Channels with strong ROAS should receive larger budget allocation because they generate more revenue per dollar spent.

### 2. Review low-efficiency channels

Channels with lower ROAS and higher CPA should be reviewed for targeting, creative quality, landing page performance, and audience fit.

### 3. Prioritize high-performing campaigns

Campaigns that generate both high revenue and strong ROAS should be used as benchmarks for future campaign planning.

### 4. Optimize campaign objectives

Objectives with stronger revenue and conversion performance should receive more attention in budget planning.

### 5. Use regional insights for targeting

Regions with higher revenue and conversion volume should be prioritized for localized messaging and budget allocation.

### 6. Compare device-level performance

Device performance should be monitored to optimize ad creative, landing pages, and bid strategy by device type.

---

## Skills Demonstrated

- Python data cleaning
- Synthetic dataset generation
- SQL analysis
- SQLite database creation
- Marketing KPI development
- ROAS analysis
- CPA and CPC analysis
- CTR and conversion rate analysis
- Channel performance analysis
- Campaign performance analysis
- Regional and device-level analysis
- Business insight communication

---

## Next Step

The next phase is to build an interactive Power BI dashboard using the cleaned marketing campaign dataset.
"""

    report_path.write_text(report, encoding="utf-8")

    print("Business insights report created successfully.")
    print(f"Report path: {report_path}")


if __name__ == "__main__":
    main()