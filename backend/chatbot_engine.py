import json
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

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'scikit-learn'])
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

try:
    import numpy as np
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'numpy'])
    import numpy as np

import os
import logging
import re

class ChatbotEngine:
    def __init__(self, knowledge_base_path):
        # Initialize NLTK components
        nltk.download('punkt')
        nltk.download('stopwords')
        
        # Use both English and Vietnamese stopwords
        self.stop_words = set(stopwords.words('english'))
        # Add Vietnamese stop words
        vn_stop_words = {'và', 'của', 'cho', 'trong', 'với', 'các', 'được', 'để', 'có',
                        'những', 'một', 'là', 'này', 'từ', 'khi', 'đến', 'như', 'không',
                        'về', 'tại', 'theo', 'đã', 'sẽ', 'vì', 'nhưng', 'còn', 'bị', 
                        'do', 'phải', 'nếu', 'nên', 'được', 'đang', 'sau', 'rồi', 'thì'}
        self.stop_words.update(vn_stop_words)
        
        # Load knowledge base
        self.knowledge_base = self.load_knowledge_base(knowledge_base_path)
        
        # Initialize TF-IDF vectorizer with Vietnamese support
        self.vectorizer = TfidfVectorizer(
            tokenizer=self.tokenize_text,
            stop_words=list(self.stop_words),
            lowercase=True,
            max_features=5000
        )
        self.response_vectors = None
        self.train_vectorizer()

    def load_knowledge_base(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            logging.error(f"Error loading knowledge base: {e}")
            return {"intents": []}

    def tokenize_text(self, text):
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-ZÀ-ỹ\s]', ' ', text)
        # Tokenize
        tokens = word_tokenize(text.lower())
        # Remove stop words and single characters
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 1]
        return tokens

    def preprocess_text(self, text):
        tokens = self.tokenize_text(text)
        return ' '.join(tokens)

    def train_vectorizer(self):
        # Prepare corpus from knowledge base
        corpus = []
        self.responses = []
        
        for intent in self.knowledge_base['intents']:
            for pattern in intent['patterns']:
                processed_pattern = self.preprocess_text(pattern)
                corpus.append(processed_pattern)
                self.responses.append(intent['responses'])

        # Fit vectorizer and transform corpus
        if corpus:
            self.response_vectors = self.vectorizer.fit_transform(corpus)
        else:
            logging.warning("No patterns found in knowledge base")

    def get_response(self, user_input, context=None):
        try:
            # Preprocess user input
            processed_input = self.preprocess_text(user_input)
            
            # Transform user input
            input_vector = self.vectorizer.transform([processed_input])
            
            # Calculate similarities
            similarities = cosine_similarity(input_vector, self.response_vectors)
            
            # Get most similar response
            max_similarity_idx = np.argmax(similarities[0])
            
            # Check if similarity is too low
            if similarities[0][max_similarity_idx] < 0.3:
                return self.get_default_response()
            
            # Get response options for the best match
            response_options = self.responses[max_similarity_idx]
            
            # Randomly select one response
            return np.random.choice(response_options)
            
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return self.get_default_response()

    def get_default_response(self):
        default_responses = [
            "Xin lỗi, tôi không hiểu câu hỏi của bạn. Bạn có thể diễn đạt lại được không?",
            "Tôi chưa rõ ý bạn lắm. Bạn có thể giải thích rõ hơn được không?",
            "Xin bạn hãy cho tôi thêm thông tin về vấn đề này."
        ]
        return np.random.choice(default_responses)

    def update_knowledge_base(self, new_intent):
        try:
            self.knowledge_base['intents'].append(new_intent)
            self.train_vectorizer()
            return True
        except Exception as e:
            logging.error(f"Error updating knowledge base: {e}")
            return False

    def save_interaction(self, user_input, bot_response, feedback=None):
        # Implementation for saving chat interactions to database
        pass

    def get_program_recommendations(self, user_preferences):
        # Implementation for program recommendations based on user preferences
        pass