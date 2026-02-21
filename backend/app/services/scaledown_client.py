import time
import requests
import logging
from typing import Dict, Optional
from app.config import config

logger = logging.getLogger(__name__)

class ScaleDownClient:
    BASE_URL = "https://api.scaledown.xyz/v1/compress" # Updated hypothetical endpoint or stick to what was there if working

    def compress_prompt(self, context: str, prompt: str, model: str = None) -> Dict:
        """
        Compresses a prompt using ScaleDown API.
        Returns a dict with compression details for metrics.
        """
        if not config.SCALEDOWN_API_KEY:
            logger.warning("ScaleDown API key missing. Skipping compression.")
            return {
                "compressed_prompt": context, # Fallback to original
                "original_tokens": len(context.split()),  # Rough estimate
                "compressed_tokens": len(context.split()),
                "latency_ms": 0,
                "successful": False,
                "fallback": True
            }

        model = model or config.MODEL_NAME or "gpt-4o-mini"
        
        # Construct the full prompt to be compressed or just context?
        # The user's spec says: compress_prompt(context, prompt, model)
        # Usually we want to compress the context that feeds into the prompt.
        
        payload = {
            "context": context,
            "query": prompt, # ScaleDown usually takes context + query
            "model": model
        }

        # If the user's previous code used specific endpoint/payload, I should probably respect that strictly 
        # unless I know better. The previous code usage:
        # BASE_URL = "https://api.scaledown.xyz/compress/raw/"
        # payload = { "context": ..., "prompt": ..., "model": ..., "scaledown": {"rate": "auto"} }
        
        # I will stick to the previous payload structure but wrap it in the new function signature 
        # to ensure compatibility if the URL was correct.
        
        api_url = "https://api.scaledown.xyz/compress/raw" # Correcting/Keeping URL
        
        payload = {
            "context": context,
            "prompt": prompt,
            "model": model, 
            "scaledown": {"rate": "auto"}
        }

        headers = {
            "x-api-key": config.SCALEDOWN_API_KEY,
            "Content-Type": "application/json"
        }

        start_time = time.time()
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=5)
            latency_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                data = response.json()
                # Handle nested results structure if needed
                results = data.get("results", data)
                
                compressed_text = results.get("compressed_prompt", context)
                original_tokens = results.get("original_prompt_tokens", len(context.split()) * 1.3) # 1.3 is a better estimate for chars->tokens if split is words
                compressed_tokens = results.get("compressed_prompt_tokens", len(compressed_text.split()) * 1.3)
                
                return {
                    "compressed_prompt": compressed_text,
                    "original_tokens": int(original_tokens),
                    "compressed_tokens": int(compressed_tokens),
                    "latency_ms": latency_ms,
                    "successful": True,
                    "fallback": False
                }
            else:
                logger.error(f"ScaleDown API error: {response.status_code} - {response.text}")
                return {
                    "compressed_prompt": context,
                    "original_tokens": len(context.split()),
                    "compressed_tokens": len(context.split()),
                    "latency_ms": latency_ms,
                    "successful": False,
                    "fallback": True
                }

        except Exception as e:
            logger.error(f"ScaleDown connection failed: {e}")
            return {
                "compressed_prompt": context,
                "original_tokens": len(context.split()),
                "compressed_tokens": len(context.split()),
                "latency_ms": int((time.time() - start_time) * 1000),
                "successful": False,
                "fallback": True
            }

scaledown_client = ScaleDownClient()
