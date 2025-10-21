"""
LLM Wrapper - Hỗ trợ nhiều LLM providers: OpenAI, Google Gemini, HuggingFace
"""
import os
from typing import List, Dict, Optional


class LLMProvider:
    """Base class cho LLM providers"""

    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        raise NotImplementedError


class OpenAICompatProvider(LLMProvider):
    """Provider tương thích OpenAI API qua base_url tuỳ biến (Groq, Together, OpenRouter)."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        try:
            from openai import OpenAI
            self.model = model or os.getenv('LLM_MODEL') or 'gpt-3.5-turbo'
            self.client = OpenAI(
                api_key=api_key or os.getenv('LLM_API_KEY') or os.getenv('OPENAI_API_KEY'),
                base_url=base_url or os.getenv('LLM_BASE_URL')
            )
            self.available = True
        except Exception as e:
            print(f"[LLM] OpenAI-Compat init failed: {e}")
            self.available = False

    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        if not self.available:
            return "[Error] OpenAI-Compat not available"
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Bạn là trợ lý tư vấn tuyển sinh thân thiện và chuyên nghiệp của Trường Đại học Công nghệ Thông tin và Truyền thông - ĐHTN (ICTU)."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error] OpenAI-Compat generation failed: {e}"


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        try:
            import openai
            self.openai = openai
            self.client = openai.OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
            self.model = model
            self.available = True
        except Exception as e:
            print(f"[LLM] OpenAI init failed: {e}")
            self.available = False
    
    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        if not self.available:
            return "[Error] OpenAI not available"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Bạn là trợ lý tư vấn tuyển sinh thân thiện và chuyên nghiệp của Trường Đại học Công nghệ Thông tin và Truyền thông - ĐHTN (ICTU)."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error] OpenAI generation failed: {e}"


class GeminiProvider(LLMProvider):
    """Google Gemini provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Ưu tiên lấy model từ biến môi trường `GEMINI_MODEL`.
        Nếu không có, thử lần lượt các model phổ biến hiện tại.
        """
        try:
            import google.generativeai as genai
            key = api_key or os.getenv('GOOGLE_API_KEY')
            if not key:
                raise RuntimeError("GOOGLE_API_KEY is not set")

            genai.configure(api_key=key)

            # 1) Nếu có GEMINI_MODEL hoặc đối số model, thử trước
            requested = (model or os.getenv('GEMINI_MODEL') or '').strip() or None

            # 2) Lấy danh sách model có hỗ trợ generateContent
            available_models = []
            try:
                for m in genai.list_models():
                    methods = set(getattr(m, 'supported_generation_methods', []) or [])
                    name = getattr(m, 'name', '')
                    # API trả về "models/<name>", ta tách phần sau dấu '/'
                    if name.startswith('models/'):
                        short = name.split('/', 1)[1]
                    else:
                        short = name
                    if 'generateContent' in methods:
                        available_models.append(short)
            except Exception:
                # Nếu list_models thất bại (quyền hạn), dùng danh sách phổ biến
                available_models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']

            # Ghép danh sách ứng viên: requested (nếu có) + các model hợp lệ còn lại
            candidates = []
            seen = set()
            for n in [requested] + available_models:
                if n and n not in seen:
                    candidates.append(n)
                    seen.add(n)

            self._genai = genai
            self._key = key
            self._model_name = None
            self.model = None

            last_err = None
            for name in candidates:
                try:
                    mdl = genai.GenerativeModel(name)
                    # Không gọi generate ngay để tránh lỗi quyền; chỉ lưu model
                    self.model = mdl
                    self._model_name = name
                    break
                except Exception as e:
                    last_err = e
                    self.model = None
                    continue

            if not self.model:
                raise RuntimeError(f"No working Gemini model found. Last error: {last_err}")

            print(f"[LLM] Gemini initialized with model: {self._model_name}")
            self.available = True
        except Exception as e:
            print(f"[LLM] Gemini init failed: {e}")
            self.available = False
    
    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        if not self.available:
            return "[Error] Gemini not available"

        system_prompt = (
            "Bạn là trợ lý tư vấn tuyển sinh thân thiện và chuyên nghiệp của Trường "
            "Đại học Công nghệ Thông tin và Truyền thông - ĐHTN (ICTU)."
        )
        full_prompt = f"{system_prompt}\n\n{prompt}"

        def _call(model_obj):
            return model_obj.generate_content(
                full_prompt,
                generation_config={
                    'max_output_tokens': max_tokens,
                    'temperature': temperature,
                }
            )

        try:
            response = _call(self.model)
            return (response.text or "").strip() or "Xin vui lòng hỏi lại theo cách khác."
        except Exception as e:
            msg = str(e)
            # Nếu lỗi do model không hỗ trợ hoặc 404, thử fallback model khác
            if any(s in msg for s in ["not found", "is not supported for generateContent", "404"]):
                fallbacks = [m for m in ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro'] if m != self._model_name]
                for name in fallbacks:
                    try:
                        alt_model = self._genai.GenerativeModel(name)
                        resp = _call(alt_model)
                        self.model = alt_model
                        self._model_name = name
                        print(f"[LLM] Gemini switched to fallback model: {name}")
                        return (resp.text or "").strip() or "Xin vui lòng hỏi lại theo cách khác."
                    except Exception:
                        continue
            return f"[Error] Gemini generation failed: {e}"


class HuggingFaceProvider(LLMProvider):
    """HuggingFace Inference API provider (text-generation)"""

    def __init__(self, api_key: Optional[str] = None, model: str = "openchat/openchat-3.5-0106"):
        self.api_key = api_key or os.getenv('HUGGINGFACE_API_KEY')
        self.model = model
        self.available = bool(self.api_key)

    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        if not self.available:
            return "[Error] HuggingFace API key not available"
        try:
            import requests
            url = f"https://api-inference.huggingface.co/models/{self.model}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "inputs": prompt,
                "parameters": {"max_new_tokens": max_tokens, "temperature": temperature},
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            # Trả về kết quả đầu tiên
            if isinstance(data, list) and data and 'generated_text' in data[0]:
                return data[0]['generated_text'].strip()
            elif isinstance(data, dict) and 'generated_text' in data:
                return data['generated_text'].strip()
            else:
                return str(data)
        except Exception as e:
            return f"[Error] HuggingFace generation failed: {e}"


class FallbackProvider(LLMProvider):
    """Fallback provider khi không có LLM nào available"""
    
    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        return "Xin lỗi, hiện tại hệ thống chatbot AI chưa được cấu hình. Vui lòng liên hệ hotline 0981 33 66 28 hoặc email tuyensinh@ictu.edu.vn để được hỗ trợ trực tiếp."


def get_llm_provider(provider_name: Optional[str] = None) -> LLMProvider:
    """
    Factory function để lấy LLM provider
    Args:
        provider_name: 'openai', 'gemini', 'groq', 'together', 'openrouter', hoặc None (auto-detect)
    """
    provider_name = provider_name or os.getenv('LLM_PROVIDER', 'auto').lower()

    # 1. Thử Groq trước (miễn phí, nhanh nhất)
    if provider_name in ('groq', 'auto') and os.getenv('GROQ_API_KEY'):
        provider = OpenAICompatProvider(
            api_key=os.getenv('GROQ_API_KEY'),
            base_url=os.getenv('GROQ_BASE_URL'),
            model=os.getenv('GROQ_MODEL')
        )
        if provider.available:
            print("[LLM] Using Groq provider (llama-3.3-70b-versatile)")
            return provider

    # 2. Thử Together AI (miễn phí $25 credit)
    if provider_name in ('together', 'auto') and os.getenv('TOGETHER_API_KEY'):
        provider = OpenAICompatProvider(
            api_key=os.getenv('TOGETHER_API_KEY'),
            base_url=os.getenv('TOGETHER_BASE_URL'),
            model=os.getenv('TOGETHER_MODEL')
        )
        if provider.available:
            print("[LLM] Using Together AI provider")
            return provider

    # 3. Thử OpenRouter (nhiều model miễn phí)
    if provider_name in ('openrouter', 'auto') and os.getenv('OPENROUTER_API_KEY'):
        provider = OpenAICompatProvider(
            api_key=os.getenv('OPENROUTER_API_KEY'),
            base_url=os.getenv('OPENROUTER_BASE_URL'),
            model=os.getenv('OPENROUTER_MODEL')
        )
        if provider.available:
            print("[LLM] Using OpenRouter provider")
            return provider

    # 4. Thử Ollama local (ưu tiên OLLAMA_* trước)
    if provider_name in ('ollama', 'auto'):
        ollama_url = os.getenv('OLLAMA_BASE_URL')
        if ollama_url:
            provider = OpenAICompatProvider(
                api_key=os.getenv('OLLAMA_API_KEY', 'none'),
                base_url=ollama_url,
                model=os.getenv('OLLAMA_MODEL')
            )
            if provider.available:
                print("[LLM] Using Ollama local provider")
                return provider

    # 5. OpenAI (nếu có key)
    if provider_name == 'openai' or (provider_name == 'auto' and os.getenv('OPENAI_API_KEY')):
        provider = OpenAIProvider()
        if provider.available:
            print("[LLM] Using OpenAI provider")
            return provider

    # 6. Gemini (nếu có key)
    if provider_name == 'gemini' or (provider_name == 'auto' and os.getenv('GOOGLE_API_KEY')):
        provider = GeminiProvider()
        if provider.available:
            print("[LLM] Using Gemini provider")
            return provider

    # 7. OpenAI-compatible generic (LLM_BASE_URL)
    if provider_name in ('openai-compat', 'compat') or (provider_name == 'auto' and os.getenv('LLM_BASE_URL')):
        provider = OpenAICompatProvider()
        if provider.available:
            print("[LLM] Using OpenAI-Compatible provider")
            return provider

    # 8. HuggingFace (thường không hoạt động với free tier)
    if provider_name == 'hf' or (provider_name == 'auto' and os.getenv('HUGGINGFACE_API_KEY')):
        provider = HuggingFaceProvider()
        if provider.available:
            print("[LLM] Using HuggingFace provider")
            return provider

    print("[LLM] No LLM provider available, using fallback")
    return FallbackProvider()


def create_rag_prompt(query: str, retrieved_docs: List[tuple]) -> str:
    """
    Tạo prompt cho LLM từ query và retrieved documents
    Args:
        query: Câu hỏi của user
        retrieved_docs: List of (document_text, metadata, score)
    """
    # Build context từ retrieved documents
    context_parts = []
    for i, (doc, meta, score) in enumerate(retrieved_docs, 1):
        context_parts.append(f"[Tài liệu {i}]\n{doc}\n")
    
    context = "\n".join(context_parts) if context_parts else "Không tìm thấy tài liệu liên quan."
    
    prompt = f"""Dựa vào các tài liệu sau đây về Trường Đại học Công nghệ Thông tin và Truyền thông - ĐHTN (ICTU), hãy trả lời câu hỏi của sinh viên một cách chính xác, thân thiện và chuyên nghiệp.

TÀI LIỆU THAM KHẢO:
{context}

CÂU HỎI: {query}

HƯỚNG DẪN TRẢ LỜI:
- Trả lời ngắn gọn, rõ ràng, dễ hiểu
- Chỉ dùng thông tin từ tài liệu tham khảo
- Nếu không có thông tin trong tài liệu, hãy nói "Hiện tại tôi chưa có thông tin này. Vui lòng liên hệ hotline 0981 33 66 28 hoặc email tuyensinh@ictu.edu.vn"
- Thêm thông tin liên hệ nếu cần thiết
- Giữ giọng văn thân thiện, tư vấn viên chuyên nghiệp

TRẢ LỜI:"""
    
    return prompt


if __name__ == '__main__':
    # Test LLM providers
    print("=== Testing LLM Providers ===")
    provider = get_llm_provider()
    
    test_prompt = "Giới thiệu ngắn gọn về Trường Đại học ICTU"
    response = provider.generate(test_prompt, max_tokens=200)
    print(f"\nPrompt: {test_prompt}")
    print(f"Response: {response}")
