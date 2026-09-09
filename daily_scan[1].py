from sources import collect
from engine import score, qualifies
from db import upsert_jobs
from config import DAILY_TARGET

raw = collect()
unique = {}
for j in raw:
    if qualifies(j):
        j["score"] = score(j)
        old = unique.get(j["id"])
        if old is None or j["score"] > old["score"]:
            unique[j["id"]] = j

ranked = sorted(unique.values(), key=lambda x: (x["score"], x["posted"]), reverse=True)
upsert_jobs(ranked)

print("Qualifying jobs stored:", len(ranked))
print("TOP", DAILY_TARGET)
for j in ranked[:DAILY_TARGET]:
    print(f'{j["score"]:.0f} | {j["title"]} | {j["company"]} | {j["url"]}')
