import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class WebScraper:
    """Scrape and extract content from web pages"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'MRWA-Bot/1.0 (Research & Analysis Tool)'
        }
        self.timeout = 10
    
    def scrape(self, url: str) -> Dict[str, Any]:
        """Scrape web page and extract content"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            result = {
                "success": True,
                "url": url,
                "status_code": response.status_code,
                "title": self._extract_title(soup),
                "description": self._extract_description(soup),
                "text_content": self._extract_text(soup),
                "links": self._extract_links(soup, url),
                "metadata": self._extract_metadata(soup),
                "content_length": len(response.content)
            }
            
            logger.info(f"Successfully scraped: {url}")
            return result
            
        except Exception as e:
            logger.error(f"Web scraping failed for {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "url": url
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        if soup.title:
            return soup.title.string.strip()
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        return "No title found"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        return ""
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract main text content"""
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:10000]
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links"""
        links = []
        for a in soup.find_all('a', href=True):
            url = urljoin(base_url, a['href'])
            text = a.get_text().strip()
            if text:
                links.append({"url": url, "text": text})
        return links[:50]
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract various metadata"""
        metadata = {}
        for tag in soup.find_all('meta', attrs={'property': lambda x: x and x.startswith('og:')}):
            key = tag.get('property', '').replace('og:', '')
            metadata[f"og_{key}"] = tag.get('content', '')
        return metadata
