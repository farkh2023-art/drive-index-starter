import pytest
from unittest.mock import MagicMock, patch
import analyze_drive as ad


class TestResumeTexteIa:
    def test_no_key_returns_empty(self, monkeypatch):
        monkeypatch.setattr(ad, "OPENAI_KEY", "")
        result = ad.resume_texte_ia("Texte quelconque.")
        assert result == ""

    def test_success(self, monkeypatch):
        monkeypatch.setattr(ad, "OPENAI_KEY", "sk-fake")
        mock_message = MagicMock()
        mock_message.content = "Resume du document."
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion

        with patch("analyze_drive.openai.OpenAI", return_value=mock_client):
            result = ad.resume_texte_ia("Texte long du document.")

        assert result == "Resume du document."
        mock_client.chat.completions.create.assert_called_once()

    def test_truncates_input_to_5000_chars(self, monkeypatch):
        monkeypatch.setattr(ad, "OPENAI_KEY", "sk-fake")
        mock_message = MagicMock()
        mock_message.content = "Resume."
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion

        long_text = "a" * 10000
        with patch("analyze_drive.openai.OpenAI", return_value=mock_client):
            ad.resume_texte_ia(long_text)

        call_args = mock_client.chat.completions.create.call_args
        user_content = call_args.kwargs["messages"][1]["content"]
        assert len(user_content) == 5000

    def test_api_error_returns_message(self, monkeypatch):
        monkeypatch.setattr(ad, "OPENAI_KEY", "sk-fake")
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("quota depasse")

        with patch("analyze_drive.openai.OpenAI", return_value=mock_client):
            result = ad.resume_texte_ia("Texte.")

        assert result.startswith("[Erreur IA]")
