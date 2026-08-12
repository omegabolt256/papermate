"""Unpaywall client – find open-access PDFs by DOI."""
import requests
from config.settings import PUBMED_EMAIL  # reuse your email for politeness

def find_open_access_pdf(doi: str) -> str:
    """Return OA PDF URL if available, else empty string."""
    if not doi:
        return ""
    try:
        email = PUBMED_EMAIL or "user@example.com"
        url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            best = data.get("best_oa_location") or {}
            pdf_url = best.get("url_for_pdf", "")
            if pdf_url:
                return pdf_url
    except:
        pass
    return ""