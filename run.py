#!/usr/bin/env python3
"""
PaperMate — Search, Read, Chat.
Smart downloads via Unpaywall + arXiv + PMC.
"""
import sys, os, textwrap, webbrowser, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    G = Fore.GREEN; R = Fore.RED; C = Fore.CYAN; X = Fore.RESET
except:
    G = R = C = X = ""

from app.projects import ProjectManager
from app.chats import ChatManager
from app.search.engine import SearchEngine
from app.models import get_model_provider
from app.papers import PaperManager
from app.papers.downloader import PaperDownloader

project_mgr = ProjectManager()
chat_mgr = ChatManager()
search_engine = SearchEngine()
model = get_model_provider("ollama")

def ask(prompt_text):
    try: return input(prompt_text).strip()
    except: return "q"

# ==================== DASHBOARD ====================
def dashboard():
    while True:
        projects = project_mgr.get_all_projects()
        print(f"""
{C}╔══════════════════════════════╗
║     PAPERMATE                 ║
╚══════════════════════════════╝{X}

  PROJECTS ({len(projects)})
""")
        if projects:
            for i, p in enumerate(projects, 1):
                s = project_mgr.get_project_stats(p.id)
                print(f"  [{i}] {p.name} ({s.get('paper_count',0)} papers)")
        else:
            print("  None. Create one!")
        print("\n  [N] New  [D] Delete  [Q] Quit")
        c = ask("> ").lower()
        if c == 'q': break
        elif c == 'n':
            n = ask("Name: ")
            if n: open_project(project_mgr.create_project(n).id)
        elif c == 'd':
            ps = project_mgr.get_all_projects()
            for i, p in enumerate(ps, 1): print(f"  [{i}] {p.name}")
            n = ask("Delete #: ")
            if n.isdigit() and 0 <= int(n)-1 < len(ps):
                if ask(f"Type '{ps[int(n)-1].name}': ") == ps[int(n)-1].name:
                    project_mgr.delete_project(ps[int(n)-1].id)
                    print(f"{G}[OK]{X}")
        elif c.isdigit():
            i = int(c)-1
            if 0 <= i < len(projects): open_project(projects[i].id)

# ==================== PROJECT ====================
def open_project(pid):
    p = project_mgr.open_project(pid)
    if not p: return
    pm = PaperManager()
    while True:
        s = project_mgr.get_project_stats(pid)
        print(f"""
{C}{p.name[:50]}{X}
  Papers: {s.get('paper_count',0)} ({s.get('downloaded_count',0)} downloaded)
  [1] Search & Add Papers
  [2] My Papers
  [3] Chat with AI
  [B] Back
""")
        c = ask("> ").lower()
        if c == 'b': break
        elif c == '1': search_flow(pid, pm)
        elif c == '2': papers_flow(pid, pm)
        elif c == '3': chat_flow(pid, pm)
    pm.close()
    project_mgr.close_project()

# ==================== SEARCH ====================
def search_flow(pid, pm):
    q = ask("\nSearch: ")
    if not q: return
    papers = search_engine.search_all(q)
    if not papers: print(f"{R}No results.{X}"); return
    print(f"\n{G}{len(papers)} results:{X}\n")
    for i, p in enumerate(papers[:15], 1):
        print(f"  [{i}] {p.title[:80]}")
        print(f"      {p.authors[:50]} | {p.source} | {p.year}\n")
    print("[da] Add All  [d 3] Add #3  [q] Back")
    a = ask("> ").lower()
    if a == 'q': return
    elif a == 'da':
        for p in papers[:15]: pm.add_paper(pid, paper_to_dict(p))
        print(f"{G}[OK]{X}")
        if ask("Download PDFs? (y/n): ").lower() == 'y': download_all(pid, pm)
    elif a.startswith('d '):
        try:
            i = int(a[2:])-1
            if 0 <= i < len(papers):
                pp = pm.add_paper(pid, paper_to_dict(papers[i]))
                if pp and papers[i].pdf_url:
                    dl = PaperDownloader(project_mgr.get_project_dir(pid)/"PDFs")
                    s, m, path = dl.download(pp)
                    if s: pm.update_paper(pp.id, full_text_available=True, pdf_path=path)
                    print(f"Download: {m}")
        except: pass

def paper_to_dict(p):
    return {"title": p.title, "authors": p.authors, "abstract": p.abstract,
            "journal": p.journal, "year": p.year, "doi": p.doi,
            "pmid": p.pmid, "url": p.url, "pdf_url": p.pdf_url, "source": p.source}

# ==================== PAPERS ====================
def papers_flow(pid, pm):
    while True:
        papers = pm.get_project_papers(pid)
        st = pm.get_paper_stats(pid)
        print(f"\n{C}MY PAPERS ({len(papers)})  Downloaded: {st['downloaded']}{X}\n")
        for i, p in enumerate(papers[:15], 1):
            icon = "📥" if p.full_text_available else "📄"
            print(f"  [{i}] {icon} {p.title[:65]}")
            print(f"      {p.authors[:45]} | {p.year} | {p.source}")
        print("\n  [O] Open PDF  [B] Open in Browser  [C] Citation  [DL] Download All  [Q] Back")
        c = ask("> ").lower()
        if c == 'q': break
        elif c == 'dl': download_all(pid, pm)
        elif c == 'o':
            n = ask("#: ")
            if n.isdigit() and 0 <= int(n)-1 < len(papers): open_pdf(papers[int(n)-1], pid)
        elif c == 'b':
            n = ask("#: ")
            if n.isdigit() and 0 <= int(n)-1 < len(papers):
                p = papers[int(n)-1]
                url = f"https://doi.org/{p.doi}" if p.doi else p.url
                if url:
                    webbrowser.open(url)
                    print(f"{G}Opened in browser.{X}")
                else:
                    print(f"{R}No URL available.{X}")
        elif c == 'c':
            n = ask("#: ")
            if n.isdigit() and 0 <= int(n)-1 < len(papers):
                p = papers[int(n)-1]
                cite = f"{p.authors} ({p.year}). {p.title}."
                if p.journal: cite += f" {p.journal}."
                if p.doi: cite += f" DOI: {p.doi}"
                print(f"\n{G}Citation:{X}\n{cite}\n")
                cf = project_mgr.get_project_dir(pid)/"citations.txt"
                with open(cf, "a", encoding="utf-8") as f: f.write(cite+"\n\n")
                print(f"{G}Saved to citations.txt{X}")

def open_pdf(paper, pid):
    paths = []
    if paper.pdf_path and os.path.exists(paper.pdf_path):
        paths.append(paper.pdf_path)
    dl = project_mgr.get_project_dir(pid)/"PDFs"
    if dl.exists():
        for f in dl.rglob("*.pdf"):
            if paper.title[:30].lower() in f.name.lower():
                paths.append(str(f))
    if paths:
        os.startfile(paths[0])
        print(f"{G}PDF opened.{X}")
    else:
        print(f"{R}Not found. Use [B] to open in browser.{X}")

def download_all(pid, pm):
    from config.settings import ZOTERO_API_KEY, ZOTERO_USER_ID
    from app.integrations.zotero import ZoteroClient
    from app.integrations.zotero.sync import ZoteroSync
    
    papers = pm.get_project_papers(pid)
    td = [p for p in papers if not p.full_text_available and p.pdf_url]
    if not td: print("All downloaded."); return
    
    # Initialize Zotero if configured
    zotero = ZoteroClient()
    if ZOTERO_API_KEY and ZOTERO_USER_ID:
        zotero.configure(ZOTERO_API_KEY, ZOTERO_USER_ID)
    syncer = ZoteroSync(zotero, pid) if zotero.connected else None
    
    print(f"\nDownloading {len(td)}...\n")
    dl = PaperDownloader(project_mgr.get_project_dir(pid)/"PDFs")
    for i, p in enumerate(td, 1):
        print(f"  [{i}/{len(td)}] {p.title[:50]}...")
        s, m, path = dl.download(p)
        print(f"    -> {m}")
        if s:
            pm.update_paper(p.id, full_text_available=True, pdf_path=path)
            pm.session.commit()
            # Auto-save to Zotero
            if syncer:
                try:
                    syncer._sync_item_from_paper(p)
                    print(f"    -> Saved to Zotero")
                except:
                    print(f"    -> Zotero save failed (will retry later)")
    
    if syncer: syncer.close()
    print(f"[OK] Done!")
# ==================== CHAT ====================
def chat_flow(pid, pm):
    chats = chat_mgr.get_project_chats(pid)
    chat = chats[0] if chats else chat_mgr.create_chat(pid, "Chat")
    papers = pm.get_project_papers(pid)
    msgs = chat_mgr.get_messages(chat.id)
    
    print(f"\n{C}CHAT | {len(papers)} papers | {len(msgs)} messages{X}")
    print("Ask anything. AI uses your papers + knowledge. /back to exit.\n")
    
    if msgs:
        for m in msgs[-3:]:
            r = "You" if m.role == "user" else "AI"
            print(f"  [{r}] {m.content[:100]}...")
        print()
    
    ctx = "\n\n".join([f"[PAPER {i+1}] {p.title}\nAbstract: {(p.abstract or 'N/A')[:200]}" for i, p in enumerate(papers[:10])]) if papers else ""
    
    while True:
        q = ask("You: ")
        if q.lower() in ['/back', 'exit', 'quit']: break
        if not q: continue
        
        chat_mgr.add_message(chat.id, "user", q)
        all_msgs = chat_mgr.get_messages(chat.id)
        history = "\n".join([f"{'User' if m.role=='user' else 'AI'}: {m.content[:300]}" for m in all_msgs[-6:]])
        
        prompt = f"""Conversation:
{history}

Papers:
{ctx if ctx else 'No papers in project.'}

Question: {q}

If papers are relevant, cite as [PAPER 1], [PAPER 2]. If not, answer from knowledge. Never make up citations.
ANSWER:"""
        
        print(f"{C}AI: {X}", end="", flush=True)
        resp = model.generate(prompt, max_tokens=500)
        print(resp)
        chat_mgr.add_message(chat.id, "assistant", resp)

# ==================== MAIN ====================
if __name__ == "__main__":
    print(f"\n{C}PaperMate — Search, Read, Chat{X}\n")
    try:
        model.generate("OK", max_tokens=5)
        print(f"{G}AI Ready.{X}\n")
    except:
        print(f"{R}AI offline.{X}\n")
    dashboard()
