"""
RAG (Retrieval Augmented Generation) service using ChromaDB
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import logging
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for knowledge base retrieval"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.collection = None
        self.embedding_model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB and embedding model"""
        try:
            logger.info("Initializing RAG service...")
            
            # Initialize ChromaDB
            self.client = chromadb.Client(ChromaSettings(
                persist_directory=self.settings.chroma_persist_dir,
                anonymized_telemetry=False
            ))
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="knowledge_base",
                metadata={"description": "Voice AI knowledge base"}
            )
            
            # Load embedding model
            self.embedding_model = SentenceTransformer(
                self.settings.embedding_model
            )
            
            logger.info("RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"RAG initialization error: {e}")
            raise
    
    async def add_knowledge(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ):
        """
        Add documents to knowledge base
        
        Args:
            documents: List of text documents
            metadatas: Optional metadata for each document
            ids: Optional IDs for documents
        """
        try:
            if not documents:
                return
            
            # Generate IDs if not provided
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in documents]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(documents).tolist()
            
            # Add to collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas or [{} for _ in documents],
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to knowledge base")
            
        except Exception as e:
            logger.error(f"Error adding knowledge: {e}")
            raise
    
    async def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0].tolist()
            
            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, self.settings.max_rag_results),
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0.0,
                        'relevance': 1.0 - (results['distances'][0][i] if results['distances'] else 0.0)
                    })
            
            logger.info(f"Found {len(formatted_results)} relevant documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"RAG search error: {e}")
            return []
    
    async def get_context_for_query(
        self,
        query: str,
        max_tokens: int = 1000
    ) -> str:
        """
        Get formatted context for a query
        
        Returns context string ready to be injected into prompts.
        """
        try:
            results = await self.search(query)
            
            if not results:
                return "No relevant information found in knowledge base."
            
            # Format context
            context_parts = []
            total_length = 0
            
            for i, result in enumerate(results, 1):
                content = result['content']
                relevance = result['relevance']
                
                # Estimate tokens (rough: 1 token ≈ 4 chars)
                estimated_tokens = len(content) // 4
                
                if total_length + estimated_tokens > max_tokens:
                    break
                
                context_parts.append(
                    f"[Source {i}] (Relevance: {relevance:.2f})\n{content}\n"
                )
                total_length += estimated_tokens
            
            context = "\n".join(context_parts)
            logger.info(f"Generated context with {len(context_parts)} sources")
            
            return context
            
        except Exception as e:
            logger.error(f"Context generation error: {e}")
            return ""
    
    async def seed_knowledge_base(self):
        """
        Seed knowledge base with initial data
        
        For POC, add some sample knowledge.
        """
        try:
            # Check if already seeded
            count = self.collection.count()
            if count > 0:
                logger.info(f"Knowledge base already has {count} documents")
                return
            
            # Sample knowledge for POC
            sample_docs = [
                "Our customer support is available 24/7 via phone, email, and chat. Response time is typically under 2 hours.",
                "To reset your password, go to Settings > Security > Reset Password. You'll receive a verification email.",
                "We offer three pricing tiers: Basic ($9/month), Pro ($29/month), and Enterprise (custom pricing).",
                "Appointments can be booked online through our portal or by calling our scheduling team at 1-800-SCHEDULE.",
                "Our refund policy allows returns within 30 days of purchase for a full refund, no questions asked.",
                "Technical support includes troubleshooting, bug fixes, and feature guidance. Premium support includes dedicated account manager.",
                "To schedule an appointment, provide your preferred date, time, and service type. We'll confirm availability within 1 hour.",
                "Our AI voice agents can handle customer inquiries, book appointments, provide product information, and escalate complex issues.",
                "Integration with CRM systems like Salesforce and HubSpot is available on Pro and Enterprise plans.",
                "Voice calls are recorded for quality assurance. Recordings are stored securely and deleted after 90 days."
            ]
            
            metadatas = [
                {"category": "support", "topic": "availability"},
                {"category": "support", "topic": "password"},
                {"category": "pricing", "topic": "plans"},
                {"category": "booking", "topic": "appointments"},
                {"category": "policy", "topic": "refunds"},
                {"category": "support", "topic": "technical"},
                {"category": "booking", "topic": "process"},
                {"category": "product", "topic": "features"},
                {"category": "product", "topic": "integrations"},
                {"category": "policy", "topic": "privacy"}
            ]
            
            await self.add_knowledge(sample_docs, metadatas)
            logger.info("Knowledge base seeded with sample data")
            
        except Exception as e:
            logger.error(f"Knowledge base seeding error: {e}")
