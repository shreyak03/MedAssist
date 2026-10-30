import requests
from agno.tools import tool
from app.config import settings

@tool
def search_pubmed(query: str, max_results: int = 5) -> str:
    """Search PubMed for medical literature. Returns titles, dates, links and available abstracts."""
    query = query.strip()[:400]
    if not query:
        return "No search query supplied."
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    params = {"db": "pubmed", "term": query, "retmax": min(max(int(max_results), 1), 5), "retmode": "json"}
    if settings.pubmed_email:
        params["email"] = settings.pubmed_email
    try:
        search = requests.get(base + "esearch.fcgi", params=params, timeout=15)
        search.raise_for_status()
        ids = search.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return "PubMed returned no matching records."
        summary = requests.get(base + "esummary.fcgi", params={"db":"pubmed","id":",".join(ids),"retmode":"json"}, timeout=15)
        summary.raise_for_status()
        result = summary.json().get("result", {})
        lines = []
        for pmid in ids:
            item = result.get(pmid, {})
            lines.append(f"Title: {item.get('title','Unavailable')}\nDate: {item.get('pubdate','Unavailable')}\nJournal: {item.get('fulljournalname','Unavailable')}\nURL: https://pubmed.ncbi.nlm.nih.gov/{pmid}/")
        return "\n\n".join(lines)
    except requests.RequestException as exc:
        return f"PubMed search unavailable: {exc}. Do not invent references."
