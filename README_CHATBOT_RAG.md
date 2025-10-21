# Hướng dẫn Chatbot RAG + LLM cho ICTU Admission System

## Tổng quan

Hệ thống chatbot hỗ trợ **2 chế độ**:

1. **RAG + LLM Mode** (Khuyến nghị): Sử dụng Retrieval-Augmented Generation với LLM (OpenAI GPT hoặc Google Gemini) để trả lời tự nhiên, chính xác dựa trên knowledge base.
2. **TF-IDF Fallback Mode**: Sử dụng TF-IDF similarity matching (chatbot đơn giản, không cần API key).

## Cài đặt Dependencies

### 1. Cài đặt thư viện cơ bản

```bash
pip install -r requirements.txt
```

### 2. Cài đặt thư viện RAG (nếu muốn dùng RAG mode)

```bash
pip install sentence-transformers faiss-cpu openai google-generativeai
```

**Lưu ý**: 
- `sentence-transformers`: Tạo embeddings cho tiếng Việt
- `faiss-cpu`: Vector search engine
- `openai`: OpenAI API client (nếu dùng GPT)
- `google-generativeai`: Google Gemini API client (nếu dùng Gemini)

## Cấu hình

### 1. Tạo file `.env`

Tạo file `.env` trong thư mục gốc:

```bash
# Cấu hình LLM Provider
LLM_PROVIDER=openai  # Hoặc 'gemini', 'auto'
USE_RAG_CHATBOT=true  # true = RAG mode, false = TF-IDF mode

# OpenAI API Key (nếu dùng OpenAI)
OPENAI_API_KEY=sk-...your-key-here...

# Google Gemini API Key (nếu dùng Gemini)
GOOGLE_API_KEY=...your-key-here...

# Cấu hình khác (mail, database, etc.)
SECRET_KEY=...
MAIL_SERVER=...
```

### 2. Lấy API Keys

#### OpenAI (GPT-3.5/GPT-4)
1. Truy cập https://platform.openai.com/
2. Đăng ký/đăng nhập
3. Vào **API Keys** → **Create new secret key**
4. Copy key và dán vào `.env`

**Chi phí**: 
- GPT-3.5-turbo: ~$0.002/1K tokens (rẻ, phù hợp production)
- GPT-4: ~$0.03/1K tokens (đắt hơn nhưng thông minh hơn)

#### Google Gemini (Miễn phí tier available)
1. Truy cập https://makersuite.google.com/app/apikey
2. Đăng nhập Google account
3. Click **Get API key** → **Create API key**
4. Copy key và dán vào `.env`

**Chi phí**: 
- Gemini 1.5 Flash: **MIỄN PHÍ** (60 requests/minute)
- Gemini 1.5 Pro: Có free tier hạn chế

**Khuyến nghị**: Dùng **Gemini** cho development/testing (free), dùng **OpenAI GPT-3.5** cho production.

## Sử dụng

### 1. Khởi động server

```bash
cd admission_system
python backend/app.py
```

Hoặc với gunicorn (production):

```bash
gunicorn backend.app:app
```

### 2. Test chatbot qua API

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Điểm chuẩn ngành Khoa học máy tính năm 2024 là bao nhiêu?"}'
```

### 3. Test trực tiếp từ code

```python
from backend.chatbot_engine_v2 import ChatbotEngine

bot = ChatbotEngine('data/chatbot_knowledge_new.json', use_rag=True)
response = bot.get_response("Học phí của ICTU")
print(response)
```

## Quản lý Knowledge Base

### Cập nhật dữ liệu

1. Chỉnh sửa file `data/chatbot_knowledge_new.json`
2. Rebuild index:

```python
from backend.chatbot_engine_v2 import ChatbotEngine

bot = ChatbotEngine('data/chatbot_knowledge_new.json', use_rag=True)
bot.rebuild_index()
```

### Cấu trúc knowledge base

```json
{
  "truong_dai_hoc": {
    "thong_tin_chung": { ... },
    "tuyen_sinh_qua_cac_nam": {
      "2024": {
        "danh_sach_nganh": [ ... ]
      }
    }
  },
  "intents": [ ... ]
}
```

## Troubleshooting

### Lỗi: "sentence-transformers not installed"
```bash
pip install sentence-transformers faiss-cpu
```

### Lỗi: "OpenAI API key not found"
- Kiểm tra file `.env` có `OPENAI_API_KEY=...`
- Restart server sau khi thêm key

### Chatbot trả lời không chính xác
1. Kiểm tra knowledge base có đầy đủ thông tin không
2. Rebuild index: `bot.rebuild_index()`
3. Tăng `top_k` trong `rag_engine.retrieve(query, top_k=5)`

### Chatbot chạy chậm
- Lần đầu tiên sẽ chậm (download model embeddings ~400MB)
- Sau đó sẽ dùng cache, nhanh hơn
- Dùng GPU nếu có: `pip install sentence-transformers[gpu]`

## Architecture

```
User Query
    ↓
RAG Engine (retrieve top-k relevant docs)
    ↓
Create Prompt (query + retrieved docs)
    ↓
LLM Provider (OpenAI/Gemini)
    ↓
Response
```

## Files quan trọng

- `backend/rag_engine.py`: RAG engine với FAISS vector search
- `backend/llm_provider.py`: LLM wrappers (OpenAI, Gemini, Fallback)
- `backend/chatbot_engine_v2.py`: Main chatbot logic
- `data/chatbot_knowledge_new.json`: Knowledge base mới (đầy đủ)
- `data/.rag_cache/`: Cache cho embeddings và FAISS index

## Performance

- **Latency**: 1-3 giây (bao gồm retrieve + LLM generation)
- **Accuracy**: Phụ thuộc vào quality của knowledge base và LLM
- **Cost**: 
  - Gemini Flash: **FREE**
  - GPT-3.5-turbo: ~$0.001 per response
  - GPT-4: ~$0.02 per response

## Liên hệ

- Email: tuyensinh@ictu.edu.vn
- Hotline: 0981 33 66 28 / 0981 33 66 29
