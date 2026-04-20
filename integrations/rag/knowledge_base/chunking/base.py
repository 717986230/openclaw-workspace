"""
Text Chunking Strategies.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re


@dataclass
class ChunkConfig:
    """Configuration for chunking."""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    separator: str = "\n\n"
    separators: Optional[List[str]] = None
    keep_separator: bool = False
    length_function: callable = len


@dataclass
class TextChunk:
    """Represents a text chunk."""
    content: str
    index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "index": self.index,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "metadata": self.metadata
        }


class BaseChunker(ABC):
    """Abstract base chunker."""
    
    def __init__(self, config: Optional[ChunkConfig] = None):
        self.config = config or ChunkConfig()
    
    @abstractmethod
    def chunk(self, text: str, metadata: Optional[Dict] = None) -> List[TextChunk]:
        """Split text into chunks."""
        pass
    
    def _calculate_overlap(self, chunks: List[str]) -> List[str]:
        """Add overlap between chunks."""
        if self.config.chunk_overlap == 0:
            return chunks
        
        overlapped = []
        for i, chunk in enumerate(chunks):
            if i == 0:
                overlapped.append(chunk)
            else:
                # Get last N characters from previous chunk
                prev_chunk = overlapped[-1]
                overlap_text = prev_chunk[-self.config.chunk_overlap:]
                overlapped.append(overlap_text + chunk)
        
        return overlapped


class RecursiveChunker(BaseChunker):
    """
    Recursively splits text using multiple separators.
    Tries larger separators first, then smaller ones.
    """
    
    def __init__(self, config: Optional[ChunkConfig] = None):
        super().__init__(config)
        self.separators = self.config.separators or [
            "\n\n",  # Paragraph
            "\n",    # Line
            ". ",    # Sentence
            " ",     # Word
            ""       # Character
        ]
    
    def chunk(self, text: str, metadata: Optional[Dict] = None) -> List[TextChunk]:
        """Recursively chunk text."""
        chunks = self._split_text_recursive(
            text,
            self.separators,
            self.config.chunk_size
        )
        
        # Add overlap
        overlapped = self._calculate_overlap(chunks)
        
        # Convert to TextChunk
        result = []
        start = 0
        for i, chunk in enumerate(overlapped):
            end = start + len(chunk)
            result.append(TextChunk(
                content=chunk,
                index=i,
                start_char=start,
                end_char=end,
                metadata=metadata or {}
            ))
            start = end - self.config.chunk_overlap
        
        return result
    
    def _split_text_recursive(
        self,
        text: str,
        separators: List[str],
        chunk_size: int
    ) -> List[str]:
        """Split text recursively."""
        if not separators:
            return self._split_by_characters(text, chunk_size)
        
        separator = separators[0]
        remaining_separators = separators[1:]
        
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for split in splits:
            split_length = len(split)
            
            if current_length + split_length > chunk_size:
                if current_chunk:
                    chunks.append(separator.join(current_chunk) if separator else "".join(current_chunk))
                current_chunk = [split]
                current_length = split_length
            else:
                current_chunk.append(split)
                current_length += split_length + (len(separator) if separator else 0)
        
        if current_chunk:
            chunks.append(separator.join(current_chunk) if separator else "".join(current_chunk))
        
        # Check if any chunk is too large
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > chunk_size:
                # Recursively split with remaining separators
                final_chunks.extend(
                    self._split_text_recursive(chunk, remaining_separators, chunk_size)
                )
            else:
                final_chunks.append(chunk)
        
        return final_chunks
    
    def _split_by_characters(self, text: str, chunk_size: int) -> List[str]:
        """Split by characters when no separator works."""
        return [
            text[i:i + chunk_size]
            for i in range(0, len(text), chunk_size)
        ]


class FixedSizeChunker(BaseChunker):
    """Fixed-size chunking with optional overlap."""
    
    def chunk(self, text: str, metadata: Optional[Dict] = None) -> List[TextChunk]:
        """Chunk text into fixed sizes."""
        chunks = []
        start = 0
        index = 0
        
        while start < len(text):
            end = min(start + self.config.chunk_size, len(text))
            chunk_text = text[start:end]
            
            chunks.append(TextChunk(
                content=chunk_text,
                index=index,
                start_char=start,
                end_char=end,
                metadata=metadata or {}
            ))
            
            start = end - self.config.chunk_overlap
            index += 1
        
        return chunks


class SemanticChunker(BaseChunker):
    """
    Semantic chunking based on embedding similarity.
    Creates chunks at natural semantic boundaries.
    """
    
    def __init__(
        self,
        config: Optional[ChunkConfig] = None,
        embedding_model: Optional[str] = None,
        similarity_threshold: float = 0.8
    ):
        super().__init__(config)
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
    
    def chunk(self, text: str, metadata: Optional[Dict] = None) -> List[TextChunk]:
        """
        Chunk based on semantic similarity.
        Note: This is a simplified version. Full implementation
        requires embedding model for similarity calculation.
        """
        # Split into sentences first
        sentences = self._split_sentences(text)
        
        if len(sentences) == 0:
            return []
        
        # Group sentences into chunks
        chunks = []
        current_chunk = [sentences[0]]
        current_length = len(sentences[0])
        
        for sentence in sentences[1:]:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > self.config.chunk_size:
                # Start new chunk
                chunk_text = " ".join(current_chunk)
                chunks.append(chunk_text)
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        # Convert to TextChunk
        result = []
        start = 0
        for i, chunk in enumerate(chunks):
            end = start + len(chunk)
            result.append(TextChunk(
                content=chunk,
                index=i,
                start_char=start,
                end_char=end,
                metadata=metadata or {}
            ))
            start = end
        
        return result
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitter
        sentence_endings = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_endings, text)
        return [s.strip() for s in sentences if s.strip()]


class CodeChunker(BaseChunker):
    """Code-aware chunking that respects structure."""
    
    def __init__(
        self,
        config: Optional[ChunkConfig] = None,
        language: str = "python"
    ):
        super().__init__(config)
        self.language = language
    
    def chunk(self, code: str, metadata: Optional[Dict] = None) -> List[TextChunk]:
        """Chunk code respecting function/class boundaries."""
        if self.language == "python":
            return self._chunk_python(code, metadata)
        else:
            # Fallback to recursive chunking
            recursive = RecursiveChunker(self.config)
            return recursive.chunk(code, metadata)
    
    def _chunk_python(self, code: str, metadata: Optional[Dict] = None) -> List[TextChunk]:
        """Chunk Python code."""
        # Split at function/class definitions
        pattern = r'(?=\n(?:class|def|async def)\s+)'
        blocks = re.split(pattern, code)
        
        chunks = []
        start = 0
        index = 0
        
        for block in blocks:
            if not block.strip():
                continue
            
            # Check if block is too large
            if len(block) > self.config.chunk_size:
                # Further split
                recursive = RecursiveChunker(self.config)
                sub_chunks = recursive.chunk(block, metadata)
                for sc in sub_chunks:
                    sc.index = index
                    chunks.append(sc)
                    index += 1
            else:
                end = start + len(block)
                chunks.append(TextChunk(
                    content=block.strip(),
                    index=index,
                    start_char=start,
                    end_char=end,
                    metadata={**(metadata or {}), "language": "python"}
                ))
                index += 1
                start = end
        
        return chunks


def get_chunker(
    strategy: str = "recursive",
    config: Optional[ChunkConfig] = None,
    **kwargs
) -> BaseChunker:
    """Factory function to get chunker."""
    chunkers = {
        "recursive": RecursiveChunker,
        "fixed": FixedSizeChunker,
        "semantic": SemanticChunker,
        "code": CodeChunker
    }
    
    if strategy not in chunkers:
        raise ValueError(f"Unknown chunking strategy: {strategy}")
    
    return chunkers[strategy](config, **kwargs)
