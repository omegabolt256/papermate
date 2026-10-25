from __future__ import annotations
from pathlib import Path

import argparse
import os
import sys

try:
    from rich import box
    from rich.align import Align
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    console = Console()
except ImportError:
    console = None

import httpx

from backend.api.research import create_research_api
from backend.library.index import LibraryIndex
from backend.library.pdf_text import PDFTextIndex
from backend.library.zotero import ZoteroLocalClient, ZoteroConnectionError


GREEN = "\033[38;5;108m"
CREAM = "\033[38;5;230m"
MUTED = "\033[38;5;245m"
RESET = "\033[0m"





def _papermate_wordmark() -> list[str]:
    """Render PAPER over MATE using the DOS Rebel FIGlet font."""
    from pyfiglet import Figlet

    fig = Figlet(font="DOS Rebel")
    paper = fig.renderText("PAPER").rstrip().splitlines()
    mate = fig.renderText("MATE").rstrip().splitlines()
    return paper + [""] + mate



def show_intro() -> None:
    if console is None:
        print("\n" + "=" * 70)
        print("  WELCOME TO PAPERMATE  /  BOTANICAL RESEARCH WORKSPACE")
        print("=" * 70)
        print()
        for row in _papermate_wordmark():
            print(row)
        print()
        print("  Cultivate knowledge.")
        print("  Follow the evidence.")
        print()
        print("  [ FIELD NOTES & SOURCE CARE ]")
        print("  1. Verify key claims against their sources.")
        print("  2. Check citations and source context.")
        print("  3. Keep sensitive documents in services you trust.")
        print()
        print("  " + "-" * 18 + "  < leaf >  " + "-" * 18)
        print("  LOCAL-FIRST RESEARCH / ROOTED IN EVIDENCE")
        input("\n  Press Enter to continue...")
        return

    from rich.align import Align
    from rich.panel import Panel
    from rich.text import Text
    from rich import box

    console.clear()
    console.print()
    console.print(Panel(
        Text("WELCOME TO PAPERMATE  /  BOTANICAL RESEARCH WORKSPACE",
             style="bold white"),
        border_style="green",
        box=box.ROUNDED,
        padding=(0, 1),
    ))
    console.print()

    for row in _papermate_wordmark():
        console.print(Align.center(Text(row, style="bold bright_green")))

    console.print()
    console.print(Align.center(Text("Cultivate knowledge.", style="bold white")))
    console.print(Align.center(Text("Follow the evidence.", style="bold bright_green")))
    console.print()
    console.print()
    console.print()
    console.print(Text("  [ FIELD NOTES & SOURCE CARE ]", style="bold bright_green"))
    console.print(Text("  1. Verify key claims against their sources.", style="white"))
    console.print(Text("  2. Check citations and source context.", style="white"))
    console.print(Text("  3. Keep sensitive documents in services you trust.", style="white"))
    console.print()
    console.print()
    console.print(Align.center(Text("LOCAL-FIRST RESEARCH  /  ROOTED IN EVIDENCE", style="dim green")))
    console.print()
    console.print(Text("  Press Enter to continue...", style="bold bright_green"))
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        raise SystemExit(0)


def show_welcome() -> None:
    if console is None:
        print("\nPAPERMATE  /  BOTANICAL RESEARCH WORKSPACE")
        print("-" * 62)
        print("  01  Search literature       Find and open papers")
        print("  02  Investigate              Build evidence-backed answers")
        print("  03  Sync Zotero              Refresh your paper index")
        print("  04  Papers workspace         Open your working folder")
        print("  05  Exit                     Close PaperMate")
        print("-" * 62)
        print("  ROOTED IN YOUR LIBRARY  |  papermate status")
        return

    from rich.table import Table
    from rich.text import Text

    console.clear()
    console.print()
    console.print(
        Text("PAPERMATE", style="bold bright_green")
        + Text("   /   BOTANICAL RESEARCH WORKSPACE", style="dim")
    )
    console.print(Text("Cultivate knowledge. Follow the evidence.", style="green"))
    console.print(Text("-" * 62, style="green"))
    console.print()

    menu = Table(box=None, show_header=False, padding=(0, 1), expand=False)
    menu.add_column("KEY", style="bold bright_green", width=5)
    menu.add_column("ACTION", style="bold white", width=23)
    menu.add_column("DETAIL", style="dim")
    menu.add_row("01", "Search literature", "Find and open papers")
    menu.add_row("02", "Investigate", "Build evidence-backed answers")
    menu.add_row("03", "Sync Zotero", "Refresh your paper index")
    menu.add_row("04", "Papers workspace", "Open your working folder")
    menu.add_row("05", "Exit", "Close PaperMate")

    console.print(Text("FIELD GUIDE", style="bold bright_green"))
    console.print(menu)
    console.print()
    console.print(Text("-" * 62, style="green"))
    console.print(Text("LOCAL-FIRST  |  papermate status for diagnostics", style="dim green"))
    console.print()


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="papermate",
        description="PaperMate — your local-first research companion.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Show basic system status")

    library = subparsers.add_parser("library", help="Manage your paper library")
    library_sub = library.add_subparsers(dest="library_command")
    library_sub.add_parser("status", help="Show library index status")
    library_sub.add_parser("sync", help="Synchronize library metadata")
    search = library_sub.add_parser("search", help="Search indexed papers")
    search.add_argument("query", help="Words to search for")
    library_sub.add_parser("index-pdfs", help="Extract text from Zotero PDFs")
    search_text = library_sub.add_parser("search-text", help="Search extracted PDF text")
    search_text.add_argument("query", help="Words to search for")

    library_sub.add_parser("attachments", help="List Zotero PDF attachments")
    library_sub.add_parser("papers-with-pdfs", help="List papers and their PDF availability")
    show = library_sub.add_parser("show", help="Show a paper and linked PDFs")
    show.add_argument("zotero_key", help="Zotero item key")
    open_pdf = library_sub.add_parser("open-pdf", help="Open an existing Zotero PDF")
    open_pdf.add_argument("zotero_key", help="Paper or attachment Zotero key")

    research = subparsers.add_parser("research", help="Research a question")
    research.add_argument("question", nargs="+", help="Research question")
    research.add_argument(
        "--max-sources", type=int, choices=range(1, 51), default=10,
        help="Maximum sources to retrieve (1-50; default: 10)",
    )
    research.add_argument("--project-id", help="Optional project identifier")
    research.add_argument(
        "--no-citations", action="store_true",
        help="Disable answer-wide citation coverage requirement",
    )

    args = parser.parse_args()

    if args.command is None:
        papers_folder = Path("data") / "papers"
        papers_folder.mkdir(parents=True, exist_ok=True)

        show_intro()
        while True:
            show_welcome()
            try:
                choice = input("  Choose [1-5]: ").strip()

                if choice == "1":
                    query = input("\n  Search papers: ").strip()
                    if query:
                        main_with_args = ["library", "search", query]
                        sys.argv = [sys.argv[0], *main_with_args]
                        return main()

                elif choice == "2":
                    question = input("\n  Research question: ").strip()
                    if question:
                        sys.argv = [sys.argv[0], "research", *question.split()]
                        return main()

                elif choice == "3":
                    sys.argv = [sys.argv[0], "library", "sync"]
                    return main()

                elif choice == "4":
                    try:
                        os.startfile(str(papers_folder.resolve()))
                    except Exception as exc:
                        print(f"  Could not open folder: {exc}")
                        print(f"  Folder: {papers_folder.resolve()}")
                    input("\n  Press Enter to return to the menu...")
                    continue

                elif choice == "5":
                    print("\n  Stay curious. Goodbye.\n")
                    return 0

                else:
                    print("  Choose a number from 1 to 5.")
                    input("\n  Press Enter to continue...")
            except (EOFError, KeyboardInterrupt):
                print("\n  Goodbye.\n")
                return 0

    if args.command == "status":
        print("PaperMate status")
        print("Research API: configured in backend")
        status = LibraryIndex().status()
        print("Library initialized:", status["initialized"])
        print("Papers indexed:", status["paper_count"])
        return 0

    if args.command == "library":
        if args.library_command is None:
            library.print_help()
            return 0
        index = LibraryIndex()

        if args.library_command == "status":
            status = index.status()
            pdf_status = PDFTextIndex().status()
            print("PaperMate Library")
            print(f"Initialized: {status['initialized']}")
            print(f"Papers indexed: {status['paper_count']}")
            print(f"PDFs text-indexed: {pdf_status['document_count']}")
            print(f"PDF pages indexed: {pdf_status['page_count']}")
            print(f"Database: {status['database']}")
            return 0

        if args.library_command == "search":
            try:
                results = index.search(args.query)
            except Exception as exc:
                print(f"Search failed: {exc}", file=sys.stderr)
                return 1

            if not results:
                print("No matching papers found. Sync or index papers first.")
                return 0

            print(f"\\n  PAPERS FOUND: {len(results)}\\n")
            for number, paper in enumerate(results, 1):
                title = paper.get("title") or "Untitled"
                year = paper.get("year") or "Year unknown"
                creators = paper.get("creators") or "Author unknown"
                if isinstance(creators, list):
                    creators = "; ".join(str(x) for x in creators[:3])
                elif isinstance(creators, str):
                    creators = creators.split(";")[0]
                print(f"  [{number}] {title} ({year})")
                print(f"      {creators}")
                print(f"      Zotero key: {paper.get('zotero_key', 'Unknown')}")
                if paper.get("doi"):
                    print(f"      DOI: {paper['doi']}")
                print()

            try:
                selected = input("  Enter paper number to open, or Enter to return: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return 0

            if not selected:
                return 0
            if not selected.isdigit() or not 1 <= int(selected) <= len(results):
                print("  Invalid paper number.")
                return 0

            paper = results[int(selected) - 1]
            key = paper.get("zotero_key")
            if not key:
                print("  This result has no Zotero key.")
                return 1

            print("\\n  [1] Open in Zotero")
            print("  [2] Open PDF")
            print("  [3] Back")
            try:
                action = input("  Choose [1-3]: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return 0

            if action == "1":
                import webbrowser
                from urllib.parse import quote
                uri = f"zotero://select/library/items/{quote(str(key))}"
                try:
                    if not webbrowser.open(uri):
                        print("  Could not open Zotero. Is the desktop app installed<")
                except Exception as exc:
                    print(f"  Could not open Zotero: {exc}")
            elif action == "2":
                return main(["library", "open-pdf", str(key)])
            elif action != "3":
                print("  Invalid selection.")
            return 0

        if args.library_command == "index-pdfs":
            try:
                result = PDFTextIndex().sync(ZoteroLocalClient())
            except Exception as exc:
                print(f"PDF indexing failed: {exc}", file=sys.stderr)
                return 1

            print(f"PDF attachments found: {result['attachments_found']}")
            print(f"Indexed: {result['indexed']}")
            print(f"Skipped: {result['skipped']}")
            print(f"Failures: {result['failures']}")
            return 0 if result["failures"] == 0 else 1

        if args.library_command == "search-text":
            try:
                results = PDFTextIndex().search(args.query)
            except Exception as exc:
                print(f"PDF text search failed: {exc}", file=sys.stderr)
                return 1

            if not results:
                pdf_status = PDFTextIndex().status()
                if pdf_status["document_count"] == 0:
                    print("No PDF text is indexed yet. Run 'python papermate.py library index-pdfs' first.")
                else:
                    print(f"No matches found in {pdf_status['document_count']} text-indexed PDF(s).")
                return 0

            for number, result in enumerate(results, 1):
                print(f"{number}. {result.get('title') or 'Untitled'}")
                print(f"   Zotero key: {result['parent_key']}")
                print(f"   PDF: {result['filename']}")
                if result.get("page") is not None:
                    print(f"   PDF page: {result['page']}")
                print(f"   {result['excerpt']}")
            return 0

        if args.library_command == "open-pdf":
            import subprocess
            from urllib.parse import unquote, urlparse
            from pathlib import Path as _LocalPath

            try:
                items = ZoteroLocalClient().fetch_raw_items()
            except Exception as exc:
                print(f"Zotero read failed: {exc}", file=sys.stderr)
                return 1

            target = next(
                (x for x in items if x.get("key") == args.zotero_key),
                None,
            )
            if target is None:
                print(f"Zotero item not found: {args.zotero_key}")
                return 1

            data = target.get("data", {})
            if data.get("itemType") != "attachment":
                target = next(
                    (
                        x for x in items
                        if x.get("data", {}).get("itemType") == "attachment"
                        and x.get("data", {}).get("parentItem") == args.zotero_key
                        and x.get("data", {}).get("contentType") == "application/pdf"
                    ),
                    None,
                )
                if target is None:
                    print("No PDF attachment found for this paper.")
                    return 1
                data = target.get("data", {})

            if data.get("contentType") != "application/pdf":
                print("Selected Zotero attachment is not a PDF.")
                return 1

            try:
                response = httpx.get(
                    f"http://127.0.0.1:23119/api/users/0/items/{target['key']}/file",
                    headers={"Zotero-API-Version": "3"},
                    follow_redirects=False,
                    trust_env=False,
                    timeout=10,
                )
                if response.status_code != 302:
                    print(f"Zotero did not return a file redirect (HTTP {response.status_code}).")
                    return 1

                location = response.headers.get("Location", "")
                parsed = urlparse(location)
                if parsed.scheme.lower() != "file":
                    print("Zotero returned an unexpected file location.")
                    return 1

                file_path = Path(unquote(parsed.path.lstrip("/")))
                if len(str(file_path)) >= 3 and str(file_path)[1:3] == ":\\":
                    pass
                else:
                    file_path = Path(unquote(location.removeprefix("file:///")))

                if not file_path.is_file():
                    print("The linked PDF file does not exist at the returned path.")
                    return 1

                os.startfile(str(file_path))
                print(f"Opening PDF: {file_path.name}")
                return 0
            except Exception as exc:
                print(f"Could not open PDF: {exc}", file=sys.stderr)
                return 1

        if args.library_command == "show":
            try:
                items = ZoteroLocalClient().fetch_raw_items()
            except Exception as exc:
                print(f"Zotero read failed: {exc}", file=sys.stderr)
                return 1

            item = next(
                (x for x in items if x.get("key") == args.zotero_key),
                None,
            )
            if item is None:
                print(f"Zotero item not found: {args.zotero_key}")
                return 1

            data = item.get("data", {})
            if data.get("itemType") == "attachment":
                print("This key belongs to an attachment, not a paper.")
                print("Parent item:", data.get("parentItem") or "None")
                print("Filename:", data.get("filename") or data.get("title") or "Unknown")
                return 0

            print(data.get("title") or "Untitled")
            print("Zotero key:", item.get("key"))
            print("Type:", data.get("itemType", "Unknown"))
            print("Date:", data.get("date") or "Unknown")
            print("DOI:", data.get("DOI") or "Not available")
            print("URL:", data.get("url") or "Not available")

            attachments = [
                x for x in items
                if x.get("data", {}).get("itemType") == "attachment"
                and x.get("data", {}).get("parentItem") == args.zotero_key
            ]
            if attachments:
                print(f"Attachments: {len(attachments)}")
                for attachment in attachments:
                    adata = attachment.get("data", {})
                    print("- Filename:", adata.get("filename") or adata.get("title") or "Unknown")
                    print("  Attachment key:", attachment.get("key"))
            else:
                print("Attachments: none found")
            return 0

        if args.library_command == "papers-with-pdfs":
            try:
                client = ZoteroLocalClient()
                items = client.fetch_raw_items()
            except Exception as exc:
                print(f"Zotero read failed: {exc}", file=sys.stderr)
                return 1

            attachments_by_parent = {}
            for item in items:
                data = item.get("data", {})
                if data.get("itemType") == "attachment" and data.get("parentItem"):
                    attachments_by_parent.setdefault(data["parentItem"], []).append(
                        data.get("filename") or data.get("title") or "Unnamed attachment"
                    )

            papers = [
                item for item in items
                if item.get("data", {}).get("itemType") == "journalArticle"
            ]

            print(f"Journal articles: {len(papers)}")
            for item in papers:
                data = item.get("data", {})
                key = item.get("key", "")
                filenames = attachments_by_parent.get(key, [])
                marker = "PDF available" if filenames else "No attachment found"
                print(f"- {data.get('title') or 'Untitled'} [{marker}]")
                for filename in filenames:
                    print(f"    {filename}")
            return 0

        if args.library_command == "attachments":
            try:
                client = ZoteroLocalClient()
                items = client.fetch_raw_items()
            except AttributeError:
                print("Attachment listing needs a raw-item method in zotero.py.")
                print("No files were changed.")
                return 1
            except Exception as exc:
                print(f"Zotero read failed: {exc}", file=sys.stderr)
                return 1

            attachments = [
                item for item in items
                if item.get("data", {}).get("itemType") == "attachment"
            ]
            if not attachments:
                print("No Zotero attachments found.")
                return 0

            print(f"Zotero attachments: {len(attachments)}")
            for item in attachments:
                data = item.get("data", {})
                print(f"- {data.get('filename') or data.get('title') or 'Untitled'}")
                print(f"  Attachment key: {item.get('key', '')}")
                print(f"  Parent item: {data.get('parentItem') or 'None'}")
                print(f"  Link mode: {data.get('linkMode') or 'Unknown'}")
            return 0

        if args.library_command == "sync":
            print("Connecting to Zotero (read-only)...")
            try:
                papers = ZoteroLocalClient().fetch_items()
                count = index.upsert_papers(papers)
            except ZoteroConnectionError as exc:
                print(f"Zotero connection failed: {exc}", file=sys.stderr)
                return 1
            except Exception as exc:
                print(f"Library sync failed: {exc}", file=sys.stderr)
                return 1

            print(f"Sync complete. Processed {count} paper records.")
            print(f"Indexed total: {index.status()['paper_count']}")
            return 0

        return 0

    if args.command == "research":
        question = " ".join(args.question)
        print("Researching:", question)
        try:
            result = create_research_api().research(
                question,
                project_id=args.project_id,
                max_sources=args.max_sources,
                require_citations=not args.no_citations,
            )
        except Exception as exc:
            print(f"Research failed: {exc}", file=sys.stderr)
            return 1

        answer = result.get("answer") or ""
        print("\\nAnswer\\n------")
        print(answer or "The research API returned an empty answer.")

        references = result.get("references") or result.get("sources") or []
        if references:
            print("\\nReferences\\n----------")
            for number, reference in enumerate(references, 1):
                title = reference.get("title") or "Untitled source"
                year = reference.get("year")
                url = reference.get("url")
                print(f"{number}. {title}" + (f" ({year})" if year else ""))
                if url:
                    print(f"   {url}")
        else:
            print("\\nNo references were returned.")

        claims = result.get("claims", [])
        evidence_items = result.get("evidence", [])
        cited_ids = list(dict.fromkeys(
            evidence_id
            for claim in claims
            for evidence_id in claim.get("evidence_ids", [])
        ))

        evidence_by_id = {
            item.get("evidence_id"): item
            for item in evidence_items
        }

        if claims:
            print("\\nClaim-to-Evidence Map\\n---------------------")
            for claim in claims:
                claim_id = claim.get("claim_id", "Unknown claim")
                print(f"\\n{claim_id}: {claim.get('text', '').strip()}")

                claim_evidence_ids = claim.get("evidence_ids", [])
                if not claim_evidence_ids:
                    print("   No supporting evidence IDs.")
                    continue

                for evidence_id in claim_evidence_ids:
                    item = evidence_by_id.get(evidence_id)
                    if not item:
                        print(f"   [{evidence_id}] Evidence record not found.")
                        continue

                    page = item.get("page")
                    location = item.get("location")
                    page_label = f"PDF p. {page}" if page is not None else "Page unavailable"

                    print(f"   [{evidence_id}] {page_label}")
                    if location:
                        print(f"      File: {location}")
                    print(f"      {item.get('content', '').strip()}")

        for run in result.get("model_runs", []):
            provider = run.get("provider", "unknown")
            model = run.get("model", "unknown")
            print(f"Model: {provider}/{model}")

        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
