import requests
import time
import csv
from datetime import datetime, timedelta

BASE_URL = "https://a.klaviyo.com/api"
CONVERSION_METRIC_ID = "VtyFnM"

# Set timeframe for past 12 full months
today = datetime.today().replace(day=1)
start = (today - timedelta(days=365)).replace(day=1)
end = (start + timedelta(days=365)) - timedelta(days=1)
start_str = start.strftime("%Y-%m-%d")
end_str = end.strftime("%Y-%m-%d")

def HEADERS(api_key):
    return {
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "revision": "2025-04-15"
    }

def get_flows(api_key):
    url = f"{BASE_URL}/flows/"
    flows = []
    while url:
        res = requests.get(url, headers=HEADERS(api_key))
        if not res.ok:
            raise Exception(f"Failed to fetch flows: {res.status_code} - {res.text}")
        data = res.json()
        flows += data["data"]
        url = data.get("links", {}).get("next")
    return [{"id": f["id"], "name": f["attributes"]["name"]} for f in flows]

def get_metrics(api_key, flow_id):
    url = f"{BASE_URL}/flow-series-reports"
    payload = {
        "data": {
            "type": "flow-series-report",
            "attributes": {
                "filter": f"equals(flow_id,\"{flow_id}\")",
                "timeframe": {"start": start_str, "end": end_str},
                "interval": "monthly",
                "statistics": [
                    "delivered", "open_rate", "click_rate", "conversion_rate",
                    "conversion_value", "unsubscribe_rate", "bounce_rate", "spam_complaint_rate"
                ],
                "conversion_metric_id": CONVERSION_METRIC_ID
            }
        }
    }

    for attempt in range(3):
        r = requests.post(url, headers=HEADERS(api_key), json=payload)
        if r.status_code == 429:
            wait = 2 ** attempt * 60  # exponential backoff
            print(f"🛑 429 for {flow_id}. Waiting {wait} seconds...")
            time.sleep(wait)
            continue
        if r.ok:
            return r.json()["data"]["attributes"]["results"]
        else:
            print(f"❌ {r.status_code} for {flow_id}: {r.text}")
            return None

def pull_all_flow_data(api_key):
    flows = get_flows(api_key)
    fieldnames = [
        "flow_name", "flow_id", "month", "delivered", "open_rate",
        "click_rate", "conversion_rate", "revenue",
        "unsubscribe_rate", "bounce_rate", "spam_complaint_rate"
    ]

    with open("flow_metrics.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        f.flush()  # flush header immediately

        for flow in flows:
            print(f"📊 Fetching: {flow['name']} ({flow['id']})")
            metrics = get_metrics(api_key, flow["id"])

            if not metrics:
                print(f"⚠️ Skipping {flow['id']} due to no data or throttling")
                continue

            stats = metrics[0]["statistics"]
            for i in range(12):
                month = (start.month + i - 1) % 12 + 1
                year = start.year + ((start.month + i - 1) // 12)
                def safe(metric): return metric[i] if i < len(metric) else 0

                row = {
                    "flow_name": flow["name"],
                    "flow_id": flow["id"],
                    "month": f"{year}-{month:02d}",
                    "delivered": safe(stats.get("delivered", [])),
                    "open_rate": safe(stats.get("open_rate", [])) * 100,
                    "click_rate": safe(stats.get("click_rate", [])) * 100,
                    "conversion_rate": safe(stats.get("conversion_rate", [])) * 100,
                    "revenue": safe(stats.get("conversion_value", [])),
                    "unsubscribe_rate": safe(stats.get("unsubscribe_rate", [])) * 100,
                    "bounce_rate": safe(stats.get("bounce_rate", [])) * 100,
                    "spam_complaint_rate": safe(stats.get("spam_complaint_rate", [])) * 100
                }

                writer.writerow(row)
                f.flush()  # ✅ force write after each row
                print(f"✅ Writing: {row['flow_name']} - {row['month']}")

            time.sleep(2)

    return "Done"
