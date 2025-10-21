"""
Test suite cho RAG + LLM Chatbot
"""
import os
import sys

# Add parent directory to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

def test_rag_engine():
    """Test RAG engine retrieval"""
    print("\n=== Test 1: RAG Engine ===")
    try:
        from backend.rag_engine import RAGEngine
        
        kb_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'chatbot_knowledge_new.json')
        rag = RAGEngine(kb_path)
        
        test_query = "Điểm chuẩn ngành Khoa học máy tính năm 2024"
        results = rag.retrieve(test_query, top_k=2)
        
        print(f"Query: {test_query}")
        print(f"Retrieved {len(results)} documents")
        
        for i, (doc, meta, score) in enumerate(results, 1):
            print(f"\n  [{i}] Score: {score:.3f}")
            print(f"      Type: {meta.get('type')}")
            print(f"      Content: {doc[:200]}...")
        
        assert len(results) > 0, "No documents retrieved"
        print("\n✓ RAG Engine test PASSED")
        return True
    except Exception as e:
        print(f"\n✗ RAG Engine test FAILED: {e}")
        return False


def test_llm_provider():
    """Test LLM provider"""
    print("\n=== Test 2: LLM Provider ===")
    try:
        from backend.llm_provider import get_llm_provider
        
        provider = get_llm_provider()
        print(f"Provider type: {type(provider).__name__}")
        
        test_prompt = "Hãy giới thiệu ngắn gọn về ICTU trong 2 câu."
        response = provider.generate(test_prompt, max_tokens=100)
        
        print(f"Prompt: {test_prompt}")
        print(f"Response: {response}")
        
        assert len(response) > 10, "Response too short"
        print("\n✓ LLM Provider test PASSED")
        return True
    except Exception as e:
        print(f"\n✗ LLM Provider test FAILED: {e}")
        return False


def test_chatbot_engine():
    """Test full chatbot with RAG + LLM"""
    print("\n=== Test 3: Chatbot Engine (RAG Mode) ===")
    try:
        from backend.chatbot_engine_v2 import ChatbotEngine
        
        kb_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'chatbot_knowledge_new.json')
        bot = ChatbotEngine(kb_path, use_rag=True)
        
        test_queries = [
            "Xin chào",
            "Điểm chuẩn ngành Mạng máy tính năm 2024 là bao nhiêu?",
            "Học phí của ICTU",
            "Địa chỉ trường đại học",
        ]
        
        for query in test_queries:
            print(f"\nUser: {query}")
            response = bot.get_response(query)
            print(f"Bot: {response[:200]}..." if len(response) > 200 else f"Bot: {response}")
            
            assert len(response) > 0, f"Empty response for: {query}"
        
        print("\n✓ Chatbot Engine test PASSED")
        return True
    except Exception as e:
        print(f"\n✗ Chatbot Engine test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chatbot_fallback():
    """Test chatbot fallback mode (TF-IDF)"""
    print("\n=== Test 4: Chatbot Engine (Fallback Mode) ===")
    try:
        from backend.chatbot_engine_v2 import ChatbotEngine
        
        kb_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'chatbot_knowledge_new.json')
        bot = ChatbotEngine(kb_path, use_rag=False)  # Force fallback
        
        test_query = "Xin chào"
        response = bot.get_response(test_query)
        
        print(f"User: {test_query}")
        print(f"Bot (Fallback): {response}")
        
        assert len(response) > 0, "Empty response in fallback mode"
        print("\n✓ Chatbot Fallback test PASSED")
        return True
    except Exception as e:
        print(f"\n✗ Chatbot Fallback test FAILED: {e}")
        return False


def test_api_endpoint():
    """Test /api/chat endpoint"""
    print("\n=== Test 5: API Endpoint ===")
    try:
        from backend.app import app
        
        with app.test_client() as client:
            # Test chatbot API
            response = client.post('/api/chat', json={
                'message': 'Điểm chuẩn ngành CNTT năm 2024'
            })
            
            print(f"Status: {response.status_code}")
            data = response.get_json()
            print(f"Response: {data.get('response', '')[:200]}...")
            
            assert response.status_code == 200, f"API returned {response.status_code}"
            assert 'response' in data, "No 'response' field in API result"
            
        print("\n✓ API Endpoint test PASSED")
        return True
    except Exception as e:
        print(f"\n✗ API Endpoint test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("RAG + LLM Chatbot Test Suite")
    print("="*60)
    
    results = {
        'RAG Engine': test_rag_engine(),
        'LLM Provider': test_llm_provider(),
        'Chatbot Engine (RAG)': test_chatbot_engine(),
        'Chatbot Fallback': test_chatbot_fallback(),
        'API Endpoint': test_api_endpoint(),
    }
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:30} {status}")
    
    total = len(results)
    passed_count = sum(results.values())
    
    print("="*60)
    print(f"Total: {passed_count}/{total} tests passed")
    
    if passed_count == total:
        print("\n🎉 All tests PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed_count} test(s) FAILED")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
