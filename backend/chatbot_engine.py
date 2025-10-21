import os
import re
import json
import logging
import numpy as np

# --- Thư viện xử lý ngôn ngữ ---
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'nltk'])
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords

# --- Thư viện học máy ---
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'scikit-learn'])
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

# --- Thư viện toán học ---
try:
    import numpy as np
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'numpy'])
    import numpy as np


class ChatbotEngine:
    def __init__(self, knowledge_base_path):
        """
        Khởi tạo chatbot engine với cơ sở tri thức JSON
        """

        # 🧠 Đảm bảo các gói dữ liệu NLTK được tải đầy đủ
        for resource in ['punkt', 'stopwords', 'punkt_tab']:
            try:
                nltk.download(resource, quiet=True)
            except Exception as e:
                logging.warning(f"Không thể tải {resource}: {e}")

        # Thêm đường dẫn dự phòng nếu Render reset dữ liệu
        nltk.data.path.append(os.path.join(os.getcwd(), "nltk_data"))

        # ✅ Gộp stopwords Anh + Việt
        self.stop_words = set(stopwords.words('english'))
        vn_stop_words = {
            'và', 'của', 'cho', 'trong', 'với', 'các', 'được', 'để', 'có',
            'những', 'một', 'là', 'này', 'từ', 'khi', 'đến', 'như', 'không',
            'về', 'tại', 'theo', 'đã', 'sẽ', 'vì', 'nhưng', 'còn', 'bị',
            'do', 'phải', 'nếu', 'nên', 'được', 'đang', 'sau', 'rồi', 'thì'
        }
        self.stop_words.update(vn_stop_words)

        # 🔹 Tải cơ sở tri thức
        self.knowledge_base = self.load_knowledge_base(knowledge_base_path)

        # 🔹 Khởi tạo vectorizer
        self.vectorizer = TfidfVectorizer(
            tokenizer=self.tokenize_text,
            stop_words=list(self.stop_words),
            lowercase=True,
            max_features=5000
        )
        self.response_vectors = None
        self.responses = []
        self.train_vectorizer()

    # ----------------------------------------------------------
    # Load dữ liệu
    # ----------------------------------------------------------
    def load_knowledge_base(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            logging.error(f"Lỗi khi tải knowledge base: {e}")
            return {"intents": []}

    # ----------------------------------------------------------
    # Xử lý ngôn ngữ
    # ----------------------------------------------------------
    def tokenize_text(self, text):
        # Loại bỏ ký tự đặc biệt, số và giữ lại tiếng Việt
        text = re.sub(r'[^a-zA-ZÀ-ỹ\s]', ' ', text)
        tokens = word_tokenize(text.lower())
        tokens = [
            token for token in tokens
            if token not in self.stop_words and len(token) > 1
        ]
        return tokens

    def preprocess_text(self, text):
        return ' '.join(self.tokenize_text(text))

    # ----------------------------------------------------------
    # Huấn luyện TF-IDF
    # ----------------------------------------------------------
    def train_vectorizer(self):
        corpus = []
        self.responses = []

        for intent in self.knowledge_base.get('intents', []):
            for pattern in intent.get('patterns', []):
                processed_pattern = self.preprocess_text(pattern)
                corpus.append(processed_pattern)
                self.responses.append(intent.get('responses', []))

        if corpus:
            self.response_vectors = self.vectorizer.fit_transform(corpus)
            logging.info("✅ Huấn luyện vectorizer thành công.")
        else:
            logging.warning("⚠️ Không tìm thấy pattern trong knowledge base!")

    # ----------------------------------------------------------
    # Trả lời người dùng
    # ----------------------------------------------------------
    def get_response(self, user_input, context=None):
        try:
            processed_input = self.preprocess_text(user_input)
            input_vector = self.vectorizer.transform([processed_input])
            similarities = cosine_similarity(input_vector, self.response_vectors)

            max_idx = np.argmax(similarities[0])
            max_score = similarities[0][max_idx]

            if max_score < 0.3:
                return self.get_default_response()

            response_options = self.responses[max_idx]
            return np.random.choice(response_options)

        except Exception as e:
            logging.error(f"Lỗi khi sinh phản hồi: {e}")
            return self.get_default_response()

    # ----------------------------------------------------------
    # Câu trả lời mặc định
    # ----------------------------------------------------------
    def get_default_response(self):
        return np.random.choice([
            "Xin lỗi, tôi chưa hiểu câu hỏi của bạn. Bạn có thể nói rõ hơn không?",
            "Tôi chưa rõ ý bạn lắm. Bạn có thể giải thích lại được không?",
            "Bạn có thể nói cụ thể hơn để tôi hỗ trợ tốt hơn không?"
        ])

    # ----------------------------------------------------------
    # Cập nhật tri thức
    # ----------------------------------------------------------
    def update_knowledge_base(self, new_intent):
        try:
            self.knowledge_base.setdefault('intents', []).append(new_intent)
            self.train_vectorizer()
            logging.info("✅ Đã cập nhật knowledge base.")
            return True
        except Exception as e:
            logging.error(f"Lỗi khi cập nhật knowledge base: {e}")
            return False

    # ----------------------------------------------------------
    # Các chức năng mở rộng
    # ----------------------------------------------------------
    def save_interaction(self, user_input, bot_response, feedback=None):
        # TODO: Ghi lịch sử hội thoại vào DB hoặc file log
        pass

    def get_program_recommendations(self, user_preferences):
        # TODO: Gợi ý chương trình học dựa theo sở thích
        pass
