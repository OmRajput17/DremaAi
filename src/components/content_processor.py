"""
Content Processor Component
Handles RAG-based content processing for focused MCQ generation
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from typing import List, Optional
from src.logging import get_logger
from src.utils.vector_cache import VectorStoreCache

# Initialize logger
logger = get_logger(__name__)


class ContentProcessor:
    """
    Process retrieved content using RAG for focused MCQ generation.
    
    This component sits between content retrieval and MCQ generation,
    using embeddings to filter and focus content for better quality
    and reduced LLM costs.
    """
    
    def __init__(self, embeddings, chunk_size=2500, chunk_overlap=500, vector_cache=None):
        """
        Initialize the content processor.
        
        Args:
            embeddings: HuggingFaceEmbeddings instance
            chunk_size (int): Size of text chunks in characters
            chunk_overlap (int): Overlap between chunks in characters
            vector_cache (VectorStoreCache, optional): Cache for vector stores
        """
        logger.info("Initializing ContentProcessor...")
        self.embeddings = embeddings
        self.vector_cache = vector_cache
        
        # Initialize text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        cache_status = "enabled" if vector_cache else "disabled"
        logger.info(f"ContentProcessor initialized with chunk_size={chunk_size}, overlap={chunk_overlap}, cache={cache_status}")
    
    def process_for_mcqs(
        self, 
        content: str, 
        topic_name: str, 
        difficulty: str, 
        num_questions: int
    ) -> str:
        """
        Process content and return focused chunks for MCQ generation.
        
        This method:
        1. Chunks the content into semantic units
        2. Creates embeddings for each chunk
        3. Performs semantic search based on difficulty and topic
        4. Returns only the most relevant chunks
        
        Args:
            content (str): Full chapter/topic content from content fetcher
            topic_name (str): Name of the topic(s) for context
            difficulty (str): 'easy', 'medium', or 'hard'
            num_questions (int): Number of MCQs to be generated
        
        Returns:
            str: Filtered and focused content for MCQ generation
        """
        logger.info(f"Processing content for MCQ generation")
        logger.debug(f"Input: {len(content)} chars, difficulty={difficulty}, num_questions={num_questions}")
        
        try:
            # Generate smart search query based on difficulty and topic
            search_query = self._generate_search_query(topic_name, difficulty)
            logger.debug(f"Generated search query: '{search_query}'")
            
            # Determine optimal number of chunks to retrieve
            k = self._calculate_chunk_count(difficulty, num_questions)
            logger.debug(f"Will retrieve top {k} chunks")
            
            # Split content into chunks
            chunks = self._chunk_content(content)
            logger.info(f"Split content into {len(chunks)} chunks")
            
            # If content is already small, return as-is (no need for RAG)
            if len(chunks) <= k:
                logger.info("Content already small enough, returning original content")
                return content
            
            # Create temporary FAISS vector store from chunks
            vector_store = self._create_vector_store(chunks)
            
            # Retrieve most relevant chunks using semantic search
            relevant_chunks = self._retrieve_relevant_chunks(
                vector_store, 
                search_query, 
                k
            )
            
            # Log retrieved documents/chunks
            logger.info(f"Retrieved {len(relevant_chunks)} relevant chunks from RAG:")
            for idx, chunk in enumerate(relevant_chunks, 1):
                chunk_preview = chunk.page_content[:200].replace('\n', ' ')  # First 200 chars
                logger.info(f"  Chunk {idx}: {chunk_preview}...")
            
            # Merge chunks back into coherent text
            focused_content = self._merge_chunks(relevant_chunks)
            
            # Log reduction stats
            reduction_pct = (1 - len(focused_content) / len(content)) * 100
            logger.info(
                f"Content reduction: {len(content)} → {len(focused_content)} chars "
                f"({reduction_pct:.1f}% reduction)"
            )
            
            return focused_content
            
        except Exception as e:
            logger.error(f"Error processing content: {str(e)}", exc_info=True)
            logger.warning("Falling back to original content due to processing error")
            return content  # Fallback to original content on error
    
    def _chunk_content(self, content: str) -> List[Document]:
        """
        Split content into semantic chunks.
        
        Args:
            content (str): Content to chunk
        
        Returns:
            List[Document]: List of document chunks
        """
        try:
            chunks = self.text_splitter.create_documents([content])
            return chunks
        except Exception as e:
            logger.error(f"Error chunking content: {str(e)}")
            # Fallback: create single document
            return [Document(page_content=content)]
    
    def _create_vector_store(self, chunks: List[Document]) -> FAISS:
        """
        Create FAISS vector store from document chunks.
        Uses cache if available to avoid re-embedding the same content.
        
        Args:
            chunks (List[Document]): Document chunks to embed
        
        Returns:
            FAISS: Vector store with embedded chunks (from cache or newly created)
        """
        # If cache is available, use it
        if self.vector_cache:
            # Combine all chunk content to create cache key
            combined_content = "\n\n".join([doc.page_content for doc in chunks])
            
            # Define function to create vector store if not cached
            def create_fn(content, embeddings):
                logger.debug(f"Creating FAISS vector store from {len(chunks)} chunks")
                return FAISS.from_documents(chunks, embeddings)
            
            # Get from cache or create new
            vector_store = self.vector_cache.get_or_create(
                combined_content, 
                self.embeddings, 
                create_fn
            )
            return vector_store
        else:
            # No cache - create directly
            logger.debug(f"Creating FAISS vector store from {len(chunks)} chunks (no cache)")
            vector_store = FAISS.from_documents(chunks, self.embeddings)
            logger.debug("Vector store created successfully")
            return vector_store
    
    def _retrieve_relevant_chunks(
        self, 
        vector_store: FAISS, 
        query: str, 
        k: int
    ) -> List[Document]:
        """
        Retrieve most relevant chunks using semantic search.
        
        Args:
            vector_store (FAISS): Vector store to search
            query (str): Search query
            k (int): Number of chunks to retrieve
        
        Returns:
            List[Document]: Most relevant document chunks
        """
        logger.debug(f"Retrieving top {k} chunks for query: '{query}'")
        
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
        
        relevant_chunks = retriever.invoke(query)
        logger.debug(f"Retrieved {len(relevant_chunks)} chunks")
        
        return relevant_chunks
    
    def _merge_chunks(self, chunks: List[Document]) -> str:
        """
        Merge document chunks into coherent text.
        
        Args:
            chunks (List[Document]): Chunks to merge
        
        Returns:
            str: Merged content
        """
        # Join with double newline for readability
        merged = "\n\n".join([doc.page_content for doc in chunks])
        logger.debug(f"Merged {len(chunks)} chunks into {len(merged)} chars")
        return merged
    
    def _generate_search_query(self, topic_name: str, difficulty: str) -> str:
        """
        Generate contextual search query based on difficulty level.
        
        Different difficulty levels require different types of content:
        - Easy: Definitions, basic facts, key terms
        - Medium: Concepts, principles, relationships
        - Hard: Complex analysis, applications, problem-solving
        
        Args:
            topic_name (str): Topic/chapter name
            difficulty (str): Difficulty level
        
        Returns:
            str: Optimized search query
        """
        difficulty = difficulty.lower()
        
        query_templates = {
            "easy": f"basic definitions, key terms, simple facts and fundamental concepts about {topic_name}",
            "medium": f"important concepts, principles, processes, relationships and examples in {topic_name}",
            "hard": f"complex analysis, advanced concepts, applications, problem-solving and detailed understanding of {topic_name}"
        }
        
        query = query_templates.get(difficulty, query_templates["medium"])
        logger.debug(f"Generated {difficulty} difficulty query")
        
        return query
    
    def _calculate_chunk_count(self, difficulty: str, num_questions: int) -> int:
        """
        Calculate optimal number of chunks to retrieve.
        
        More questions and higher difficulty require more content chunks.
        
        Args:
            difficulty (str): Difficulty level
            num_questions (int): Number of MCQs to generate
        
        Returns:
            int: Number of chunks to retrieve
        """
        difficulty = difficulty.lower()
        
        # Base chunk counts for each difficulty
        base_chunks = {
            "easy": 6,
            "medium": 10,
            "hard": 16
        }
        
        # Get base count for difficulty
        base = base_chunks.get(difficulty, 6)
        
        # Scale with number of questions
        # More questions = need more diverse content
        scaled = base + (num_questions // 3)
        
        # Cap at reasonable maximum to avoid too much content
        final_count = min(scaled, 15)
        
        logger.debug(f"Calculated chunk count: base={base}, scaled={scaled}, final={final_count}")
        
        return final_count
