"""AI service implementations for text summarization."""

from typing import Optional
from .exceptions import AIServiceError


class AIModel:
    """Base class for AI models."""

    def summarize(self, text: str, prompt: str = "") -> str:
        """Summarize text using AI.

        Args:
            text: Text to summarize
            prompt: Optional prompt to guide summarization

        Returns:
            Summarized text

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement summarize()")


class OpenAIModel(AIModel):
    """OpenAI-based text summarization model."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", 
                 max_tokens: int = 220, temperature: float = 0.5):
        """Initialize OpenAI model.

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-3.5-turbo)
            max_tokens: Maximum tokens in response (default: 220)
            temperature: Sampling temperature (default: 0.5)
        """
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client = None

    @property
    def client(self):
        """Lazy-loaded OpenAI client."""
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise AIServiceError("OpenAI package not installed. Install it with: pip install openai")
        return self._client

    def summarize(self, text: str, prompt: str = "Resume ce document en 4 lignes :") -> str:
        """Summarize text using OpenAI.

        Args:
            text: Text to summarize
            prompt: Optional prompt to guide summarization

        Returns:
            Summarized text

        Raises:
            AIServiceError: If summarization fails
        """
        if not self.api_key:
            raise AIServiceError("OpenAI API key not provided")

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text[:5000]}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            raise AIServiceError(f"Failed to summarize text with OpenAI: {e}")


class MockAIModel(AIModel):
    """Mock AI model for testing purposes."""

    def __init__(self, response: str = "[Mock] This is a test summary"):
        """Initialize mock model.

        Args:
            response: Fixed response to return for all summarizations
        """
        self.response = response

    def summarize(self, text: str, prompt: str = "") -> str:
        """Return mock summary.

        Args:
            text: Text to summarize (ignored)
            prompt: Optional prompt (ignored)

        Returns:
            Mock summary text
        """
        return self.response


class AIModelFactory:
    """Factory for creating AI models."""

    @staticmethod
    def create_model(model_type: str = "openai", **kwargs) -> AIModel:
        """Create an AI model instance.

        Args:
            model_type: Type of model to create ('openai' or 'mock')
            **kwargs: Additional arguments for model initialization

        Returns:
            AI model instance

        Raises:
            AIServiceError: If model type is unknown
        """
        if model_type == "openai":
            return OpenAIModel(**kwargs)
        elif model_type == "mock":
            return MockAIModel(**kwargs)
        else:
            raise AIServiceError(f"Unknown model type: {model_type}")
