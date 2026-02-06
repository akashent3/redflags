"""Google Gemini API client for LLM operations."""

import logging
from typing import List, Optional

import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Google Gemini API."""

    def __init__(self):
        """Initialize Gemini client with API key."""
        genai.configure(api_key=settings.gemini_api_key)

        # Default model - using Gemini 2.5 Pro (latest and most capable)
        # Note: Model names may need adjustment based on API version
        # Available: models/gemini-2.5-pro, models/gemini-2.5-flash, models/gemini-2.0-flash
        self.model_name = "models/gemini-2.5-pro"  # Latest Gemini 2.5 model
        try:
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            logger.warning(f"Failed to initialize model {self.model_name}: {e}. Trying models/gemini-2.5-flash...")
            self.model_name = "models/gemini-2.5-flash"
            self.model = genai.GenerativeModel(self.model_name)

        logger.info(f"Gemini client initialized with model: {self.model_name}")

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        model_name: Optional[str] = None,
    ) -> str:
        """
        Generate text using Gemini.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            model_name: Optional model override

        Returns:
            Generated text

        Raises:
            Exception: If generation fails
        """
        try:
            # Use custom model if specified
            if model_name and model_name != self.model_name:
                model = genai.GenerativeModel(model_name)
            else:
                model = self.model

            # Generation config
            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            }

            # Safety settings - disable blocking for financial analysis
            from google.generativeai.types import HarmCategory, HarmBlockThreshold

            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }

            # Generate
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings,
            )

            # Extract text with robust error handling
            try:
                # Try accessing the response text directly (most common)
                try:
                    generated_text = response.text
                    logger.info(f"Generated {len(generated_text)} characters")
                    return generated_text
                except (ValueError, AttributeError) as e:
                    logger.debug(f"Direct text access failed: {e}")

                # Fallback: Try accessing via candidates structure
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]

                    # Check finish reason for blocking
                    if hasattr(candidate, 'finish_reason'):
                        finish_reason = candidate.finish_reason
                        if finish_reason == 2:  # SAFETY
                            logger.warning("Response blocked by safety filters")
                        elif finish_reason == 3:  # RECITATION
                            logger.warning("Response blocked due to recitation")
                        elif finish_reason == 4:  # OTHER
                            logger.warning(f"Response blocked for other reasons: {finish_reason}")

                    # Try to extract text anyway
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        if len(candidate.content.parts) > 0:
                            generated_text = candidate.content.parts[0].text
                            logger.info(f"Generated {len(generated_text)} characters")
                            return generated_text

                logger.warning("Gemini returned no readable content")
                return ""

            except (IndexError, AttributeError) as e:
                logger.error(f"Failed to extract text from response: {e}")
                return ""

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}", exc_info=True)
            raise Exception(f"Gemini API error: {str(e)}")

    def generate_structured_output(
        self,
        prompt: str,
        output_format: str = "json",
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> str:
        """
        Generate structured output (JSON, CSV, etc.).

        Args:
            prompt: Input prompt
            output_format: Desired output format ('json', 'csv', etc.)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (lower for structured output)

        Returns:
            Generated structured output as string
        """
        # Add format instruction to prompt
        structured_prompt = f"{prompt}\n\nProvide the output in {output_format.upper()} format only."

        return self.generate_text(
            prompt=structured_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def analyze_financial_text(
        self, text: str, analysis_type: str, context: Optional[str] = None
    ) -> str:
        """
        Analyze financial text with Gemini.

        Args:
            text: Financial text to analyze
            analysis_type: Type of analysis ('red_flags', 'sentiment', 'extract_numbers', etc.)
            context: Optional context for analysis

        Returns:
            Analysis result
        """
        # Build analysis prompt based on type
        if analysis_type == "red_flags":
            prompt = f"""Analyze the following financial text for red flags or concerning patterns:

{text}

Identify:
1. Unusual language or defensive tone
2. Contradictions or inconsistencies
3. Vague explanations for poor performance
4. Increased jargon or complexity
5. Concerning risk factors

Provide specific examples with quotes."""

        elif analysis_type == "sentiment":
            prompt = f"""Analyze the sentiment and tone of this financial text:

{text}

Rate the sentiment as:
- Positive/Optimistic
- Neutral
- Negative/Defensive

Provide reasoning with examples."""

        elif analysis_type == "extract_numbers":
            prompt = f"""Extract key financial numbers from this text:

{text}

Extract:
- Revenue figures
- Profit/Loss numbers
- Cash flow amounts
- Debt figures
- Any percentages or ratios

Format as JSON."""

        else:
            prompt = f"Analyze this financial text:\n\n{text}"

        if context:
            prompt = f"Context: {context}\n\n{prompt}"

        return self.generate_text(prompt=prompt, temperature=0.2)

    def batch_generate(
        self, prompts: List[str], max_tokens: int = 2048, temperature: float = 0.7
    ) -> List[str]:
        """
        Generate text for multiple prompts (sequential).

        Args:
            prompts: List of prompts
            max_tokens: Maximum tokens per generation
            temperature: Sampling temperature

        Returns:
            List of generated texts
        """
        results = []

        for i, prompt in enumerate(prompts):
            try:
                logger.info(f"Processing prompt {i + 1}/{len(prompts)}")
                result = self.generate_text(
                    prompt=prompt, max_tokens=max_tokens, temperature=temperature
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process prompt {i + 1}: {e}")
                results.append(f"ERROR: {str(e)}")

        return results

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        try:
            # Gemini uses ~4 characters per token (rough estimate)
            return len(text) // 4
        except Exception as e:
            logger.error(f"Token counting failed: {e}")
            return 0


# Singleton instance
gemini_client = GeminiClient()
