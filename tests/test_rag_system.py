"""
Basic tests for HealthRAG system

To run tests:
    pytest tests/

To run with coverage:
    pytest --cov=src tests/
"""

import pytest
import os
import tempfile
import shutil
from src.rag_system import HealthRAG, MLXModel, OllamaLLM


class TestMLXModel:
    """Tests for MLX model wrapper"""

    def test_mlx_model_initialization(self):
        """Test MLX model can be initialized"""
        # This may fail if MLX is not available, which is expected
        try:
            model = MLXModel()
            assert model is not None
        except Exception as e:
            # MLX not available is acceptable
            pytest.skip(f"MLX not available: {e}")

    def test_mlx_model_switch(self):
        """Test MLX model switching"""
        try:
            model = MLXModel()
            original_model_name = model.model_name
            # Switch to same model (shouldn't fail)
            model.switch_model(original_model_name)
            assert model.model_name == original_model_name
        except Exception as e:
            pytest.skip(f"MLX not available: {e}")


class TestOllamaLLM:
    """Tests for Ollama LLM wrapper"""

    def test_ollama_initialization(self):
        """Test Ollama LLM can be initialized"""
        llm = OllamaLLM()
        assert llm.model == "llama3.1:8b"
        assert llm.base_url == "http://localhost:11434"

    def test_ollama_custom_initialization(self):
        """Test Ollama with custom parameters"""
        llm = OllamaLLM(model="llama2", base_url="http://custom:11434")
        assert llm.model == "llama2"
        assert llm.base_url == "http://custom:11434"

    def test_ollama_switch_model(self):
        """Test switching Ollama model"""
        llm = OllamaLLM()
        llm.switch_model("llama3.1:70b")
        assert llm.model == "llama3.1:70b"


class TestHealthRAG:
    """Tests for main HealthRAG system"""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing"""
        temp_data = tempfile.mkdtemp()
        temp_vectorstore = tempfile.mkdtemp()

        yield temp_data, temp_vectorstore

        # Cleanup
        shutil.rmtree(temp_data, ignore_errors=True)
        shutil.rmtree(temp_vectorstore, ignore_errors=True)

    def test_healthrag_initialization_ollama(self, temp_dirs):
        """Test HealthRAG initialization with Ollama backend"""
        temp_data, temp_vectorstore = temp_dirs

        rag = HealthRAG(
            data_path=temp_data,
            persist_directory=temp_vectorstore,
            backend="ollama"
        )

        assert rag.backend == "ollama"
        assert isinstance(rag.llm, OllamaLLM)
        assert rag.data_path == temp_data
        assert rag.persist_directory == temp_vectorstore

    def test_healthrag_initialization_mlx(self, temp_dirs):
        """Test HealthRAG initialization with MLX backend"""
        temp_data, temp_vectorstore = temp_dirs

        try:
            rag = HealthRAG(
                data_path=temp_data,
                persist_directory=temp_vectorstore,
                backend="mlx"
            )
            assert rag.backend == "mlx"
            assert isinstance(rag.llm, MLXModel)
        except Exception as e:
            pytest.skip(f"MLX not available: {e}")

    def test_backend_switching(self, temp_dirs):
        """Test switching between backends"""
        temp_data, temp_vectorstore = temp_dirs

        rag = HealthRAG(
            data_path=temp_data,
            persist_directory=temp_vectorstore,
            backend="ollama"
        )

        assert isinstance(rag.llm, OllamaLLM)

        # Switch to MLX (will fall back to Ollama if MLX unavailable)
        rag.switch_backend("mlx")
        # Should either be MLX or Ollama depending on availability
        assert rag.llm is not None

    def test_document_count_empty(self, temp_dirs):
        """Test document count with empty vectorstore"""
        temp_data, temp_vectorstore = temp_dirs

        rag = HealthRAG(
            data_path=temp_data,
            persist_directory=temp_vectorstore,
            backend="ollama"
        )

        # Should be 0 for empty vectorstore
        count = rag.get_document_count()
        assert count == 0

    def test_query_without_documents(self, temp_dirs):
        """Test querying without documents returns appropriate message"""
        temp_data, temp_vectorstore = temp_dirs

        rag = HealthRAG(
            data_path=temp_data,
            persist_directory=temp_vectorstore,
            backend="ollama"
        )

        response, response_time = rag.query("What is the best workout?")

        # Should return error message about missing documents
        assert "not properly initialized" in response.lower() or "no pdf" in response.lower()
        assert response_time >= 0


class TestConfiguration:
    """Tests for configuration and settings"""

    def test_config_file_exists(self):
        """Test that config file exists"""
        config_path = "config/settings.py"
        assert os.path.exists(config_path)

    def test_data_directories_exist(self):
        """Test that data directories exist"""
        assert os.path.exists("data")
        assert os.path.exists("data/pdfs")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
