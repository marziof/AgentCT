import requests
from collections import Counter

QUERY = "moderate alcohol consumption cardiovascular"  # edit to test other queries
PAGE_SIZE = 20

url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
params = {
    "query": QUERY,          # note: no OPEN_ACCESS / HAS_FT filter
    "format": "json",
    "resultType": "core",
    "pageSize": PAGE_SIZE,
}

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
except Exception as e:
    raise SystemExit(f"Europe PMC request failed: {type(e).__name__}: {e}")

data = response.json()
records = data.get("resultList", {}).get("result", [])
print(f"Query: {QUERY!r} | hitCount: {data.get('hitCount')} | returned: {len(records)}\n")

n_abstract = n_pmcid = n_oa = 0
pubtypes, sources = Counter(), Counter()

for i, r in enumerate(records, 1):
    abstract = r.get("abstractText") or ""
    types = (r.get("pubTypeList") or {}).get("pubType") or []
    journal = ((r.get("journalInfo") or {}).get("journal") or {}).get("title", "")

    n_abstract += bool(abstract)
    n_pmcid += bool(r.get("pmcid"))
    n_oa += r.get("isOpenAccess") == "Y"
    sources[r.get("source")] += 1
    pubtypes.update(types)

    print(
        f"{i:>2}. {(r.get('title') or '')[:70]}\n"
        f"    src={r.get('source')} pmid={r.get('pmid')} pmcid={r.get('pmcid')} doi={r.get('doi')}\n"
        f"    types={types} abstract_len={len(abstract)} OA={r.get('isOpenAccess')} "
        f"cited={r.get('citedByCount')} year={r.get('pubYear')} journal={journal[:40]}\n"
    )

print("=== SUMMARY ===")
print(f"with abstract: {n_abstract}/{len(records)}")
print(f"with PMCID:    {n_pmcid}/{len(records)}")
print(f"open access:   {n_oa}/{len(records)}")
print(f"source codes:  {dict(sources)}")
print(f"pub types:     {dict(pubtypes)}")