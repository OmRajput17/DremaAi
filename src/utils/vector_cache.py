"""
Vector Store Cache Manager
Handles persistent caching of FAISS vector stores to avoid re-embedding content
"""
import os
import hashlib
import pickle
from pathlib import Path
from typing import Optional
from langchain_community.vectorstores import FAISS
from src.logging import get_logger

logger = get_logger(__name__)


class VectorStoreCache:
    """
    Manages persistent caching of FAISS vector stores.
    
    This cache prevents re-computation of embeddings for the same content,
    significantly improving performance for frequently accessed chapters.
    """
    
    def __init__(self, cache_dir: str = "cache/vector_stores"):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir (str): Directory to store cached vector stores
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"VectorStoreCache initialized at: {self.cache_dir}")
    
    def _generate_cache_key(self, content: str) -> str:
        """
        Generate a unique cache key based on content hash.
        
        Uses SHA-256 hash of the content to create a stable, unique identifier.
        Same content will always produce the same cache key.
        
        Args:
            content (str): Content to hash
        
        Returns:
            str: Hexadecimal hash string (cache key)
        """
        # Create SHA-256 hash of content
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        logger.debug(f"Generated cache key: {content_hash[:16]}...")
        return content_hash
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """
        Get the file path for a cached vector store.
        
        Args:
            cache_key (str): Cache key (content hash)
        
        Returns:
            Path: Path to the cache directory for this key
        """
        return self.cache_dir / cache_key
    
    def exists(self, content: str) -> bool:
        """
        Check if a vector store exists in cache for the given content.
        
        Args:
            content (str): Content to check
        
        Returns:
            bool: True if cache exists, False otherwise
        """
        cache_key = self._generate_cache_key(content)
        cache_path = self._get_cache_path(cache_key)
        
        # FAISS stores as directory with index files
        exists = cache_path.exists() and (cache_path / "index.faiss").exists()
        
        if exists:
            logger.debug(f"Cache HIT for key: {cache_key[:16]}...")
        else:
            logger.debug(f"Cache MISS for key: {cache_key[:16]}...")
        
        return exists
    
    def save(self, content: str, vector_store: FAISS) -> bool:
        """
        Save a vector store to cache.
        
        Args:
            content (str): Content that was embedded (for cache key)
            vector_store (FAISS): Vector store to cache
        
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            cache_key = self._generate_cache_key(content)
            cache_path = self._get_cache_path(cache_key)
            
            # Save FAISS index to disk
            logger.debug(f"Saving vector store to cache: {cache_key[:16]}...")
            vector_store.save_local(str(cache_path))
            
            logger.info(f"Vector store cached successfully: {cache_key[:16]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error saving vector store to cache: {str(e)}", exc_info=True)
            return False
    
    def load(self, content: str, embeddings) -> Optional[FAISS]:
        """
        Load a vector store from cache.
        
        Args:
            content (str): Content to load (for cache key)
            embeddings: Embeddings instance (required for FAISS loading)
        
        Returns:
            Optional[FAISS]: Loaded vector store, or None if not found/error
        """
        try:
            cache_key = self._generate_cache_key(content)
            cache_path = self._get_cache_path(cache_key)
            
            if not self.exists(content):
                logger.debug(f"No cache found for key: {cache_key[:16]}...")
                return None
            
            # Load FAISS index from disk
            logger.debug(f"Loading vector store from cache: {cache_key[:16]}...")
            vector_store = FAISS.load_local(
                str(cache_path),
                embeddings,
                allow_dangerous_deserialization=True  # We control the cache, so this is safe
            )
            
            logger.info(f"Vector store loaded from cache: {cache_key[:16]}...")
            return vector_store
            
        except Exception as e:
            logger.error(f"Error loading vector store from cache: {str(e)}", exc_info=True)
            return None
    
    def get_or_create(self, content: str, embeddings, create_fn) -> FAISS:
        """
        Get vector store from cache, or create and cache if not exists.
        
        This is the main method to use for cache-aware vector store access.
        
        Args:
            content (str): Content to embed
            embeddings: Embeddings instance
            create_fn (callable): Function to create vector store if not cached
                                Should accept (content, embeddings) and return FAISS
        
        Returns:
            FAISS: Vector store (from cache or newly created)
        """
        # Try to load from cache
        vector_store = self.load(content, embeddings)
        
        if vector_store is not None:
            logger.info("Using cached vector store (cache hit)")
            return vector_store
        
        # Cache miss - create new vector store
        logger.info("Creating new vector store (cache miss)")
        vector_store = create_fn(content, embeddings)
        
        # Save to cache for future use
        self.save(content, vector_store)
        
        return vector_store
    
    def clear_cache(self, max_age_days: Optional[int] = None):
        """
        Clear cached vector stores.
        
        Args:
            max_age_days (Optional[int]): If provided, only clear caches older than this many days.
                                         If None, clear all caches.
        """
        import time
        from datetime import timedelta
        
        try:
            removed_count = 0
            current_time = time.time()
            
            for cache_dir in self.cache_dir.iterdir():
                if cache_dir.is_dir():
                    # Check age if max_age_days specified
                    if max_age_days is not None:
                        dir_mtime = cache_dir.stat().st_mtime
                        age_days = (current_time - dir_mtime) / 86400  # seconds to days
                        
                        if age_days < max_age_days:
                            continue  # Skip - not old enough
                    
                    # Remove cache directory
                    import shutil
                    shutil.rmtree(cache_dir)
                    removed_count += 1
                    logger.debug(f"Removed cache: {cache_dir.name[:16]}...")
            
            logger.info(f"Cache cleared: {removed_count} vector stores removed")
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}", exc_info=True)
    
    def get_cache_stats(self) -> dict:
        """
        Get statistics about the cache.
        
        Returns:
            dict: Cache statistics including count and total size
        """
        try:
            total_size = 0
            cache_count = 0
            
            for cache_dir in self.cache_dir.iterdir():
                if cache_dir.is_dir():
                    cache_count += 1
                    # Calculate directory size
                    for file in cache_dir.rglob('*'):
                        if file.is_file():
                            total_size += file.stat().st_size
            
            # Convert bytes to MB
            size_mb = total_size / (1024 * 1024)
            
            return {
                "cache_count": cache_count,
                "total_size_mb": round(size_mb, 2),
                "cache_dir": str(self.cache_dir)
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {"error": str(e)}
