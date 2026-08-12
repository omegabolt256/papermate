"""Smart PDF downloader – tries open access, then Unpaywall, then gives browser link."""
import os, re, time, requests
from pathlib import Path
from .unpaywall import find_open_access_pdf

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
HEADERS = {"User-Agent": USER_AGENT}

class PaperDownloader:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def download(self, paper, filename: str = None) -> tuple:
        """
        Returns (success: bool, message: str, filepath: str).
        Tries: 1) given pdf_url, 2) Unpaywall by DOI, 3) arXiv mirror.
        """
        title = re.sub(r'[^\w\s-]', '', str(getattr(paper, 'title', 'paper')))[:60]
        title = re.sub(r'\s+', '_', title)
        year = str(getattr(paper, 'year', 'unknown') or 'unknown')
        year_dir = self.base_dir / year
        year_dir.mkdir(parents=True, exist_ok=True)
        if not filename:
            filename = f"{title}.pdf"
        filepath = year_dir / filename
        if filepath.exists():
            return True, "Already downloaded", str(filepath)

        # Collect URLs to try
        urls = []
        # 1. Direct PDF URL from metadata (arXiv, PMC)
        direct_url = getattr(paper, 'pdf_url', '')
        if direct_url:
            urls.append(("direct", direct_url))

        # 2. Unpaywall by DOI
        doi = getattr(paper, 'doi', '')
        if doi:
            oa_url = find_open_access_pdf(doi)
            if oa_url:
                urls.append(("Unpaywall", oa_url))

        # 3. arXiv ID fallback
        arxiv_id = None
        if hasattr(paper, 'arxiv_id') and paper.arxiv_id:
            arxiv_id = paper.arxiv_id
        else:
            # Try to extract from URL
            url = getattr(paper, 'url', '') or direct_url
            if 'arxiv.org' in url:
                m = re.search(r'abs/([^v]+)', url)
                if m: arxiv_id = m.group(1)
        if arxiv_id:
            urls.append(("arXiv", f"https://arxiv.org/pdf/{arxiv_id}.pdf"))

        if not urls:
            return False, "No download source", ""

        # Try each URL
        for source, url in urls:
            try:
                time.sleep(1)
                resp = requests.get(url, timeout=30, stream=True, headers=HEADERS)
                if resp.status_code == 200 and len(resp.content) > 5000:
                    if resp.content.startswith(b'%PDF'):
                        with open(filepath, "wb") as f:
                            for chunk in resp.iter_content(8192):
                                f.write(chunk)
                        return True, f"OK via {source} ({len(resp.content)//1024}KB)", str(filepath)
                    else:
                        continue  # not a real PDF, try next
                else:
                    continue
            except:
                continue

        # All failed – give user the browser link
        doi_link = f"https://doi.org/{doi}" if doi else getattr(paper, 'url', '')
        return False, f"Open in browser: {doi_link}" if doi_link else "No access", ""
    
    def download_batch(self, papers, delay: float = 2.0) -> dict:
        results = {"success": 0, "failed": 0, "skipped": 0}
        for i, paper in enumerate(papers):
            print(f"  [{i+1}/{len(papers)}] ", end="")
            s, m, path = self.download(paper)
            title = str(getattr(paper, 'title', ''))[:50]
            print(f"{title}... -> {m}")
            if "Already" in m: results["skipped"] += 1
            elif s: results["success"] += 1
            else: results["failed"] += 1
            if i < len(papers): time.sleep(delay)
        return results