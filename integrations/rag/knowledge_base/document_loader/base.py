"""
Document Loaders for various file types.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import os
import hashlib


@dataclass
class LoadedDocument:
    """Represents a loaded document."""
    id: str
    content: str
    source: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "metadata": self.metadata
        }


class BaseDocumentLoader(ABC):
    """Abstract base document loader."""
    
    @abstractmethod
    async def load(self, source: str) -> List[LoadedDocument]:
        """Load documents from source."""
        pass
    
    @abstractmethod
    async def load_batch(self, sources: List[str]) -> List[LoadedDocument]:
        """Load multiple documents."""
        pass
    
    def _generate_id(self, content: str, source: str) -> str:
        """Generate document ID."""
        hash_input = f"{source}:{content[:100]}"
        return hashlib.md5(hash_input.encode()).hexdigest()


class TextLoader(BaseDocumentLoader):
    """Load plain text files."""
    
    def __init__(
        self,
        encoding: str = "utf-8",
        autodetect_encoding: bool = True
    ):
        self.encoding = encoding
        self.autodetect_encoding = autodetect_encoding
    
    async def load(self, source: str) -> List[LoadedDocument]:
        """Load text file."""
        path = Path(source)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {source}")
        
        # Try encoding detection
        content = None
        if self.autodetect_encoding:
            encodings = ["utf-8", "latin-1", "cp1252", "ascii"]
            for enc in encodings:
                try:
                    content = path.read_text(encoding=enc)
                    break
                except UnicodeDecodeError:
                    continue
        
        if content is None:
            content = path.read_text(encoding=self.encoding)
        
        doc = LoadedDocument(
            id=self._generate_id(content, source),
            content=content,
            source=str(path.absolute()),
            metadata={
                "filename": path.name,
                "extension": path.suffix,
                "size_bytes": path.stat().st_size
            }
        )
        
        return [doc]
    
    async def load_batch(self, sources: List[str]) -> List[LoadedDocument]:
        """Load multiple files."""
        results = []
        for source in sources:
            docs = await self.load(source)
            results.extend(docs)
        return results


class MarkdownLoader(BaseDocumentLoader):
    """Load Markdown files."""
    
    def __init__(
        self,
        extract_headers: bool = True,
        remove_code_blocks: bool = False,
        **kwargs
    ):
        self.extract_headers = extract_headers
        self.remove_code_blocks = remove_code_blocks
        self.text_loader = TextLoader(**kwargs)
    
    async def load(self, source: str) -> List[LoadedDocument]:
        """Load Markdown file."""
        docs = await self.text_loader.load(source)
        
        for doc in docs:
            # Process markdown
            content = doc.content
            
            # Extract headers
            if self.extract_headers:
                import re
                headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
                doc.metadata["headers"] = [
                    {"level": len(h[0]), "text": h[1]}
                    for h in headers
                ]
            
            # Remove code blocks if requested
            if self.remove_code_blocks:
                import re
                content = re.sub(r'```[\s\S]*?```', '', content)
                content = re.sub(r'`[^`]+`', '', content)
                doc.content = content.strip()
            
            doc.metadata["format"] = "markdown"
        
        return docs
    
    async def load_batch(self, sources: List[str]) -> List[LoadedDocument]:
        """Load multiple files."""
        results = []
        for source in sources:
            docs = await self.load(source)
            results.extend(docs)
        return results


class PDFLoader(BaseDocumentLoader):
    """Load PDF files."""
    
    def __init__(
        self,
        extract_images: bool = False,
        ocr_enabled: bool = False,
        **kwargs
    ):
        self.extract_images = extract_images
        self.ocr_enabled = ocr_enabled
        self.kwargs = kwargs
    
    async def load(self, source: str) -> List[LoadedDocument]:
        """Load PDF file."""
        try:
            import pypdf
        except ImportError:
            raise ImportError(
                "pypdf not installed. Install with: pip install pypdf"
            )
        
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {source}")
        
        reader = pypdf.PdfReader(str(path))
        
        documents = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            
            doc = LoadedDocument(
                id=self._generate_id(text, f"{source}:page{i}"),
                content=text,
                source=str(path.absolute()),
                metadata={
                    "filename": path.name,
                    "page": i + 1,
                    "total_pages": len(reader.pages),
                    "format": "pdf"
                }
            )
            documents.append(doc)
        
        return documents
    
    async def load_batch(self, sources: List[str]) -> List[LoadedDocument]:
        """Load multiple PDFs."""
        results = []
        for source in sources:
            docs = await self.load(source)
            results.extend(docs)
        return results


class HTMLLoader(BaseDocumentLoader):
    """Load HTML files."""
    
    def __init__(
        self,
        remove_boilerplate: bool = True,
        extract_links: bool = False,
        **kwargs
    ):
        self.remove_boilerplate = remove_boilerplate
        self.extract_links = extract_links
        self.kwargs = kwargs
    
    async def load(self, source: str) -> List[LoadedDocument]:
        """Load HTML file."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            raise ImportError(
                "beautifulsoup4 not installed. Install with: pip install beautifulsoup4"
            )
        
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {source}")
        
        html_content = path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove scripts and styles
        for element in soup(["script", "style", "nav", "footer"]):
            element.decompose()
        
        # Get text
        text = soup.get_text(separator="\n", strip=True)
        
        # Extract metadata
        metadata = {"format": "html", "filename": path.name}
        
        # Title
        if soup.title:
            metadata["title"] = soup.title.string
        
        # Links
        if self.extract_links:
            links = [a.get("href") for a in soup.find_all("a", href=True)]
            metadata["links"] = links
        
        doc = LoadedDocument(
            id=self._generate_id(text, source),
            content=text,
            source=str(path.absolute()),
            metadata=metadata
        )
        
        return [doc]
    
    async def load_batch(self, sources: List[str]) -> List[LoadedDocument]:
        """Load multiple files."""
        results = []
        for source in sources:
            docs = await self.load(source)
            results.extend(docs)
        return results


class DirectoryLoader(BaseDocumentLoader):
    """Load all files from a directory."""
    
    def __init__(
        self,
        directory: str,
        glob_pattern: str = "**/*",
        file_types: Optional[List[str]] = None,
        recursive: bool = True,
        loader_map: Optional[Dict[str, BaseDocumentLoader]] = None
    ):
        self.directory = directory
        self.glob_pattern = glob_pattern
        self.file_types = file_types
        self.recursive = recursive
        self.loader_map = loader_map or self._