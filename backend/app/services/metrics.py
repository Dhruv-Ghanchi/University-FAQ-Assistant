from typing import Dict, List, Optional
from app.schemas import MetricsResponse

class MetricsService:
    def __init__(self):
        self.total_requests = 0
        self.total_tokens_original = 0
        self.total_tokens_compressed = 0
        self.total_latency_ms = 0
        self.fallback_count = 0
        self.latencies = []

    def log_request(self, original_tokens: int, compressed_tokens: int, latency_ms: int, fallback: bool = False):
        self.total_requests += 1
        self.total_tokens_original += original_tokens
        
        if fallback:
            self.fallback_count += 1
            self.total_tokens_compressed += original_tokens # No saving
        else:
            self.total_tokens_compressed += compressed_tokens
            
        self.total_latency_ms += latency_ms
        self.latencies.append(latency_ms)

    def get_summary(self) -> MetricsResponse:
        avg_latency = self.total_latency_ms / self.total_requests if self.total_requests > 0 else 0
        
        saved = self.total_tokens_original - self.total_tokens_compressed
        
        ratio = 1.0
        if self.total_tokens_original > 0:
            ratio = self.total_tokens_compressed / self.total_tokens_original
            
        return MetricsResponse(
            total_requests=self.total_requests,
            total_tokens_saved=max(0, saved),
            avg_latency_ms=round(avg_latency, 2),
            avg_compression_ratio=round(ratio, 2),
            fallback_count=self.fallback_count
        )

metrics_service = MetricsService()
