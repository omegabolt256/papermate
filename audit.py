#!/usr/bin/env python3
"""
PaperMate — Strict Usability & Functionality Audit
Scores each component 0-100. Fails if any critical issue found.
"""
import sys, time, os, json, tempfile, shutil
sys.path.insert(0, '.')

RESULTS = []
CRITICAL_FAILURES = []

def score(name, points, max_points, notes=""):
    pct = (points / max_points) * 100 if max_points > 0 else 0
    RESULTS.append({"component": name, "points": points, "max": max_points, "pct": pct, "notes": notes})
    status = "PASS" if pct >= 60 else "FAIL"
    print(f"  [{status}] {name}: {points}/{max_points} ({pct:.0f}%) {notes}")
    if pct < 60:
        CRITICAL_FAILURES.append(name)

print('='*60)
print('PAPERMATE STRICT AUDIT')
print('='*60)

# ==================== 1. IMPORTS ====================
print('\n1. IMPORTS (20pts)')
pts = 20
try:
    from app.projects import ProjectManager
    from app.chats import ChatManager
    from app.search.engine import SearchEngine
    from app.models import get_model_provider
    from app.papers import PaperManager
    from app.papers.downloader import PaperDownloader
    from app.papers.unpaywall import find_open_access_pdf
except Exception as e:
    pts = 0
    notes = str(e)
score("Imports", pts, 20, notes if pts == 0 else "All modules importable")

# ==================== 2. SEARCH SOURCES ====================
print('\n2. SEARCH SOURCES (20pts)')
import requests
sources = {
    'PubMed': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=test&retmax=1&retmode=json',
    'Europe PMC': 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=test&pageSize=1&format=json',
    'OpenAlex': 'https://api.openalex.org/works?search=test&per_page=1',
    'arXiv': 'http://export.arxiv.org/api/query?search_query=all:test&max_results=1'
}
working = 0
for name, url in sources.items():
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            working += 1
            print(f"    OK: {name}")
        else:
            print(f"    FAIL: {name} (HTTP {r.status_code})")
    except Exception as e:
        print(f"    FAIL: {name} ({str(e)[:30]})")
    time.sleep(0.3)
pts = working * 5
score("Search Sources", pts, 20, f"{working}/4 sources working")

# ==================== 3. PROJECT CRUD ====================
print('\n3. PROJECT CRUD (15pts)')
pts = 15
try:
    pm = ProjectManager()
    p = pm.create_project('_TEST_A_')
    assert p.name == '_TEST_A_'
    stats = pm.get_project_stats(p.id)
    assert 'paper_count' in stats
    pm.rename_project(p.id, '_TEST_B_')
    p2 = pm.repo.get(p.id)
    assert p2.name == '_TEST_B_'
    pm.delete_project(p.id)
    assert pm.repo.get(p.id) is None
    print("    Create/Rename/Stats/Delete all pass")
except Exception as e:
    pts = 0
    print(f"    FAIL: {e}")
score("Project CRUD", pts, 15)

# ==================== 4. PAPER OPERATIONS ====================
print('\n4. PAPER OPERATIONS (15pts)')
pts = 15
try:
    pm = ProjectManager()
    p = pm.create_project('_P_TEST_')
    paper_mgr = PaperManager()
    paper_mgr.add_paper(p.id, {'title':'Test Paper','authors':'Author A','year':'2024','source':'test'})
    papers = paper_mgr.get_project_papers(p.id)
    assert len(papers) == 1
    paper_mgr.add_tag(papers[0].id, 'test-tag')
    paper_mgr.mark_read_status(papers[0].id, 'read')
    paper_mgr.update_screening(papers[0].id, 'included')
    p_refresh = paper_mgr.get_paper(papers[0].id)
    assert p_refresh.read_status == 'read'
    assert p_refresh.screening_status == 'included'
    paper_mgr.delete_paper(papers[0].id)
    assert len(paper_mgr.get_project_papers(p.id)) == 0
    pm.delete_project(p.id)
    paper_mgr.close()
    print("    Add/Tag/Read/Screen/Delete all persist")
except Exception as e:
    pts = 0
    print(f"    FAIL: {e}")
score("Paper Operations", pts, 15)

# ==================== 5. CHAT PERSISTENCE ====================
print('\n5. CHAT PERSISTENCE (10pts)')
pts = 10
try:
    cm = ChatManager()
    pm = ProjectManager()
    p = pm.create_project('_C_TEST_')
    chat = cm.create_chat(p.id, 'Test')
    cm.add_message(chat.id, 'user', 'Question 1')
    cm.add_message(chat.id, 'assistant', 'Answer 1')
    cm.add_message(chat.id, 'user', 'Question 2')
    msgs = cm.get_messages(chat.id)
    assert len(msgs) == 3
    cm.rename_chat(chat.id, 'Renamed')
    assert cm.get_chat(chat.id).title == 'Renamed'
    cm.delete_chat(chat.id)
    assert cm.get_chat(chat.id) is None
    pm.delete_project(p.id)
    cm.close()
    print("    Chat messages persist, rename/delete work")
except Exception as e:
    pts = 0
    print(f"    FAIL: {e}")
score("Chat Persistence", pts, 10)

# ==================== 6. OLLAMA AI ====================
print('\n6. OLLAMA AI (10pts)')
pts = 10
try:
    m = get_model_provider('ollama')
    resp = m.generate('Reply with just OK', max_tokens=10)
    if 'ok' in resp.lower() or 'ok' in resp:
        print("    AI responding correctly")
    elif 'Error' in resp:
        print(f"    AI error: {resp[:50]}")
        pts = 0
    else:
        print(f"    Unclear response: {resp[:50]}")
        pts = 5
except Exception as e:
    pts = 0
    print(f"    FAIL: {e}")
score("Ollama AI", pts, 10)

# ==================== 7. DOWNLOADER ====================
print('\n7. DOWNLOADER (10pts)')
pts = 10
try:
    from pathlib import Path
    tmp = tempfile.mkdtemp()
    dl = PaperDownloader(Path(tmp))
    class FakePaper:
        title = 'Attention Is All You Need'
        pdf_url = 'https://arxiv.org/pdf/1706.03762.pdf'
        year = '2017'
        doi = ''
        url = ''
    s, m, path = dl.download(FakePaper())
    if s and os.path.exists(path):
        size = os.path.getsize(path)
        print(f"    Downloaded {size//1024}KB successfully")
    else:
        print(f"    Download failed: {m}")
        pts = 3
    shutil.rmtree(tmp)
except Exception as e:
    pts = 0
    print(f"    FAIL: {e}")
score("Downloader", pts, 10)

# ==================== SUMMARY ====================
print('\n' + '='*60)
total = sum(r['points'] for r in RESULTS)
max_total = sum(r['max'] for r in RESULTS)
overall = (total / max_total) * 100 if max_total else 0

print(f'\nOVERALL SCORE: {overall:.0f}%')
print(f'CRITICAL FAILURES: {len(CRITICAL_FAILURES)}')

if CRITICAL_FAILURES:
    print('\nComponents needing attention:')
    for c in CRITICAL_FAILURES:
        print(f'  - {c}')

print('\nDETAILED SCORES:')
for r in RESULTS:
    bar = '#' * int(r['pct'] // 10)
    print(f"  {r['component']:20s} {r['pct']:3.0f}% {bar}")

print('='*60)