#!/usr/bin/env python3
"""
PaperMate v1.0 — AI Research Assistant
Smart, working, practical.
"""
import sys, os, textwrap, subprocess, webbrowser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.projects import ProjectManager
from app.chats import ChatManager
from app.search.engine import SearchEngine
from app.models import get_model_provider
from app.papers import PaperManager
from app.papers.downloader import PaperDownloader
from app.export import ResearchExporter
from app.reports import ReportGenerator

# Globals
project_mgr = ProjectManager()
chat_mgr = ChatManager()
search_engine = SearchEngine()
model = get_model_provider("ollama")

# ==================== DASHBOARD ====================
def dashboard():
    while True:
        projects = project_mgr.get_recent_projects(limit=10)
        
        print(f"""
╔══════════════════════════════════════════════╗
║     PAPERMATE — AI Research Assistant         ║
╚══════════════════════════════════════════════╝

  PROJECTS ({len(project_mgr.get_all_projects())} total)
""")
        if projects:
            for i, p in enumerate(projects, 1):
                stats = project_mgr.get_project_stats(p.id)
                sn = f"#{p.serial_number}" if p.serial_number else ""
                print(f"  [{i}] {sn} {p.name}")
                print(f"      {stats.get('paper_count',0)} papers | {stats.get('chat_count',0)} chats")
        else:
            print("  No projects yet. Create one!")
        
        print("\n  [N] New Project  [D] Delete Project  [Q] Quit")
        choice = input("> ").strip().lower()
        
        if choice == 'q': break
        elif choice == 'n': create_project_flow()
        elif choice == 'd': delete_project_flow()
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(projects):
                open_project_flow(projects[idx].id)

def create_project_flow():
    name = input("Project name: ").strip()
    if name:
        desc = input("Description (optional): ").strip()
        rq = input("Research question (optional): ").strip()
        p = project_mgr.create_project(name, desc, rq)
        print(f"[OK] Created: {p.name}")
        open_project_flow(p.id)

def delete_project_flow():
    projects = project_mgr.get_all_projects()
    for i, p in enumerate(projects, 1):
        print(f"  [{i}] {p.name}")
    num = input("Delete which project number? ").strip()
    if num.isdigit():
        idx = int(num) - 1
        if 0 <= idx < len(projects):
            p = projects[idx]
            confirm = input(f"Type DELETE to confirm deleting '{p.name}': ").strip()
            if confirm == "DELETE":
                project_mgr.delete_project(p.id)
                print("[OK] Deleted.")

# ==================== PROJECT VIEW ====================
def open_project_flow(project_id: str):
    project = project_mgr.open_project(project_id)
    if not project: return
    
    paper_mgr = PaperManager()
    
    while True:
        stats = project_mgr.get_project_stats(project_id)
        papers = paper_mgr.get_project_papers(project_id)
        
        print(f"""
╔══════════════════════════════════════════════╗
║  {project.name[:45]}
╚══════════════════════════════════════════════╝

  Papers: {stats.get('paper_count',0)} ({stats.get('downloaded_count',0)} downloaded) | Chats: {stats.get('chat_count',0)}

  [1] Search & Add Papers
  [2] My Papers ({len(papers)})
  [3] Chat with Project (AI + Internet)
  [4] Deep Research (AI Synthesis)
  [5] Export & Reports
  [6] Zotero Sync
  [7] Systematic Review
  [S] Saved Searches
  [W] Watch Folder (auto-import PDFs)
  [B] Back to Projects
""")
        
        choice = input("> ").strip().lower()
        
        if choice == 'b':
            project_mgr.close_project()
            break
        elif choice == '1': search_flow(project_id, paper_mgr)
        elif choice == '2': papers_flow(project_id, paper_mgr)
        elif choice == '3': project_chat_flow(project_id, paper_mgr)
        elif choice == '4': deep_research_flow(project_id, paper_mgr)
        elif choice == '5': export_flow(project_id, paper_mgr)
        elif choice == '6': zotero_flow(project_id, paper_mgr)
        elif choice == '7': review_flow(project_id, paper_mgr)
        elif choice == 's': quick_search_flow(project_id, paper_mgr)
        elif choice == 'w': watch_folder_flow(project_id, paper_mgr)
    
    paper_mgr.close()

# ==================== 1. SEARCH ====================
def search_flow(project_id, paper_mgr):
    query = input("\nSearch: ").strip()
    if not query: return
    
    print(f"\nSearching: {query}\n")
    papers = search_engine.search_all(query)
    
    if not papers:
        print("No results found.")
        return
    
    print(f"Found {len(papers)} papers:\n")
    for i, p in enumerate(papers[:15], 1):
        print(f"  [{i}] {p.title[:80]}")
        print(f"      {p.authors[:55]} | {p.source} | {p.year}")
        print()
    
    print("Actions: [num] View  [d num] Add+Download  [da] Add All  [q] Back")
    action = input("> ").strip().lower()
    
    if action == 'q': return
    elif action == 'da':
        added = 0
        for p in papers[:15]:
            if paper_mgr.add_paper(project_id, paper_to_dict(p)): added += 1
        print(f"[OK] Added {added} papers.")
        if input("Download PDFs now? (y/n): ").strip().lower() == 'y':
            download_all(project_id, paper_mgr)
    elif action.startswith('d '):
        try:
            idx = int(action[2:]) - 1
            if 0 <= idx < len(papers):
                p = papers[idx]
                paper = paper_mgr.add_paper(project_id, paper_to_dict(p))
                if paper and p.pdf_url:
                    dl = PaperDownloader(project_mgr.get_project_dir(project_id) / "downloads")
                    success, msg, path = dl.download(paper)
                    print(f"Download: {msg}")
                    if success:
                        paper_mgr.update_paper(paper.id, full_text_available=True, pdf_path=path)
        except: pass
    elif action.isdigit():
        idx = int(action) - 1
        if 0 <= idx < len(papers):
            p = papers[idx]
            print(f"\n{'='*60}\n{p.title}\n{'='*60}")
            print(f"Authors: {p.authors}\nYear: {p.year}\nSource: {p.source}")
            print(f"DOI: {p.doi}\nAbstract: {textwrap.fill(p.abstract or 'N/A', 60)}")
            if p.doi: webbrowser.open(f"https://doi.org/{p.doi}")

def paper_to_dict(p):
    return {"title": p.title, "authors": p.authors, "abstract": p.abstract,
            "journal": p.journal, "year": p.year, "doi": p.doi,
            "pmid": p.pmid, "url": p.url, "pdf_url": p.pdf_url, "source": p.source}

# ==================== SAVED SEARCHES ====================
def quick_search_flow(project_id, paper_mgr):
    templates = {
        "1": {"name": "Liposomal drug delivery", "query": "liposomal nanoparticle drug delivery cancer"},
        "2": {"name": "Antimicrobial plant extracts", "query": "plant extract antimicrobial antibacterial activity"},
        "3": {"name": "Nanoparticle formulation", "query": "nanoparticle formulation drug delivery bioavailability"},
        "4": {"name": "Cancer targeted therapy", "query": "targeted cancer therapy nano formulation"},
        "5": {"name": "Natural product pharmacology", "query": "natural product pharmacological activity mechanism"},
        "c": {"name": "Custom search", "query": None},
    }
    
    print("\nSAVED SEARCHES:\n")
    for key, t in templates.items():
        print(f"  [{key}] {t['name']}")
    
    choice = input("\nChoose or type custom query: ").strip()
    
    if choice in templates and choice != 'c':
        query = templates[choice]["query"]
    elif choice == 'c':
        query = input("Custom query: ").strip()
    else:
        query = choice
    
    if not query: return
    
    print(f"\nSearching: {query}\n")
    papers = search_engine.search_all(query)
    
    if not papers:
        print("No results found.")
        return
    
    print(f"Found {len(papers)} papers:\n")
    for i, p in enumerate(papers[:10], 1):
        print(f"  [{i}] {p.title[:75]}")
        print(f"      {p.authors[:50]} | {p.source} | {p.year}")
        print()
    
    print("Actions: [da] Add All  [q] Back")
    action = input("> ").strip().lower()
    
    if action == 'da':
        added = 0
        for p in papers[:10]:
            if paper_mgr.add_paper(project_id, paper_to_dict(p)):
                added += 1
        print(f"[OK] Added {added} papers.")
        if input("Download PDFs? (y/n): ").strip().lower() == 'y':
            download_all(project_id, paper_mgr)

# ==================== WATCH FOLDER ====================
def watch_folder_flow(project_id, paper_mgr):
    from app.papers.watcher import FolderWatcher
    
    watch_dir = project_mgr.get_project_dir(project_id) / "watch_folder"
    watcher = FolderWatcher(project_id, watch_dir)
    
    print(f"""
╔══════════════════════════════════════════════╗
║  WATCH FOLDER                                ║
╚══════════════════════════════════════════════╝

  Drop PDFs into:
  {watch_dir}

  [S] Scan now  [O] Open folder  [B] Back
""")
    
    while True:
        c = input("> ").strip().lower()
        if c == 'b': break
        elif c == 's':
            print("\nScanning for new PDFs...\n")
            added = watcher.scan()
            print(f"\n[OK] Imported {len(added)} new papers.")
        elif c == 'o':
            os.startfile(str(watch_dir))
    
    watcher.close()

# ==================== 2. MY PAPERS ====================
def papers_flow(project_id, paper_mgr):
    while True:
        papers = paper_mgr.get_project_papers(project_id)
        stats = paper_mgr.get_paper_stats(project_id)
        
        print(f"""
╔══════════════════════════════════════════════╗
║  MY PAPERS ({len(papers)})                    ║
╚══════════════════════════════════════════════╝
  Downloaded: {stats['downloaded']} | Unread: {stats['by_status']['unread']}
""")
        for i, p in enumerate(papers[:15], 1):
            icon = "📥" if p.full_text_available else "📄"
            read = "✓" if p.read_status == "read" else "○"
            print(f"  [{i}] {icon} {read} {p.title[:65]}")
            print(f"      {p.authors[:45]} | {p.year} | {p.source}")
        
        print("\n  [V] View  [O] Open PDF  [T] Tag  [S] Screen  [DL] Download All  [B] Back")
        choice = input("> ").strip().lower()
        
        if choice == 'b': break
        elif choice == 'dl': download_all(project_id, paper_mgr)
        elif choice == 'v':
            num = input("Paper number: ").strip()
            if num.isdigit():
                idx = int(num) - 1
                if 0 <= idx < len(papers):
                    view_paper(papers[idx], project_id, paper_mgr)
        elif choice == 'o':
            num = input("Paper number: ").strip()
            if num.isdigit():
                idx = int(num) - 1
                if 0 <= idx < len(papers):
                    open_pdf(papers[idx], project_id)
        elif choice == 't':
            num = input("Paper number: ").strip()
            if num.isdigit():
                idx = int(num) - 1
                if 0 <= idx < len(papers):
                    tag = input("Tag: ").strip()
                    if tag: paper_mgr.add_tag(papers[idx].id, tag)
        elif choice == 's':
            num = input("Paper number: ").strip()
            if num.isdigit():
                idx = int(num) - 1
                if 0 <= idx < len(papers):
                    d = input("[I]nclude [E]xclude [M]aybe: ").strip().lower()
                    dm = {"i":"included","e":"excluded","m":"maybe"}
                    if d in dm:
                        paper_mgr.update_screening(papers[idx].id, dm[d])

def view_paper(paper, project_id, paper_mgr):
    while True:
        print(f"""
{'='*60}
{paper.title[:80]}
{'='*60}
Authors: {paper.authors}
Year: {paper.year} | Source: {paper.source}
DOI: {paper.doi} | PMID: {paper.pmid}
Status: {paper.read_status} | Screening: {paper.screening_status}
PDF: {'Downloaded' if paper.full_text_available else 'Not available'}
Abstract: {textwrap.fill((paper.abstract or 'N/A')[:400], 55)}
""")
        print("[O]pen PDF  [F]older  [Z]otero  [C]opy Citation  [M]ark Read  [T]ag  [E]vidence  [B]ack")
        c = input("> ").strip().lower()
        
        if c == 'b': break
        elif c == 'o': open_pdf(paper, project_id)
        elif c == 'f':
            downloads = project_mgr.get_project_dir(project_id) / "downloads"
            os.startfile(str(downloads))
            print("Downloads folder opened. Drag PDF into Zotero.")
        elif c == 'z':
            opened = False
            if paper.doi:
                try:
                    webbrowser.open(f"zotero://select/items/0_DOI:{paper.doi}")
                    opened = True
                    print("Opening in Zotero app...")
                except: pass
            if not opened:
                open_pdf(paper, project_id)
                print("PDF opened - drag into Zotero to add.")
            cite = f"{paper.authors} ({paper.year}). {paper.title}."
            if paper.journal: cite += f" {paper.journal}."
            if paper.doi: cite += f" DOI: {paper.doi}"
            cf = project_mgr.get_project_dir(project_id) / "citations.txt"
            with open(cf, "a", encoding="utf-8") as f: f.write(cite + "\n\n")
            print("Citation saved to citations.txt")
        elif c == 'c':
            cite = f"{paper.authors} ({paper.year}). {paper.title}."
            if paper.journal: cite += f" {paper.journal}."
            if paper.doi: cite += f" DOI: {paper.doi}"
            cf = project_mgr.get_project_dir(project_id) / "citations.txt"
            with open(cf, "a", encoding="utf-8") as f: f.write(cite + "\n\n")
            print(f"Saved:\n{cite}")
        elif c == 'm':
            s = input("Status (unread/reading/read): ").strip()
            paper_mgr.mark_read_status(paper.id, s)
            paper = paper_mgr.get_paper(paper.id)
        elif c == 't':
            tag = input("Tag: ").strip()
            if tag: paper_mgr.add_tag(paper.id, tag)
        elif c == 'e':
            extract_evidence(paper, project_id)
        input("\nPress Enter...")

def open_pdf(paper, project_id):
    paths = []
    if paper.pdf_path and os.path.exists(paper.pdf_path):
        paths.append(paper.pdf_path)
    dl_dir = project_mgr.get_project_dir(project_id) / "downloads"
    if dl_dir.exists():
        for f in dl_dir.glob("*.pdf"):
            if paper.title[:30].lower() in f.name.lower():
                paths.append(str(f))
    if paths:
        os.startfile(paths[0])
        print("PDF opened.")
    else:
        print("PDF not found. Download first.")

def download_all(project_id, paper_mgr):
    papers = paper_mgr.get_project_papers(project_id)
    to_dl = [p for p in papers if not p.full_text_available and p.pdf_url]
    if not to_dl:
        print("All downloaded.")
        return
    print(f"\nDownloading {len(to_dl)} papers...\n")
    dl = PaperDownloader(project_mgr.get_project_dir(project_id) / "downloads")
    for i, p in enumerate(to_dl, 1):
        print(f"  [{i}/{len(to_dl)}] {p.title[:50]}...")
        success, msg, path = dl.download(p)
        print(f"    -> {msg}")
        if success:
            paper_mgr.update_paper(p.id, full_text_available=True, pdf_path=path)
            paper_mgr.session.commit()
    print("[OK] Done!")

# ==================== 3. PROJECT CHAT (PERSISTENT) ====================
def project_chat_flow(project_id, paper_mgr):
    papers = paper_mgr.get_project_papers(project_id)
    
    # Get or create persistent chat
    chats = chat_mgr.get_project_chats(project_id)
    if chats:
        chat = chats[0]
        messages = chat_mgr.get_messages(chat.id)
    else:
        chat = chat_mgr.create_chat(project_id, "Research Chat")
        messages = []
    
    print(f"""
╔══════════════════════════════════════════════╗
║  CHAT WITH PROJECT                           ║
║  {len(papers)} papers | {len(messages)} messages in history    ║
╚══════════════════════════════════════════════╝

Type /search to force internet search. Type /back to exit.
""")
    
    # Show recent messages if any
    if messages:
        print("Recent conversation:")
        for msg in messages[-4:]:
            role = "You" if msg.role == "user" else "AI"
            print(f"  {role}: {msg.content[:100]}...")
        print()
    
    # Build paper context
    paper_context = ""
    if papers:
        paper_context = "\n\n".join([
            f"[PAPER {i+1}] {p.title}\nAuthors: {p.authors} ({p.year})\n"
            f"Abstract: {(p.abstract or 'N/A')[:300]}"
            for i, p in enumerate(papers[:15])
        ])
    
    while True:
        question = input("\nYou: ").strip()
        
        if question.lower() == '/back': break
        if not question: continue
        
        need_search = question.lower().startswith('/search')
        if need_search:
            question = question[8:].strip()
        
        # Save user message
        chat_mgr.add_message(chat.id, "user", question)
        
        # Build prompt with context
        if paper_context and not need_search:
            prompt = f"""You are a medical research assistant. Answer using the user's papers if possible.

USER'S PAPERS:
{paper_context}

QUESTION: {question}

INSTRUCTIONS:
1. First, check if the papers contain relevant information
2. If YES: Answer using the papers, cite as [PAPER 1], [PAPER 2], etc.
3. If the papers are NOT relevant or don't answer the question, say: "NEED_SEARCH: [specific search query]"
4. Be honest - don't force an answer from irrelevant papers

RESPONSE:"""
        else:
            prompt = f"""Answer this medical research question. If you need more specific papers, suggest what to search for.

QUESTION: {question}

RESPONSE:"""
        
        print("AI: ", end="", flush=True)
        response = model.generate(prompt, max_tokens=500)
        print(response)
        
        # Handle internet search fallback
        if "NEED_SEARCH:" in response:
            search_query = response.split("NEED_SEARCH:")[1].strip().split("\n")[0]
            print(f"\nSearching internet for: {search_query}\n")
            
            results = search_engine.search_all(search_query, max_per_source=5)
            
            if results:
                print(f"Found {len(results)} papers:\n")
                for i, r in enumerate(results[:8], 1):
                    print(f"  [{i}] {r.title[:80]}")
                    print(f"      {r.authors[:50]} | {r.year}")
                
                search_context = "\n\n".join([
                    f"[SEARCH {i+1}] {r.title}\n{r.abstract[:300] if r.abstract else ''}"
                    for i, r in enumerate(results[:8])
                ])
                
                prompt2 = f"""Answer the question using these search results.

SEARCH RESULTS:
{search_context}

QUESTION: {question}

Answer with citations as [SEARCH 1], [SEARCH 2], etc.

RESPONSE:"""
                
                print("\nAI (from search): ", end="", flush=True)
                response2 = model.generate(prompt2, max_tokens=500)
                print(response2)
                response = response2  # Save the search result
                
                if input("\nAdd these papers to your project? (y/n): ").strip().lower() == 'y':
                    for r in results[:8]:
                        paper_mgr.add_paper(project_id, paper_to_dict(r))
                    print("[OK] Papers added!")
                    if input("Download PDFs now? (y/n): ").strip().lower() == 'y':
                        download_all(project_id, paper_mgr)
                    papers = paper_mgr.get_project_papers(project_id)
                    paper_context = "\n\n".join([
                        f"[PAPER {i+1}] {p.title}\nAuthors: {p.authors} ({p.year})\n"
                        f"Abstract: {(p.abstract or 'N/A')[:300]}"
                        for i, p in enumerate(papers[:15])
                    ])
            else:
                print("No results found. Try different keywords.")
                response = "No results found for this search."
        
        # Save AI response
        chat_mgr.add_message(chat.id, "assistant", response)

# ==================== 4. DEEP RESEARCH ====================
def deep_research_flow(project_id, paper_mgr):
    question = input("\nResearch question: ").strip()
    if not question: return
    
    print(f"\nSearching & analyzing...\n")
    papers = search_engine.search_all(question, max_per_source=5)
    
    if not papers:
        print("No papers found.")
        return
    
    # Show papers found
    print(f"Found {len(papers)} papers. Top results:\n")
    for i, p in enumerate(papers[:5], 1):
        print(f"  [{i}] {p.title[:80]}")
        print(f"      {p.authors[:50]} | {p.year} | {p.source}")
    
    ctx = "\n\n".join([f"[{i+1}] {p.title}\n{p.abstract[:300] if p.abstract else ''}" 
                       for i, p in enumerate(papers[:8])])
    
    prompt = f"""You are a medical researcher. Answer using these papers:

{ctx}

Question: {question}

Provide: Key Findings, Limitations, Research Gaps. Cite as [1],[2].

ANALYSIS:"""
    print("\nAI Analysis:\n" + "="*60)
    print(model.generate(prompt, max_tokens=600))
    print("="*60)
    
    if input("\nAdd these papers to project? (y/n): ").strip().lower() == 'y':
        for p in papers[:8]:
            paper_mgr.add_paper(project_id, paper_to_dict(p))
        print("[OK] Added!")

# ==================== 5. EXPORT ====================
def export_flow(project_id, paper_mgr):
    proj_dir = project_mgr.get_project_dir(project_id)
    exporter = ResearchExporter(project_id, proj_dir / "exports")
    
    while True:
        print("""
  [1] BibTeX    [2] CSV    [3] RIS    [4] Evidence CSV    [5] Report    [B] Back
""")
        c = input("> ").strip().lower()
        if c == 'b': break
        elif c == '1': print(f"[OK] {exporter.export_papers_bibtex()}")
        elif c == '2': print(f"[OK] {exporter.export_papers_csv()}")
        elif c == '3': print(f"[OK] {exporter.export_papers_ris()}")
        elif c == '4': print(f"[OK] {exporter.export_evidence_csv()}")
        elif c == '5':
            gen = ReportGenerator(project_id, proj_dir)
            report = gen.generate_full_report()
            print(report[:2000])
            if input("Save? (y/n): ").strip().lower() == 'y':
                print(f"[OK] {gen.save_report(report)}")
            gen.close()
        input("Press Enter...")
    exporter.close()

# ==================== 6. ZOTERO ====================
def zotero_flow(project_id, paper_mgr):
    from app.integrations.zotero import ZoteroClient
    from app.integrations.zotero.sync import ZoteroSync
    
    zotero = ZoteroClient()
    
    while True:
        print(f"""
  Zotero: {'Connected' if zotero.connected else 'Not configured'}
  [1] Configure  [2] Sync Library  [3] Import Collection  [B] Back
""")
        c = input("> ").strip().lower()
        if c == 'b': break
        elif c == '1':
            zotero.configure(input("API Key: ").strip(), input("User ID: ").strip())
            print("[OK] Connected!" if zotero.connected else "[FAIL] Check credentials.")
        elif c == '2':
            if zotero.connected:
                syncer = ZoteroSync(zotero, project_id)
                r = syncer.sync_all()
                print(f"[OK] Added: {r.get('added',0)}, Updated: {r.get('updated',0)}")
                syncer.close()
        elif c == '3':
            if zotero.connected:
                cols = zotero.get_collections()
                for i, col in enumerate(cols, 1):
                    print(f"  [{i}] {col.get('data',{}).get('name','?')}")
                num = input("Collection number: ").strip()
                if num.isdigit():
                    idx = int(num)-1
                    if 0 <= idx < len(cols):
                        syncer = ZoteroSync(zotero, project_id)
                        r = syncer.sync_collection(cols[idx].get("key"))
                        print(f"[OK] Added {r.get('added',0)} papers")
                        syncer.close()
        input("Press Enter...")

# ==================== 7. SYSTEMATIC REVIEW ====================
def review_flow(project_id, paper_mgr):
    from app.review import SystematicReviewWorkflow
    workflow = SystematicReviewWorkflow(project_id)
    
    while True:
        status = workflow.get_status()
        print(f"""
╔══════════════════════════════════════════════╗
║  SYSTEMATIC REVIEW                           ║
╚══════════════════════════════════════════════╝

  Progress: {status['completion_pct']}% screened
  Total: {status['total_identified']} | Screened: {status['screened']} | Remaining: {status['remaining']}
  Included: {status['included']} | Excluded: {status['excluded']} | Maybe: {status['maybe']}

  [1] Screen Next Paper
  [2] View Included ({status['included']})
  [3] Evidence Synthesis (needs included papers)
  [B] Back
""")
        c = input("> ").strip().lower()
        if c == 'b': break
        elif c == '1':
            p = workflow.get_next_unscreened()
            if p:
                print(f"\n{'='*60}")
                print(f"TITLE: {p['title'][:80]}")
                print(f"{'='*60}")
                print(f"Authors: {p['authors']}")
                print(f"Year: {p['year']} | Source: {p['source']}")
                print(f"\nAbstract: {textwrap.fill(p['abstract'][:400] if p['abstract'] else 'N/A', 55)}")
                print(f"\nDecision: [I]nclude  [E]xclude  [M]aybe  [S]kip")
                d = input("> ").strip().lower()
                dm = {"i":"included","e":"excluded","m":"maybe"}
                if d in dm:
                    reason = input("Reason: ").strip()
                    workflow.screen_paper(p["id"], dm[d], reason)
                    print(f"[OK] Marked as {dm[d]}")
            else:
                print("\nNo more papers to screen!")
        elif c == '2':
            included = workflow.get_included_papers()
            if included:
                print(f"\nIncluded papers ({len(included)}):\n")
                for i, p in enumerate(included, 1):
                    print(f"  [{i}] {p['title'][:70]}")
                    print(f"      {p['authors'][:50]} ({p['year']})")
            else:
                print("\nNo papers included yet. Screen some papers first with [1].")
        elif c == '3':
            from app.synthesis import SynthesisAnalyzer
            included = workflow.get_included_papers()
            if not included:
                print("\nNo papers included yet!")
                print("Use [1] to screen papers. Mark relevant ones as Included.")
                print("Then come back here for AI synthesis.")
            else:
                s = SynthesisAnalyzer()
                ids = [p["id"] for p in included]
                print(f"\nSynthesizing {len(ids)} included papers...\n")
                result = s.synthesize(ids)
                print("="*60)
                print("EVIDENCE SYNTHESIS")
                print("="*60)
                if result.get('evidence_summary'):
                    print(f"\nSummary: {result['evidence_summary'][:500]}")
                if result.get('evidence_strength'):
                    print(f"\nStrength: {result['evidence_strength'][:200]}")
                if result.get('key_findings'):
                    print("\nKey Findings:")
                    for f in result['key_findings'][:5]:
                        print(f"  - {f}")
                if result.get('limitations'):
                    print(f"\nLimitations: {result['limitations'][:200]}")
                s.close()
        input("\nPress Enter...")
    workflow.close()

# ==================== EVIDENCE ====================
def extract_evidence(paper, project_id):
    from app.evidence import EvidenceExtractor, EVIDENCE_TEMPLATES
    ext = EvidenceExtractor()
    
    print("\nTemplates:")
    keys = list(EVIDENCE_TEMPLATES.keys())
    for i, name in enumerate(keys, 1):
        print(f"  [{i}] {name.replace('_',' ').title()} ({len(EVIDENCE_TEMPLATES[name])} fields)")
    
    choice = input("Choose template number: ").strip()
    fields = EVIDENCE_TEMPLATES["general"]
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(keys):
            fields = EVIDENCE_TEMPLATES[keys[idx]]
    
    print(f"\nExtracting: {', '.join(fields[:8])}...\n")
    result = ext.extract_from_paper(paper.id, fields)
    for k, v in result.items():
        if v and v != "Not reported":
            print(f"  {k.replace('_',' ').title()}: {v}")
    ext.close()

# ==================== MAIN ====================
if __name__ == "__main__":
    print("\nStarting PaperMate...\n")
    try:
        model.generate("OK", max_tokens=5)
        print("AI Ready.\n")
    except:
        print("AI offline - some features limited.\n")
    dashboard()
