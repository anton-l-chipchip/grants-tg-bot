import requests
import pandas as pd
import time

URL = "https://api.grants.gov/v1/api/search2"
HEADERS = {"Content-Type": "application/json"}

ROWS = 100
start = 0
all_results = []
total_expected = None

print("\n🔎 Downloading grants...\n")

while True:
    payload = {
        "rows": ROWS,
        "startRecordNum": start,
        "oppStatuses": "posted|forecasted"
    }

    r = requests.post(URL, json=payload, headers=HEADERS)
    data = r.json().get("data", {})

    if total_expected is None:
        total_expected = data.get("hitCount", 0)
        print("Total found:", total_expected)

    opps = data.get("oppHits", [])
    if not opps:
        break

    all_results.extend(opps)
    print(f"Loaded {len(all_results)} / {total_expected}")

    start += ROWS
    time.sleep(0.25)

    if len(all_results) >= total_expected:
        break

print("\n✅ Download complete\n")

# --------------------
# CHIPCHIP SCORING
# --------------------

KEYWORDS = {
    "Agriculture & Food": ["agriculture", "food", "farmer", "crop", "nutrition", "agribusiness"],
    "Climate & Sustainability": ["climate", "environment", "water", "resilience", "sustainable"],
    "Logistics & Supply Chain": ["logistics", "transport", "warehouse", "distribution", "cold"],
    "Digital & Platforms": ["digital", "technology", "data", "platform", "e-commerce", "fintech"],
    "SME & Development": ["sme", "small business", "entrepreneur", "economic", "development"],
    "Emerging & Global": ["africa", "global", "international", "developing"]
}

def analyze(text):
    text = text.lower()
    tags = []
    score = 0

    for k, words in KEYWORDS.items():
        for w in words:
            if w in text:
                tags.append(k)
                score += 10
                break

    if "usaid" in text: score += 20
    if "usda" in text: score += 15
    if "africa" in text: score += 20

    return list(set(tags)), min(score, 100)

# --------------------
# BUILD DATASET
# --------------------

rows = []

for g in all_results:
    base_text = f"{g.get('title','')} {g.get('agency','')}"
    tags, score = analyze(base_text)

    rows.append({
        "FitScore": score,
        "Tags": ", ".join(tags),
        "Title": g.get("title"),
        "Agency": g.get("agency"),
        "AgencyCode": g.get("agencyCode"),
        "OpportunityNumber": g.get("number"),
        "Status": g.get("oppStatus"),
        "OpenDate": g.get("openDate"),
        "CloseDate": g.get("closeDate"),
        "CFDA": ", ".join(g.get("cfdaList", [])),
        "Link": f"https://www.grants.gov/search-results-detail/{g.get('id')}"
    })

df = pd.DataFrame(rows)

chipchip_df = df[
    (df["FitScore"] >= 20) |
    (df["Tags"] != "")
].sort_values("FitScore", ascending=False)

file_name = "ChipChip_Grant_Pipeline.xlsx"
chipchip_df.to_excel(file_name, index=False)

print("📁 Saved:", file_name)
print("🔥 ChipChip grant pipeline ready.")
