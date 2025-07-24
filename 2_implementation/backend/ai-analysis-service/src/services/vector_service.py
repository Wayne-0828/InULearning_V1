"""
Vector Service for RAG System

This service handles vector operations for question similarity search.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from ..models.schemas import QuestionVector
import uuid


class VectorService:
    """向量服務"""
    
    def __init__(self, milvus_host: str = "localhost", milvus_port: str = "19530"):
        self.milvus_host = milvus_host
        self.milvus_port = milvus_port
        self.collection_name = "question_embeddings"
        self.dimension = 768  # BERT 向量維度
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # 輕量級模型
        
        # 連接到 Milvus
        self._connect_to_milvus()
        
        # 確保集合存在
        self._ensure_collection_exists()
    
    def _connect_to_milvus(self):
        """連接到 Milvus"""
        try:
            connections.connect(
                alias="default",
                host=self.milvus_host,
                port=self.milvus_port
            )
            print("Successfully connected to Milvus")
        except Exception as e:
            print(f"Failed to connect to Milvus: {e}")
            raise
    
    def _ensure_collection_exists(self):
        """確保集合存在"""
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            print(f"Collection {self.collection_name} already exists")
        else:
            self._create_collection()
    
    def _create_collection(self):
        """創建集合"""
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=36, is_primary=True),
            FieldSchema(name="question_id", dtype=DataType.VARCHAR, max_length=36),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
            FieldSchema(name="metadata", dtype=DataType.JSON)
        ]
        
        schema = CollectionSchema(fields, description="Question embeddings for similarity search")
        self.collection = Collection(self.collection_name, schema)
        
        # 創建索引
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        self.collection.create_index(field_name="embedding", index_params=index_params)
        print(f"Created collection {self.collection_name} with index")
    
    def generate_embedding(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # 返回零向量作為備用
            return [0.0] * self.dimension
    
    def add_question_embedding(self, question_id: str, question_text: str, metadata: Dict[str, Any]):
        """添加題目嵌入向量"""
        try:
            # 生成嵌入向量
            embedding = self.generate_embedding(question_text)
            
            # 準備數據
            data = [
                [str(uuid.uuid4())],  # id
                [question_id],        # question_id
                [embedding],          # embedding
                [metadata]            # metadata
            ]
            
            # 插入數據
            self.collection.insert(data)
            self.collection.flush()
            
            print(f"Added embedding for question {question_id}")
            
        except Exception as e:
            print(f"Error adding question embedding: {e}")
            raise
    
    def search_similar_questions(
        self, 
        query_text: str, 
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """搜索相似題目"""
        try:
            # 生成查詢向量
            query_embedding = self.generate_embedding(query_text)
            
            # 準備搜索參數
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            # 執行搜索
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=None,  # 可以添加過濾條件
                output_fields=["question_id", "metadata"]
            )
            
            # 格式化結果
            similar_questions = []
            for hits in results:
                for hit in hits:
                    similar_questions.append({
                        "question_id": hit.entity.get("question_id"),
                        "similarity_score": hit.score,
                        "metadata": hit.entity.get("metadata", {})
                    })
            
            return similar_questions
            
        except Exception as e:
            print(f"Error searching similar questions: {e}")
            return []
    
    def update_question_embedding(self, question_id: str, question_text: str, metadata: Dict[str, Any]):
        """更新題目嵌入向量"""
        try:
            # 先刪除舊的嵌入向量
            self.delete_question_embedding(question_id)
            
            # 添加新的嵌入向量
            self.add_question_embedding(question_id, question_text, metadata)
            
            print(f"Updated embedding for question {question_id}")
            
        except Exception as e:
            print(f"Error updating question embedding: {e}")
            raise
    
    def delete_question_embedding(self, question_id: str):
        """刪除題目嵌入向量"""
        try:
            # 刪除指定 question_id 的記錄
            expr = f'question_id == "{question_id}"'
            self.collection.delete(expr)
            self.collection.flush()
            
            print(f"Deleted embedding for question {question_id}")
            
        except Exception as e:
            print(f"Error deleting question embedding: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """獲取集合統計信息"""
        try:
            stats = {
                "collection_name": self.collection_name,
                "num_entities": self.collection.num_entities,
                "schema": str(self.collection.schema)
            }
            return stats
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {}
    
    def batch_add_embeddings(self, questions: List[Dict[str, Any]]):
        """批量添加嵌入向量"""
        try:
            ids = []
            question_ids = []
            embeddings = []
            metadatas = []
            
            for question in questions:
                question_id = question["question_id"]
                question_text = question["text"]
                metadata = question.get("metadata", {})
                
                embedding = self.generate_embedding(question_text)
                
                ids.append(str(uuid.uuid4()))
                question_ids.append(question_id)
                embeddings.append(embedding)
                metadatas.append(metadata)
            
            # 批量插入
            data = [ids, question_ids, embeddings, metadatas]
            self.collection.insert(data)
            self.collection.flush()
            
            print(f"Batch added {len(questions)} embeddings")
            
        except Exception as e:
            print(f"Error batch adding embeddings: {e}")
            raise
    
    def close_connection(self):
        """關閉連接"""
        try:
            connections.disconnect("default")
            print("Disconnected from Milvus")
        except Exception as e:
            print(f"Error disconnecting from Milvus: {e}") 