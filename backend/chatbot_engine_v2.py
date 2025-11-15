"""
Chatbot Engine V2 với RAG + LLM
Hỗ trợ cả TF-IDF fallback và RAG-based responses
"""
import json
import os
import logging
from typing import Optional

try:
    from .rag_engine import RAGEngine
    from .llm_provider import get_llm_provider, create_rag_prompt
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"[Chatbot] RAG/LLM not available: {e}")
    RAG_AVAILABLE = False

# Fallback imports for basic chatbot
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    TFIDF_AVAILABLE = True
except ImportError:
    TFIDF_AVAILABLE = False


class ChatbotEngine:
    def __init__(self, knowledge_base_path: str, use_rag: bool = True):
        """
        Khởi tạo Chatbot Engine
        Args:
            knowledge_base_path: Đường dẫn tới file JSON
            use_rag: Sử dụng RAG+LLM (True) hay TF-IDF (False)
        """
        self.knowledge_base_path = knowledge_base_path
        self.use_rag = use_rag and RAG_AVAILABLE
        
        # Load knowledge base
        self.knowledge_base = self.load_knowledge_base(knowledge_base_path)
        
        # Initialize RAG + LLM
        if self.use_rag:
            try:
                print("[Chatbot] Initializing RAG + LLM mode...")
                self.rag_engine = RAGEngine(knowledge_base_path)
                self.llm_provider = get_llm_provider()
                print("[Chatbot] RAG + LLM mode ready")
            except Exception as e:
                print(f"[Chatbot] RAG init failed, falling back to TF-IDF: {e}")
                self.use_rag = False
        
        # Fallback: TF-IDF
        if not self.use_rag and TFIDF_AVAILABLE:
            print("[Chatbot] Initializing TF-IDF fallback mode...")
            self._init_tfidf()
            print("[Chatbot] TF-IDF mode ready")
    
    def load_knowledge_base(self, path: str) -> dict:
        """Load knowledge base JSON"""
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            # Try alternative path (chatbot_knowledge_new.json)
            alt_path = path.replace('chatbot_knowledge.json', 'chatbot_knowledge_new.json')
            try:
                with open(alt_path, 'r', encoding='utf-8') as file:
                    print(f"[Chatbot] Loaded alternative knowledge base: {alt_path}")
                    return json.load(file)
            except Exception as e:
                logging.error(f"Error loading knowledge base: {e}")
                return {"intents": []}
        except Exception as e:
            logging.error(f"Error loading knowledge base: {e}")
            return {"intents": []}
    
    def _init_tfidf(self):
        """Initialize TF-IDF vectorizer (fallback mode)"""
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        
        # Vietnamese stop words
        self.stop_words = {'và', 'của', 'cho', 'trong', 'với', 'các', 'được', 'để', 'có',
                          'những', 'một', 'là', 'này', 'từ', 'khi', 'đến', 'như', 'không',
                          'về', 'tại', 'theo', 'đã', 'sẽ', 'vì', 'nhưng', 'còn', 'bị', 
                          'do', 'phải', 'nếu', 'nên', 'được', 'đang', 'sau', 'rồi', 'thì'}
        
        self.vectorizer = TfidfVectorizer(
            stop_words=list(self.stop_words),
            lowercase=True,
            max_features=5000
        )
        
        # Build corpus
        corpus = []
        self.responses = []
        
        for intent in self.knowledge_base.get('intents', []):
            for pattern in intent.get('patterns', []):
                corpus.append(pattern)
                self.responses.append(intent.get('responses', ['Xin lỗi, tôi chưa hiểu câu hỏi.']))
        
        if corpus:
            try:
                self.response_vectors = self.vectorizer.fit_transform(corpus)
            except Exception as e:
                print(f"[Chatbot] TF-IDF fitting error: {e}")
                self.response_vectors = None
        else:
            print("[Chatbot] Warning: No patterns found in knowledge base")
            self.response_vectors = None
    
    def get_response(self, user_input: str, context: Optional[dict] = None) -> str:
        """
        Lấy response cho user input
        Args:
            user_input: Câu hỏi của user
            context: Context bổ sung (nếu có)
        Returns:
            Response string
        """
        if not user_input or not user_input.strip():
            return "Xin lỗi, tôi không nhận được câu hỏi của bạn. Bạn cần hỗ trợ gì?"
        
        # RAG + LLM mode
        if self.use_rag:
            return self._get_rag_response(user_input)
        
        # Fallback TF-IDF mode
        if TFIDF_AVAILABLE and self.response_vectors is not None:
            return self._get_tfidf_response(user_input)
        
        # Ultimate fallback
        return "Xin lỗi, hệ thống chatbot đang gặp vấn đề. Vui lòng liên hệ hotline 0981 33 66 28 hoặc email tuyensinh@ictu.edu.vn để được hỗ trợ."

    def get_response_with_sources(self, user_input: str, top_k: int = 3) -> dict:
        """Trả về cả câu trả lời và danh sách nguồn (sources) nếu ở chế độ RAG.

        Structure:
        {
          'response': <str>,
          'sources': [ { 'index': i, 'score': float, 'meta': {...}, 'snippet': '...' }, ... ],
          'rag': bool,
          'provider': <provider_class_name or None>
        }
        """
        result = {
            'response': '',
            'sources': [],
            'rag': bool(getattr(self, 'use_rag', False)),
            'provider': getattr(getattr(self, 'llm_provider', None), '__class__', type('X',(),{})).__name__
        }
        if not user_input or not user_input.strip():
            result['response'] = "Xin lỗi, tôi không nhận được câu hỏi của bạn. Bạn cần hỗ trợ gì?"
            return result
        if not self.use_rag:
            # Non-RAG fallback
            result['response'] = self.get_response(user_input)
            return result
        try:
            retrieved_docs = self.rag_engine.retrieve(user_input, top_k=top_k) if hasattr(self, 'rag_engine') else []
            for i, (doc, meta, score) in enumerate(retrieved_docs, start=1):
                snippet = ' '.join(str(doc).split())[:800]
                result['sources'].append({
                    'index': i,
                    'score': float(score),
                    'meta': meta,
                    'snippet': snippet
                })
            # Nếu không có tài liệu
            if not retrieved_docs:
                result['response'] = "Xin lỗi, tôi chưa tìm được thông tin liên quan trong cơ sở tri thức."
                return result
            # Nếu không có LLM provider khả dụng -> tạo câu trả lời từ snippets
            if not getattr(self, 'llm_provider', None) or not getattr(self.llm_provider, 'available', False):
                combined = []
                for s in result['sources']:
                    meta_parts = []
                    m = s['meta']
                    if isinstance(m, dict):
                        for k in ('type','ten_nganh','ma_nganh'):
                            if k in m:
                                meta_parts.append(str(m[k]))
                    label = f"[Tài liệu {s['index']}{' | ' + ', '.join(meta_parts) if meta_parts else ''} | score={s['score']:.3f}]"
                    combined.append(label + "\n" + s['snippet'])
                result['response'] = (
                    "(Chế độ snippet - LLM chưa cấu hình) Tổng hợp thông tin từ cơ sở tri thức:\n\n" +
                    "\n\n".join(combined) +
                    "\n\nĐể có câu trả lời tự nhiên hơn, hãy thêm OPENAI_API_KEY hoặc GOOGLE_API_KEY vào .env rồi khởi động lại."
                )
                return result
            # Có LLM: tạo prompt và gọi LLM
            prompt = create_rag_prompt(user_input, retrieved_docs)
            answer = self.llm_provider.generate(prompt, max_tokens=500, temperature=0.7)
            result['response'] = answer
            return result
        except Exception as e:
            logging.error(f"[Chatbot] get_response_with_sources error: {e}")
            result['response'] = "Xin lỗi, đã xảy ra lỗi nội bộ trong quá trình xử lý câu hỏi."
            return result
    
    def _get_rag_response(self, user_input: str) -> str:
        """Generate response using RAG + LLM"""
        try:
            # Retrieve relevant documents
            retrieved_docs = self.rag_engine.retrieve(user_input, top_k=3)
            
            if not retrieved_docs:
                return "Xin lỗi, tôi chưa tìm được thông tin liên quan. Vui lòng liên hệ hotline 0981 33 66 28 hoặc email tuyensinh@ictu.edu.vn."
            # Nếu LLM provider không khả dụng (fallback), trả về các đoạn trích từ tài liệu thay vì gọi LLM
            if not getattr(self, 'llm_provider', None) or not getattr(self.llm_provider, 'available', False):
                parts = []
                for i, (doc, meta, score) in enumerate(retrieved_docs, start=1):
                    # Lấy snippet ngắn gọn để trả về
                    snippet = ' '.join(str(doc).split())[:800]
                    mstr = ''
                    try:
                        # Hiển thị một vài metadata nếu có
                        if isinstance(meta, dict):
                            mparts = []
                            if 'type' in meta:
                                mparts.append(meta.get('type'))
                            if 'ten_nganh' in meta:
                                mparts.append(meta.get('ten_nganh'))
                            if 'ma_nganh' in meta:
                                mparts.append(meta.get('ma_nganh'))
                            if mparts:
                                mstr = ' | ' + ', '.join(mparts)
                    except Exception:
                        mstr = ''
                    parts.append(f"[Tài liệu {i}{mstr}] (score={float(score):.3f})\n{snippet}")

                return (
                    "Hiện tại hệ thống LLM chưa được cấu hình. Dưới đây là thông tin tìm thấy từ cơ sở tri thức (tài liệu tham khảo):\n\n" +
                    "\n\n".join(parts) +
                    "\n\nNếu bạn muốn câu trả lời tự nhiên hơn, hãy cấu hình OPENAI_API_KEY hoặc GOOGLE_API_KEY trong file .env và khởi động lại server."
                )

            # Create prompt
            prompt = create_rag_prompt(user_input, retrieved_docs)

            # Generate response with LLM
            response = self.llm_provider.generate(prompt, max_tokens=500, temperature=0.7)

            return response
        except Exception as e:
            logging.error(f"[Chatbot] RAG response error: {e}")
            return "Xin lỗi, đã xảy ra lỗi khi xử lý câu hỏi. Vui lòng thử lại hoặc liên hệ hotline 0981 33 66 28."
    
    def _get_tfidf_response(self, user_input: str) -> str:
        """Generate response using TF-IDF similarity (fallback)"""
        try:
            # Vectorize input
            input_vector = self.vectorizer.transform([user_input])
            
            # Calculate similarity
            similarities = cosine_similarity(input_vector, self.response_vectors).flatten()
            
            # Get best match
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]
            
            # Threshold check
            if best_score < 0.3:
                return "Xin lỗi, tôi chưa hiểu rõ câu hỏi của bạn. Bạn có thể diễn đạt lại hoặc liên hệ hotline 0981 33 66 28 / email tuyensinh@ictu.edu.vn được không?"
            
            # Return random response from matched intent
            import random
            responses = self.responses[best_idx]
            return random.choice(responses)
        except Exception as e:
            logging.error(f"[Chatbot] TF-IDF response error: {e}")
            return "Xin lỗi, đã xảy ra lỗi. Vui lòng thử lại."
    
    def rebuild_index(self):
        """Rebuild RAG index (khi knowledge base thay đổi)"""
        if self.use_rag and hasattr(self, 'rag_engine'):
            self.rag_engine.rebuild_index()
            print("[Chatbot] RAG index rebuilt")
        elif TFIDF_AVAILABLE:
            self._init_tfidf()
            print("[Chatbot] TF-IDF re-initialized")


# Backward compatibility: Keep old class name
class ChatbotEngineV1(ChatbotEngine):
    """Alias for backward compatibility"""
    pass


if __name__ == '__main__':
    # Test chatbot
    import sys
    kb_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'chatbot_knowledge_new.json')
    
    print("=== Testing Chatbot Engine ===")
    bot = ChatbotEngine(kb_path, use_rag=True)
    
    queries = [
        "Xin chào",
        "Điểm chuẩn ngành Khoa học máy tính năm 2024 là bao nhiêu?",
        "Học phí của ICTU",
        "Địa chỉ trường",
        "Tạm biệt"
    ]
    
    for q in queries:
        print(f"\nUser: {q}")
        response = bot.get_response(q)
        print(f"Bot: {response}")
