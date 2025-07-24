import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from src.services.vector_service import VectorService
from src.models.schemas import QuestionVector

class TestVectorService:
    @pytest.fixture
    def mock_milvus_connection(self):
        with patch('src.services.vector_service.connections') as mock_connections:
            with patch('src.services.vector_service.Collection') as mock_collection:
                with patch('src.services.vector_service.utility') as mock_utility:
                    mock_connections.connect.return_value = None
                    mock_utility.has_collection.return_value = True
                    mock_collection.return_value = Mock()
                    yield mock_collection

    @pytest.fixture
    def service(self, mock_milvus_connection):
        with patch('src.services.vector_service.SentenceTransformer'):
            service = VectorService("localhost", "19530")
            service.collection = mock_milvus_connection.return_value
            return service

    def test_generate_embedding(self, service):
        """測試生成向量嵌入"""
        test_text = "解一元一次方程式 2x + 3 = 7"
        
        with patch.object(service.model, 'encode') as mock_encode:
            mock_encode.return_value = np.array([0.1, 0.2, 0.3] * 256)  # 768維向量
            
            embedding = service.generate_embedding(test_text)
            
            assert len(embedding) == 768
            assert isinstance(embedding, list)
            assert all(isinstance(x, float) for x in embedding)

    def test_add_question_embedding(self, service):
        """測試添加題目向量嵌入"""
        question_id = "q001"
        question_text = "解一元一次方程式 2x + 3 = 7"
        metadata = {
            "subject": "mathematics",
            "grade": "grade_7",
            "knowledge_points": ["algebra", "equations"],
            "difficulty": "medium"
        }
        
        with patch.object(service, 'generate_embedding') as mock_generate:
            mock_generate.return_value = [0.1] * 768
            
            service.collection.insert.return_value = Mock()
            
            result = service.add_question_embedding(question_id, question_text, metadata)
            
            assert result is True
            service.collection.insert.assert_called_once()

    def test_search_similar_questions(self, service):
        """測試搜尋相似題目"""
        query_text = "解方程式"
        top_k = 5
        metadata_filter = {"subject": "mathematics"}
        
        with patch.object(service, 'generate_embedding') as mock_generate:
            mock_generate.return_value = [0.1] * 768
            
            # 模擬搜尋結果
            mock_results = [
                {
                    "question_id": "q001",
                    "question_text": "解一元一次方程式 2x + 3 = 7",
                    "metadata": {"subject": "mathematics"},
                    "similarity_score": 0.95
                }
            ]
            
            service.collection.search.return_value = [mock_results]
            
            results = service.search_similar_questions(query_text, top_k, metadata_filter)
            
            assert len(results) == 1
            assert results[0]["question_id"] == "q001"
            assert results[0]["similarity_score"] == 0.95

    def test_update_question_embedding(self, service):
        """測試更新題目向量嵌入"""
        question_id = "q001"
        question_text = "更新後的題目內容"
        metadata = {"subject": "mathematics"}
        
        with patch.object(service, 'generate_embedding') as mock_generate:
            mock_generate.return_value = [0.2] * 768
            
            service.collection.delete.return_value = Mock()
            service.collection.insert.return_value = Mock()
            
            result = service.update_question_embedding(question_id, question_text, metadata)
            
            assert result is True
            service.collection.delete.assert_called_once()
            service.collection.insert.assert_called_once()

    def test_delete_question_embedding(self, service):
        """測試刪除題目向量嵌入"""
        question_id = "q001"
        
        service.collection.delete.return_value = Mock()
        
        result = service.delete_question_embedding(question_id)
        
        assert result is True
        service.collection.delete.assert_called_once()

    def test_batch_add_embeddings(self, service):
        """測試批量添加向量嵌入"""
        questions = [
            {
                "question_id": "q001",
                "question_text": "題目1",
                "metadata": {"subject": "mathematics"}
            },
            {
                "question_id": "q002", 
                "question_text": "題目2",
                "metadata": {"subject": "mathematics"}
            }
        ]
        
        with patch.object(service, 'generate_embedding') as mock_generate:
            mock_generate.return_value = [0.1] * 768
            
            service.collection.insert.return_value = Mock()
            
            result = service.batch_add_embeddings(questions)
            
            assert result is True
            service.collection.insert.assert_called_once()

    def test_get_collection_stats(self, service):
        """測試獲取集合統計資訊"""
        service.collection.num_entities = 100
        
        stats = service.get_collection_stats()
        
        assert "total_entities" in stats
        assert stats["total_entities"] == 100 