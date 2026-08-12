"""Zotero sync for PaperMate."""
import os
import time
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from .client import ZoteroClient, ZoteroItem
from app.database import get_session
from app.database.models import Paper

class ZoteroSync:
    def __init__(self, zotero_client: ZoteroClient, project_id: str):
        self.zotero = zotero_client
        self.project_id = project_id
        self.session = get_session()
    
    def sync_all(self) -> Dict:
        if not self.zotero.connected:
            return {"error": "Not connected", "added": 0, "updated": 0}
        
        items = self.zotero.get_items(limit=200)
        added = 0
        updated = 0
        
        for item in items:
            result = self._sync_item(item)
            if result == "added":
                added += 1
            elif result == "updated":
                updated += 1
        
        return {"added": added, "updated": updated, "items_checked": len(items)}
    
    def _sync_item(self, item: ZoteroItem) -> str:
        existing = None
        if item.doi:
            existing = self.session.query(Paper).filter(
                Paper.project_id == self.project_id,
                Paper.doi == item.doi
            ).first()
        
        if not existing and item.title:
            existing = self.session.query(Paper).filter(
                Paper.project_id == self.project_id,
                Paper.title == item.title
            ).first()
        
        paper_data = {
            "title": item.title,
            "authors": ", ".join(item.authors) if item.authors else "",
            "year": item.year,
            "doi": item.doi,
            "url": item.url,
            "abstract": item.abstract or "",
            "journal": item.journal or "",
            "source": "Zotero",
            "tags": item.tags or [],
        }
        
        if existing:
            for key, value in paper_data.items():
                if value and not getattr(existing, key, None):
                    setattr(existing, key, value)
            self.session.commit()
            return "updated"
        else:
            paper = Paper(project_id=self.project_id, **paper_data)
            self.session.add(paper)
            self.session.commit()
            return "added"
    
    def sync_collection(self, collection_key: str) -> Dict:
        if not self.zotero.connected:
            return {"error": "Not connected", "added": 0}
        
        items = self.zotero.get_items(collection_key, limit=100)
        added = 0
        for item in items:
            if self._sync_item(item) == "added":
                added += 1
        return {"added": added}
    
    def _sync_item_from_paper(self, paper):
        """Add a PaperMate paper to Zotero."""
        try:
            import requests
            url = f"https://api.zotero.org/users/{self.zotero.user_id}/items"
            headers = {
                "Zotero-API-Key": self.zotero.api_key,
                "Zotero-API-Version": "3",
                "Content-Type": "application/json"
            }
            
            creators = []
            for a in (paper.authors or "Unknown").split(",")[:5]:
                a = a.strip()
                if a:
                    creators.append({"creatorType": "author", "name": a})
            
            data = [{
                "itemType": "journalArticle",
                "title": paper.title,
                "creators": creators if creators else [{"creatorType": "author", "name": "Unknown"}],
                "date": paper.year or "",
                "DOI": paper.doi or "",
                "url": paper.url or "",
                "abstractNote": (paper.abstract or "")[:500],
                "publicationTitle": paper.journal or "",
                "tags": [{"tag": t} for t in (paper.tags or [])],
            }]
            
            response = requests.post(url, headers=headers, json=data, timeout=15)
            
            if response.status_code in [200, 201]:
                return "added"
            elif response.status_code == 400:
                return "exists_or_bad_data"
            else:
                return f"failed_{response.status_code}"
        
        except Exception as e:
            return f"error_{str(e)[:30]}"
    
    def get_sync_status(self) -> Dict:
        return {"connected": self.zotero.connected}
    
    def close(self):
        self.session.close()