"""Zotero Web API Client."""
import requests
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import json

ZOTERO_API_BASE = "https://api.zotero.org"

@dataclass
class ZoteroItem:
    """A Zotero library item."""
    key: str
    title: str = ""
    item_type: str = ""
    authors: List[str] = field(default_factory=list)
    year: str = ""
    doi: str = ""
    url: str = ""
    abstract: str = ""
    journal: str = ""
    tags: List[str] = field(default_factory=list)
    collections: List[str] = field(default_factory=list)
    pdf_attachment: Optional[Dict] = None
    raw: Dict = field(default_factory=dict)

class ZoteroClient:
    """
    Client for Zotero Web API.
    
    Setup:
    1. Get API key: https://www.zotero.org/settings/keys
    2. Find User ID: https://www.zotero.org/settings/keys (shown at top)
    3. Group ID (optional): From group settings page
    """
    
    def __init__(self, api_key: str = None, user_id: str = None, group_id: str = None):
        self.api_key = api_key
        self.user_id = user_id
        self.group_id = group_id
        self.base_url = ZOTERO_API_BASE
        self.session = requests.Session()
        self._connected = False
        self._last_error = ""
        
        if api_key:
            self._test_connection()
    
    def _get_headers(self) -> Dict:
        return {
            "Zotero-API-Key": self.api_key,
            "Zotero-API-Version": "3",
            "Accept": "application/json"
        }
    
    def _test_connection(self):
        """Test if API key works."""
        if self.user_id:
            try:
                url = f"{self.base_url}/users/{self.user_id}/items"
                response = self.session.get(
                    url,
                    headers=self._get_headers(),
                    params={"limit": 1},
                    timeout=10
                )
                if response.status_code == 200:
                    self._connected = True
                elif response.status_code == 403:
                    self._last_error = "Invalid API key or permissions"
                else:
                    self._last_error = f"HTTP {response.status_code}"
            except Exception as e:
                self._last_error = str(e)
    
    @property
    def connected(self) -> bool:
        return self._connected
    
    @property
    def last_error(self) -> str:
        return self._last_error
    
    def configure(self, api_key: str, user_id: str, group_id: str = None):
        """Configure Zotero connection."""
        self.api_key = api_key
        self.user_id = user_id
        self.group_id = group_id
        self._test_connection()
    
    def get_collections(self) -> List[Dict]:
        """Get all collections."""
        if not self.connected:
            return []
        
        url = f"{self.base_url}/users/{self.user_id}/collections"
        try:
            response = self.session.get(
                url, headers=self._get_headers(), timeout=10
            )
            if response.status_code == 200:
                return response.json().get("data", [])
        except:
            pass
        return []
    
    def get_items(self, collection_key: str = None, limit: int = 50) -> List[ZoteroItem]:
        """Get items, optionally filtered by collection."""
        if not self.connected:
            return []
        
        if self.group_id:
            url = f"{self.base_url}/groups/{self.group_id}/items"
        else:
            url = f"{self.base_url}/users/{self.user_id}/items"
        
        params = {
            "limit": limit,
            "itemType": "-attachment",
            "format": "json"
        }
        
        if collection_key:
            url = f"{self.base_url}/users/{self.user_id}/collections/{collection_key}/items"
        
        items = []
        start = 0
        
        while len(items) < limit:
            params["start"] = start
            try:
                response = self.session.get(
                    url, headers=self._get_headers(), params=params, timeout=15
                )
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                batch = data.get("data", [])
                
                if not batch:
                    break
                
                for item in batch:
                    zitem = self._parse_item(item)
                    if zitem and zitem.title:
                        items.append(zitem)
                
                start += len(batch)
                time.sleep(0.5)
                
                if len(batch) < params["limit"]:
                    break
            
            except:
                break
        
        return items[:limit]
    
    def _parse_item(self, raw: Dict) -> Optional[ZoteroItem]:
        """Parse a Zotero item into our format."""
        try:
            data = raw.get("data", {})
            
            # Extract authors
            authors = []
            for creator in data.get("creators", []):
                name = f"{creator.get('firstName', '')} {creator.get('lastName', '')}".strip()
                if name:
                    authors.append(name)
            
            # Extract year
            year = data.get("date", "")
            if year and len(year) >= 4:
                year = year[:4]
            
            # Extract tags
            tags = [t.get("tag", "") for t in data.get("tags", []) if t.get("tag")]
            
            # Extract collections
            collections = raw.get("data", {}).get("collections", [])
            
            return ZoteroItem(
                key=raw.get("key", ""),
                title=data.get("title", ""),
                item_type=data.get("itemType", ""),
                authors=authors,
                year=year,
                doi=data.get("DOI", ""),
                url=data.get("url", ""),
                abstract=data.get("abstractNote", ""),
                journal=data.get("publicationTitle", "") or data.get("journalAbbreviation", ""),
                tags=tags,
                collections=collections,
                raw=raw
            )
        except:
            return None
    
    def get_item_attachments(self, item_key: str) -> List[Dict]:
        """Get PDF attachments for an item."""
        if not self.connected:
            return []
        
        url = f"{self.base_url}/users/{self.user_id}/items/{item_key}/children"
        params = {"itemType": "attachment"}
        
        try:
            response = self.session.get(
                url, headers=self._get_headers(), params=params, timeout=10
            )
            if response.status_code == 200:
                return response.json().get("data", [])
        except:
            pass
        return []
    
    def download_attachment(self, item_key: str, attachment_key: str, save_path: str) -> bool:
        """Download a PDF attachment."""
        if not self.connected:
            return False
        
        url = f"{self.base_url}/users/{self.user_id}/items/{item_key}/children/{attachment_key}/file"
        
        try:
            response = self.session.get(
                url, headers=self._get_headers(), timeout=30, stream=True
            )
            if response.status_code == 200 and response.content:
                with open(save_path, "wb") as f:
                    for chunk in response.iter_content(8192):
                        f.write(chunk)
                return True
        except:
            pass
        return False
    
    def search(self, query: str, limit: int = 20) -> List[ZoteroItem]:
        """Search Zotero library."""
        if not self.connected:
            return []
        
        url = f"{self.base_url}/users/{self.user_id}/items"
        params = {"q": query, "limit": limit, "itemType": "-attachment"}
        
        try:
            response = self.session.get(
                url, headers=self._get_headers(), params=params, timeout=15
            )
            if response.status_code == 200:
                items = []
                for raw in response.json().get("data", []):
                    zitem = self._parse_item({"key": raw.get("key", ""), "data": raw})
                    if zitem:
                        items.append(zitem)
                return items
        except:
            pass
        return []
    
    def export_bibtex(self, item_keys: List[str]) -> str:
        """Export items as BibTeX."""
        if not self.connected or not item_keys:
            return ""
        
        url = f"{self.base_url}/users/{self.user_id}/items"
        params = {
            "itemKey": ",".join(item_keys[:50]),
            "format": "bibtex"
        }
        
        try:
            response = self.session.get(
                url, headers=self._get_headers(), params=params, timeout=15
            )
            if response.status_code == 200:
                return response.text
        except:
            pass
        return ""