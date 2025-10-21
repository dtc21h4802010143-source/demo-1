# GIẢI PHÁP LLM MIỄN PHÍ CHO RAG

## ✅ CÁC DỊCH VỤ KHUYẾN NGHỊ (Theo thứ tự ưu tiên)

### 1. ⭐ GROQ - KHUYẾN NGHỊ MẠNH (Tốt nhất cho RAG)
**Ưu điểm:**
- ✅ Hoàn toàn miễn phí, không cần credit card
- ✅ Tốc độ inference NHANH NHẤT (300-800 tokens/giây)
- ✅ Model mạnh: llama-3.3-70b-versatile (70B parameters)
- ✅ Giới hạn cao: 30 request/phút (free tier)
- ✅ Không yêu cầu xác minh điện thoại

**Cách đăng ký:**
1. Truy cập: https://console.groq.com
2. Đăng ký tài khoản (dùng email hoặc Google)
3. Vào "API Keys": https://console.groq.com/keys
4. Tạo API key mới
5. Copy key và dán vào `.env`:
   ```
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
   ```

**Test:**
```bash
python test_groq_free.py
```

---

### 2. Together AI - Tốt cho thử nghiệm
**Ưu điểm:**
- ✅ Miễn phí $25 credit khi đăng ký
- ✅ Nhiều model lựa chọn (Llama, Mixtral, Qwen, etc.)
- ✅ Hỗ trợ fine-tuning
- ⚠️ Cần xác minh email

**Cách đăng ký:**
1. Truy cập: https://api.together.xyz/signup
2. Đăng ký và xác minh email
3. Nhận $25 credit miễn phí
4. Tạo API key tại: https://api.together.xyz/settings/api-keys
5. Copy key và dán vào `.env`:
   ```
   TOGETHER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
   ```

---

### 3. OpenRouter - Nhiều lựa chọn
**Ưu điểm:**
- ✅ Nhiều model miễn phí (tag :free)
- ✅ Dễ dàng chuyển đổi giữa các model
- ✅ Hỗ trợ nhiều provider (OpenAI, Anthropic, Google, Meta, etc.)
- ⚠️ Model miễn phí thường chất lượng thấp hơn

**Cách đăng ký:**
1. Truy cập: https://openrouter.ai
2. Đăng ký tài khoản
3. Tạo API key tại: https://openrouter.ai/keys
4. Copy key và dán vào `.env`:
   ```
   OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
   ```

---

### 4. Ollama - Local LLM (Không cần API)
**Ưu điểm:**
- ✅ 100% miễn phí, không giới hạn
- ✅ Chạy offline, không cần internet
- ✅ Riêng tư, dữ liệu không bị gửi ra ngoài
- ⚠️ Cần RAM đủ lớn (8GB+ cho model 3B, 16GB+ cho 7B)
- ⚠️ Chậm hơn Groq (nhưng vẫn chấp nhận được)

**Cách cài đặt:**
1. Tải Ollama: https://ollama.com/download
2. Cài đặt và khởi động
3. Tải model:
   ```bash
   ollama pull qwen2.5:3b-instruct
   ```
4. Đã sẵn sàng sử dụng (không cần API key)

---

## 🎯 KHUYẾN NGHỊ CUỐI CÙNG

**Cho môi trường production/demo:**
1. **Groq** (Tốt nhất) - Nhanh, mạnh, miễn phí
2. **Together AI** (Backup) - $25 credit miễn phí
3. **Ollama** (Local fallback) - Khi không có internet

**Cho môi trường development:**
- **Ollama** - Không giới hạn, chạy offline

---

## 📊 SO SÁNH

| Dịch vụ | Tốc độ | Chất lượng | Giá | Giới hạn | Setup |
|---------|--------|------------|-----|----------|-------|
| **Groq** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Miễn phí | 30 req/phút | Rất dễ |
| **Together** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $25 credit | Theo credit | Dễ |
| **OpenRouter** | ⭐⭐⭐ | ⭐⭐⭐ | Miễn phí* | Varies | Dễ |
| **Ollama** | ⭐⭐⭐ | ⭐⭐⭐⭐ | Miễn phí | Không giới hạn | Trung bình |

---

## 🚀 HÀNH ĐỘNG TIẾP THEO

1. **Đăng ký Groq** (5 phút): https://console.groq.com/keys
2. **Thêm API key vào `.env`**:
   ```
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
   ```
3. **Test ngay**:
   ```bash
   python test_free_llm_services.py
   ```
4. **Chạy chatbot**:
   ```bash
   python backend/app.py
   ```

---

## ⚡ TẠI SAO CHỌN GROQ?

- **Nhanh nhất**: 300-800 tokens/giây (so với OpenAI ~40-100 tokens/s)
- **Miễn phí thực sự**: Không cần credit card, không giới hạn theo thời gian
- **Model mạnh**: Llama 3.3 70B (so sánh được GPT-3.5)
- **Stable**: Được tối ưu cho inference, ít downtime
- **Phù hợp RAG**: Context window lớn (8K-128K), low latency

**→ GROQ là lựa chọn TỐT NHẤT cho chatbot RAG tuyển sinh!**
