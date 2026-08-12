#!/usr/bin/env python3
"""PaperMate — Strict Audit (v3 — includes Zotero)"""
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
print('PAPERMATE STRICT AUDIT v3')
print('='*60)

# 1. IMPORTS
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
    from app.integrations.zotero import ZoteroClient
    from app.integrations.zotero.sync import ZoteroSync
    from config.settings import ZOTERO_API_KEY, ZOTERO_USER_ID
    print("    All modules importable")
except Exception as e:
    pts = 0
    print(f"    FAIL: {e}")
score("Imports", pts, 20)

# 2. SEARCH SOURCES
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
score("Search Sources", working * 5, 20, f"{working}/4 sources working")

# 3. PROJECT CRUD
print('\n3. PROJECT CRUD (10pts)')
pts = 10
try:
    pm = ProjectManager()
    p = pm.create_project('_TEST_A_')
    assert p.name == '_TEST_A_'
    stats = pm.get_project_stats(p.id)
    assert 'paper_count' in stats
    pm.rename_project(p.id, '_TEST_B_')
    assert pm.repo.get(p.id).name == '_TEST_B_'
    pm.delete_project(p.id)
    assert pm.repo.get(p.id) is None
    print("    Create/Rename/Stats/Delete all pass")
except Exception as e:
    pts = 0
    print(f"    FAIL: {e}")
score("Project CRUD", pts, 10)

# 4. PAPER OPERATIONS
print('\n4. PAPER OPERATIONS (10pts)')
pts = 10
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
    paper_mgr.delete_paper(papers[0].id)
    assert len(paper_mgr.get_project_papers(p.id)) == 0
    pm.delete_project(p.id)
    paper_mgr.close()
    print("    Add/Tag/Read/Screen/Delete all persist")
except Exception as e:
    pts = 0
    print(f"    FAIL: {e}")
score("Paper Operations", pts, 10)

# 5. CHAT PERSISTENCE
print('\n5. CHAT PERSISTENCE (10pts)')
pts = 10
try:
    cm = ChatManager()
    pm = ProjectManager()
    p = pm.create_project('_C_TEST_')
    chat = cm.create_chat(p.id, 'Test')
    cm.add_message(chat.id, 'user', 'Q1')
    cm.add_message(chat.id, 'assistant', 'A1')
    cm.add_message(chat.id, 'user', 'Q2')
    assert len(cm.get_messages(chat.id)) == 3
    cm.rename_chat(chat.id, 'Renamed')
    assert cm.get_chat(chat.id).title == 'Renamed'
    cm.delete_chat(chat.id)
    assert cm.get_chat(chat.id) is None
    pm.delete_project(p.id)
    cm.close()
    print("    Chat persistence works")
except Exception as e:
    pts = 0
    print(f"    FAIL: {e}")
score("Chat Persistence", pts, 10)

# 6. OLLAMA
print('\n6. OLLAMA AI (10pts)')
pts = 10
try:
    m = get_model_provider('ollama')
    resp = m.generate('Reply with just OK', max_tokens=10)
    if 'ok' in resp.lower():
        print("    AI responding")
    else:
        print(f"    Unclear: {resp[:40]}")
        pts = 5
except Exception as e:
    pts = 0
    print(f"    FAIL: {e}")
score("Ollama AI", pts, 10)

# 7. DOWNLOADER
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
        print(f"    Downloaded {os.path.getsize(path)//1024}KB")
    else:
        print(f"    Download: {m}")
        pts = 3
    shutil.rmtree(tmp)
except Exception as e:
    pts = 0
    print(f"    FAIL: {e}")
score("Downloader", pts, 10)

# 8. UNPAYWALL
print('\n8. UNPAYWALL (5pts)')
pts = 5
try:
    result = find_open_access_pdf('10.1038/nature12373')
    print(f"    Unpaywall responsive ({'found PDF' if result else 'no OA version'})")
except Exception as e:
    pts = 0
    print(f"    FAIL: {e}")
score("Unpaywall", pts, 5)

# 9. ZOTERO CONFIG
print('\n9. ZOTERO CONFIG (5pts)')
pts = 5
if ZOTERO_API_KEY and ZOTERO_USER_ID:
    print(f"    API key present (user {ZOTERO_USER_ID})")
else:
    pts = 0
    print("    No Zotero credentials")
score("Zotero Config", pts, 5)

# 10. ZOTERO CONNECTION
print('\n10. ZOTERO CONNECTION (10pts)')
pts = 10
try:
    z = ZoteroClient()
    if ZOTERO_API_KEY and ZOTERO_USER_ID:
        z.configure(ZOTERO_API_KEY, ZOTERO_USER_ID)
    if z.connected:
        print("    Zotero connected")
    else:
        print(f"    Zotero not connected: {z.last_error}")
        pts = 3
except Exception as e:
    pts = 0
    print(f"    FAIL: {e}")
score("Zotero Connection", pts, 10)

# SUMMARY
print('\n' + '='*60)
total = sum(r['points'] for r in RESULTS)
max_total = sum(r['max'] for r in RESULTS)
overall = (total / max_total) * 100 if max_total else 0

print(f'\nOVERALL SCORE: {overall:.0f}%')
print(f'CRITICAL FAILURES: {len(CRITICAL_FAILURES)}')

if CRITICAL_FAILURES:
    print('\nNeeds attention:')
    for c in CRITICAL_FAILURES:
        print(f'  - {c}')

print('\nDETAILED:')
for r in RESULTS:
    bar = '#' * int(r['pct'] // 10)
    print(f"  {r['component']:20s} {r['pct']:3.0f}% {bar}")
print('='*60)
