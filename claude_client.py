"""
Claude AI integration client for AsciiDoc Artisan.
Provides methods to interact with the Node.js Claude service.
"""

import json
import logging
from typing import Dict, Optional, Tuple
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError


logger = logging.getLogger(__name__)


class ClaudeClient:
    """Client for interacting with the Claude AI service."""

    def __init__(self, base_url: str = "http://localhost:3000"):
        """
        Initialize the Claude client.

        Args:
            base_url: Base URL of the Claude service
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.timeout = 30  # seconds

    def is_available(self) -> bool:
        """
        Check if the Claude service is available.

        Returns:
            True if service is available, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            data = response.json()
            return data.get('status') == 'ok' and data.get('claudeReady', False)
        except Exception as e:
            logger.debug(f"Claude service not available: {e}")
            return False

    def generate_asciidoc(self, prompt: str, context: Optional[str] = None) -> Tuple[bool, str, str]:
        """
        Generate AsciiDoc content based on a prompt.

        Args:
            prompt: The generation prompt
            context: Optional context information

        Returns:
            Tuple of (success, content/error_message, error_type)
        """
        try:
            payload = {"prompt": prompt}
            if context:
                payload["context"] = context

            response = self.session.post(
                f"{self.base_url}/api/generate-asciidoc",
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return True, data.get('content', ''), ''
            else:
                error_data = response.json()
                return False, error_data.get('error', 'Unknown error'), 'API_ERROR'

        except Timeout:
            return False, 'Request timed out. Please try again.', 'TIMEOUT'
        except ConnectionError:
            return False, 'Cannot connect to Claude service. Make sure it is running.', 'CONNECTION'
        except Exception as e:
            logger.exception("Error generating AsciiDoc")
            return False, str(e), 'UNKNOWN'

    def improve_asciidoc(self, content: str, instruction: str) -> Tuple[bool, str, str]:
        """
        Improve existing AsciiDoc content.

        Args:
            content: The AsciiDoc content to improve
            instruction: Improvement instruction

        Returns:
            Tuple of (success, improved_content/error_message, error_type)
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/improve-asciidoc",
                json={
                    "content": content,
                    "instruction": instruction
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return True, data.get('content', ''), ''
            else:
                error_data = response.json()
                return False, error_data.get('error', 'Unknown error'), 'API_ERROR'

        except Timeout:
            return False, 'Request timed out. Please try again.', 'TIMEOUT'
        except ConnectionError:
            return False, 'Cannot connect to Claude service. Make sure it is running.', 'CONNECTION'
        except Exception as e:
            logger.exception("Error improving AsciiDoc")
            return False, str(e), 'UNKNOWN'

    def convert_format(self, content: str, from_format: str, to_format: str) -> Tuple[bool, str, str]:
        """
        Convert content between formats.

        Args:
            content: The content to convert
            from_format: Source format (e.g., 'markdown', 'html')
            to_format: Target format (e.g., 'asciidoc')

        Returns:
            Tuple of (success, converted_content/error_message, error_type)
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/convert-format",
                json={
                    "content": content,
                    "fromFormat": from_format,
                    "toFormat": to_format
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return True, data.get('content', ''), ''
            else:
                error_data = response.json()
                return False, error_data.get('error', 'Unknown error'), 'API_ERROR'

        except Timeout:
            return False, 'Request timed out. Please try again.', 'TIMEOUT'
        except ConnectionError:
            return False, 'Cannot connect to Claude service. Make sure it is running.', 'CONNECTION'
        except Exception as e:
            logger.exception("Error converting format")
            return False, str(e), 'UNKNOWN'

    def generate_outline(self, topic: str, style: Optional[str] = None) -> Tuple[bool, str, str]:
        """
        Generate a documentation outline.

        Args:
            topic: The topic to create an outline for
            style: Optional style preference

        Returns:
            Tuple of (success, outline/error_message, error_type)
        """
        try:
            payload = {"topic": topic}
            if style:
                payload["style"] = style

            response = self.session.post(
                f"{self.base_url}/api/generate-outline",
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return True, data.get('content', ''), ''
            else:
                error_data = response.json()
                return False, error_data.get('error', 'Unknown error'), 'API_ERROR'

        except Timeout:
            return False, 'Request timed out. Please try again.', 'TIMEOUT'
        except ConnectionError:
            return False, 'Cannot connect to Claude service. Make sure it is running.', 'CONNECTION'
        except Exception as e:
            logger.exception("Error generating outline")
            return False, str(e), 'UNKNOWN'

    def get_asciidoc_help(self, question: str) -> Tuple[bool, str, str]:
        """
        Get help about AsciiDoc syntax.

        Args:
            question: The question about AsciiDoc

        Returns:
            Tuple of (success, answer/error_message, error_type)
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/asciidoc-help",
                json={"question": question},
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return True, data.get('answer', ''), ''
            else:
                error_data = response.json()
                return False, error_data.get('error', 'Unknown error'), 'API_ERROR'

        except Timeout:
            return False, 'Request timed out. Please try again.', 'TIMEOUT'
        except ConnectionError:
            return False, 'Cannot connect to Claude service. Make sure it is running.', 'CONNECTION'
        except Exception as e:
            logger.exception("Error getting AsciiDoc help")
            return False, str(e), 'UNKNOWN'


# Singleton instance for easy access
_claude_client: Optional[ClaudeClient] = None


def get_claude_client(base_url: str = "http://localhost:3000") -> ClaudeClient:
    """
    Get or create the Claude client singleton.

    Args:
        base_url: Base URL of the Claude service

    Returns:
        ClaudeClient instance
    """
    global _claude_client
    if _claude_client is None:
        _claude_client = ClaudeClient(base_url)
    return _claude_client