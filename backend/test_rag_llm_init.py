"""Quick diagnostic script for RAG + LLM initialization.
Run: python -m backend.test_rag_llm_init

Outputs:
  - Embedding model load status
  - Number of documents indexed
  - Top-2 retrieval for a sample query
  - Selected LLM provider and a short generation test (if available)
"""
import os
from dotenv import load_dotenv
from .rag_engine import RAGEngine, HAS_RAG_DEPS
from .llm_provider import get_llm_provider, create_rag_prompt

SAMPLE_QUERY = "Học phí ICTU"  # Vietnamese tuition query

def main():
    load_dotenv()
    kb_path = os.getenv('CHATBOT_KNOWLEDGE_BASE') or os.path.join(os.path.dirname(__file__), '..', 'data', 'chatbot_knowledge_new.json')
    print("=" * 70)
    print("RAG + LLM DIAGNOSTIC")
    print("=" * 70)
    print(f"Knowledge Base: {kb_path}")
    print(f"USE_RAG_CHATBOT={os.getenv('USE_RAG_CHATBOT')}")
    if not HAS_RAG_DEPS:
        print("[WARN] sentence-transformers / faiss-cpu not installed. Install per requirements.txt")
        return
    print("[STEP] Initializing RAG engine...")
    rag = RAGEngine(kb_path)
    if rag.model is None or rag.index is None:
        print("[FAIL] RAG engine not fully initialized.")
        return
    print(f"[OK] Documents indexed: {len(rag.documents)} | Cache: {rag.cache_dir}")
    print("[STEP] Sample retrieval:")
    results = rag.retrieve(SAMPLE_QUERY, top_k=2)
    if not results:
        print("[WARN] No retrieval results for sample query.")
    else:
        for i, (doc, meta, score) in enumerate(results, 1):
            preview = ' '.join(doc.split())[:120]
            print(f"  [{i}] score={score:.3f} type={meta.get('type')} preview={preview}...")

    print("[STEP] Selecting LLM provider...")
    provider = get_llm_provider()
    provider_name = provider.__class__.__name__
    print(f"[OK] Provider selected: {provider_name}")
    if getattr(provider, 'available', False):
        prompt = create_rag_prompt(SAMPLE_QUERY, results)
        print("[STEP] Generating short answer (max_tokens=120)...")
        answer = provider.generate(prompt, max_tokens=120, temperature=0.7)
        print("Answer:\n" + answer)
    else:
        print("[INFO] Provider not available (likely missing API key). Snippet fallback will be used in chatbot.")
    print("=" * 70)
    print("DONE")

if __name__ == '__main__':
    main()
