"""
Script để build RAG index từ đầu
Sử dụng knowledge base từ chatbot_knowledge_new.json
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.rag_engine import RAGEngine

def main():
    print("=" * 60)
    print("🚀 KHỞI TẠO RAG INDEX")
    print("=" * 60)
    
    # Path to knowledge base
    kb_path = os.path.join(os.path.dirname(__file__), 'data', 'chatbot_knowledge_new.json')
    
    if not os.path.exists(kb_path):
        print(f"❌ Lỗi: Không tìm thấy file {kb_path}")
        return
    
    print(f"📚 Knowledge base: {kb_path}")
    print()
    
    # Initialize RAG engine (will build index automatically)
    print("🔧 Đang khởi tạo RAG engine...")
    rag = RAGEngine(kb_path, model_name='keepitreal/vietnamese-sbert')
    
    if rag.model is None:
        print("❌ Lỗi: Không thể khởi tạo RAG engine")
        return
    
    print()
    print("=" * 60)
    print("✅ RAG INDEX ĐÃ SẴN SÀNG")
    print("=" * 60)
    print(f"📊 Số lượng documents: {len(rag.documents)}")
    print(f"💾 Cache location: {rag.cache_dir}")
    print()
    
    # Test với một số câu hỏi
    print("=" * 60)
    print("🧪 TEST RAG RETRIEVAL")
    print("=" * 60)
    
    test_queries = [
        "Điểm chuẩn ngành Khoa học máy tính năm 2024 là bao nhiêu?",
        "Học phí của trường ICTU",
        "Địa chỉ trường đại học",
        "Ngành nào có điểm chuẩn cao nhất?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Query {i}] {query}")
        results = rag.retrieve(query, top_k=2)
        
        if not results:
            print("  ⚠️  Không tìm thấy kết quả")
            continue
        
        for j, (doc, meta, score) in enumerate(results, 1):
            print(f"  [{j}] Score: {score:.3f} | Type: {meta.get('type', 'N/A')}")
            # Show first 100 chars of document
            doc_preview = doc.replace('\n', ' ')[:100]
            print(f"      {doc_preview}...")
    
    print()
    print("=" * 60)
    print("✅ HOÀN THÀNH")
    print("=" * 60)
    print("🎯 RAG đã sẵn sàng sử dụng trong chatbot!")
    print("💡 Để kích hoạt RAG trong chatbot, set use_rag=True trong ChatbotEngine")


if __name__ == '__main__':
    main()
