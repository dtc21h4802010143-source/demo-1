"""
RAG Engine - Retrieval-Augmented Generation cho Chatbot ICTU
Sử dụng sentence-transformers để tạo embeddings và FAISS để vector search
"""
import json
import os
import pickle
from typing import List, Dict, Tuple
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    HAS_RAG_DEPS = True
except ImportError:
    HAS_RAG_DEPS = False
    print("[RAG] Warning: sentence-transformers or faiss-cpu not installed. RAG will be disabled.")
    print("[RAG] Install with: pip install sentence-transformers faiss-cpu")


class RAGEngine:
    def __init__(self, knowledge_base_path: str, model_name: str = 'keepitreal/vietnamese-sbert'):
        """
        Khởi tạo RAG engine
        Args:
            knowledge_base_path: Đường dẫn tới file JSON chứa kiến thức
            model_name: Tên model sentence-transformers (mặc định dùng Vietnamese SBERT)
        """
        self.knowledge_base_path = knowledge_base_path
        self.model_name = model_name
        self.model = None
        self.index = None
        self.documents = []
        self.metadata = []
        
        # Cache paths
        self.cache_dir = os.path.join(os.path.dirname(knowledge_base_path), '.rag_cache')
        self.index_path = os.path.join(self.cache_dir, 'faiss.index')
        self.docs_path = os.path.join(self.cache_dir, 'documents.pkl')
        self.meta_path = os.path.join(self.cache_dir, 'metadata.pkl')
        
        if HAS_RAG_DEPS:
            self._init_rag()
    
    def _init_rag(self):
        """Khởi tạo model và index"""
        try:
            # Load model
            print(f"[RAG] Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            
            # Load hoặc build index
            if self._cache_exists():
                print("[RAG] Loading cached index...")
                try:
                    self._load_cache()
                except Exception as e:
                    print(f"[RAG] Failed to load cache ({e}). Rebuilding index...")
                    self._build_index()
            else:
                print("[RAG] Building new index from knowledge base...")
                self._build_index()
            
            print(f"[RAG] Index ready with {len(self.documents)} documents")
        except Exception as e:
            print(f"[RAG] Error initializing RAG: {e}")
            # As a last resort, keep model if loaded; index may be None
            if self.model is None:
                try:
                    self.model = SentenceTransformer(self.model_name)
                except Exception:
                    pass
    
    def _cache_exists(self) -> bool:
        """Kiểm tra cache có tồn tại không"""
        return (os.path.exists(self.index_path) and 
                os.path.exists(self.docs_path) and 
                os.path.exists(self.meta_path))
    
    def _load_cache(self):
        """Load index và documents từ cache"""
        self.index = faiss.read_index(self.index_path)
        with open(self.docs_path, 'rb') as f:
            self.documents = pickle.load(f)
        with open(self.meta_path, 'rb') as f:
            self.metadata = pickle.load(f)
    
    def _save_cache(self):
        """Lưu index và documents vào cache"""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            print(f"[RAG] Saving to cache: {self.cache_dir}")
            faiss.write_index(self.index, self.index_path)
            with open(self.docs_path, 'wb') as f:
                pickle.dump(self.documents, f)
            with open(self.meta_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            print(f"[RAG] Cache saved successfully")
        except Exception as e:
            print(f"[RAG] Warning: Could not save cache: {e}")
            print(f"[RAG] Index will work but won't be cached for next run")
    
    def _build_index(self):
        """Xây dựng FAISS index từ knowledge base"""
        # Load knowledge base
        with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
            knowledge = json.load(f)
        
        # Extract và chunk documents
        self.documents, self.metadata = self._extract_documents(knowledge)
        
        if not self.documents:
            print("[RAG] Warning: No documents found in knowledge base")
            return
        
        # Tạo embeddings
        print(f"[RAG] Creating embeddings for {len(self.documents)} documents...")
        embeddings = self.model.encode(self.documents, show_progress_bar=True, convert_to_numpy=True)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
        
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        
        # Save cache
        self._save_cache()
        print("[RAG] Index built and cached successfully")
    
    def _extract_documents(self, knowledge: Dict) -> Tuple[List[str], List[Dict]]:
        """
        Trích xuất documents từ knowledge base
        Mỗi document là một chunk có thể retrieve được
        """
        documents = []
        metadata = []
        
        # 1. Thông tin chung về trường
        if 'truong_dai_hoc' in knowledge:
            info = knowledge['truong_dai_hoc'].get('thong_tin_chung', {})
            doc = f"""Thông tin trường:
Tên: {info.get('ten_truong', 'N/A')}
Viết tắt: {info.get('ten_viet_tat', 'N/A')}
Địa chỉ: {info.get('dia_chi', 'N/A')}
Website: {info.get('website', 'N/A')}
Email: {info.get('email', 'N/A')}
Hotline: {', '.join(info.get('hotline', []))}"""
            documents.append(doc)
            metadata.append({'type': 'thong_tin_chung', 'source': 'truong_dai_hoc'})
        
        # 2. Thông tin tuyển sinh từng năm
        if 'truong_dai_hoc' in knowledge:
            tuyen_sinh = knowledge['truong_dai_hoc'].get('tuyen_sinh_qua_cac_nam', {})
            for nam, data in tuyen_sinh.items():
                # Tổng quan năm
                doc = f"""Tuyển sinh năm {nam}:
Chỉ tiêu: {data.get('tong_chi_tieu', 'N/A')}
Điểm chuẩn: {data.get('diem_chuan_khoang', 'N/A')}
Phương thức: {', '.join(data.get('phuong_thuc_xet_tuyen', []))}
Học phí: {data.get('hoc_phi', {}).get('theo_nam', data.get('hoc_phi', {}).get('ghi_chu', 'N/A'))}"""
                documents.append(doc)
                metadata.append({'type': 'tuyen_sinh_nam', 'nam': nam, 'source': 'truong_dai_hoc'})
                
                # Chi tiết từng ngành (năm 2024)
                if 'danh_sach_nganh' in data:
                    for nganh_info in data['danh_sach_nganh']:
                        doc = f"""Ngành {nganh_info['nganh']} (Mã: {nganh_info['ma_nganh']}) - Năm {nam}:
Tổ hợp xét tuyển: {', '.join(nganh_info.get('to_hop_xet', []))}
Phương thức: {', '.join(nganh_info.get('phuong_thuc', []))}
Điểm chuẩn thi THPT: {nganh_info.get('diem_chuan', {}).get('thi_thpt', 'N/A')}
Điểm chuẩn học bạ: {nganh_info.get('diem_chuan', {}).get('hoc_ba', 'N/A')}
Học phí: {nganh_info.get('hoc_phi_nganh', 'N/A')}
Ưu tiên: {nganh_info.get('uu_tien', 'N/A')}"""
                        documents.append(doc)
                        metadata.append({
                            'type': 'nganh_hoc',
                            'nam': nam,
                            'ma_nganh': nganh_info['ma_nganh'],
                            'ten_nganh': nganh_info['nganh'],
                            'source': 'truong_dai_hoc'
                        })
        
        # 3. Intents (patterns và responses)
        if 'intents' in knowledge:
            for intent in knowledge['intents']:
                # Mỗi intent thành 1 document
                patterns_str = ', '.join(intent.get('patterns', []))
                responses_str = '\n'.join(intent.get('responses', []))
                doc = f"""Câu hỏi thường gặp về {intent['tag']}:
Các cách hỏi: {patterns_str}
Trả lời:
{responses_str}"""
                documents.append(doc)
                metadata.append({'type': 'intent', 'tag': intent['tag'], 'source': 'intents'})
        
        return documents, metadata
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[str, Dict, float]]:
        """
        Retrieve top-k documents liên quan nhất với query
        Returns: List of (document_text, metadata, similarity_score)
        """
        if not HAS_RAG_DEPS or self.model is None or self.index is None:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):  # Valid index
                results.append((
                    self.documents[idx],
                    self.metadata[idx],
                    float(score)
                ))
        
        return results
    
    def rebuild_index(self):
        """Rebuild index từ đầu (khi knowledge base thay đổi)"""
        if not HAS_RAG_DEPS or self.model is None:
            print("[RAG] Cannot rebuild: dependencies not installed")
            return
        
        print("[RAG] Rebuilding index...")
        self._build_index()


def test_rag():
    """Test RAG engine"""
    import sys
    kb_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'chatbot_knowledge_new.json')
    
    print("=== Testing RAG Engine ===")
    rag = RAGEngine(kb_path)
    
    if not HAS_RAG_DEPS:
        print("RAG dependencies not installed. Skipping test.")
        return
    
    # Test queries
    queries = [
        "Điểm chuẩn ngành Khoa học máy tính năm 2024 là bao nhiêu?",
        "Học phí của trường ICTU",
        "Ngành nào có điểm chuẩn cao nhất?",
        "Địa chỉ trường đại học",
    ]
    
    for q in queries:
        print(f"\nQuery: {q}")
        results = rag.retrieve(q, top_k=2)
        for i, (doc, meta, score) in enumerate(results, 1):
            print(f"  [{i}] Score: {score:.3f} | Type: {meta.get('type')}")
            print(f"      {doc[:150]}...")


if __name__ == '__main__':
    test_rag()
