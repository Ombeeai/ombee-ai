"""
Arize Phoenix Cloud Monitoring Setup for Ombee AI
Sends data to hosted Phoenix Cloud dashboard
"""
from datetime import datetime
from phoenix.otel import register
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from src.config import PHOENIX_API_KEY, PHOENIX_COLLECTOR_ENDPOINT

import os
import io
import json
import time
import warnings
import logging
import contextlib
import traceback

# Reduce noisy logs from OpenTelemetry / phoenix / http libs
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("opentelemetry").setLevel(logging.WARNING)
logging.getLogger("phoenix").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Silence specific Phoenix user warning about inferring protocol
warnings.filterwarnings("ignore", message="Could not infer collector endpoint protocol")

class OmbeeMonitor:
    """Monitor and trace all RAG interactions to Phoenix Cloud"""

    def __init__(self, project_name="ombee-ai"):
        self.project_name = project_name
        self.api_key = PHOENIX_API_KEY
        self.phoenix_collector_endpoint = PHOENIX_COLLECTOR_ENDPOINT or "https://app.phoenix.arize.com"
        # tracer will be set if monitoring successfully starts; callers can check truthiness
        self.tracer = None

    def start_monitoring(self):
        """Start Phoenix Cloud tracing; register() reads env vars set below."""
        try:
            if not self.api_key:
                print("PHOENIX_API_KEY not found. Monitoring disabled.")
                self.tracer = None
                return None

            # Ensure env vars used by phoenix.register() are present
            os.environ["PHOENIX_API_KEY"] = self.api_key
            os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = self.phoenix_collector_endpoint
            os.environ["PHOENIX_PROJECT_NAME"] = self.project_name

            # Suppress prints/warnings from phoenix.register() to keep terminal clean
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                register()

            # Create tracer for span creation
            provider = trace.get_tracer_provider()
            self.tracer = trace.get_tracer(__name__)
            print("Phoenix Cloud monitoring active!")
            print(f"View dashboard at: {self.phoenix_collector_endpoint}")
            return True

        except Exception as e:
            print(f"Phoenix monitoring failed to start: {e}")
            self.tracer = None
            return None

    def log_query(
        self,
        query: str,
        domain: str,
        confidence: float,
        response: str,
        sources: list,
        latency: float = None,               # seconds
        context: str = "",
        error: str = None,
        status: str | None = None,
        retrieval_time: float | None = None,  # seconds
        generation_time: float | None = None, # seconds
        cumulative_tokens: int | None = None,
        cumulative_cost: float | None = None,
        **kwargs,
    ):
        """Log a complete RAG interaction to Phoenix Cloud via OpenTelemetry spans."""
        if not self.tracer:
            return

        try:
            with self.tracer.start_as_current_span("rag_query") as span:
                # Core attributes
                span.set_attribute("input.value", str(query))
                span.set_attribute("routing.domain", str(domain))
                try:
                    span.set_attribute("routing.confidence", float(confidence))
                except Exception:
                    span.set_attribute("routing.confidence", 0.0)

                span.set_attribute("status", str(status or "unknown"))
                span.set_attribute("kind", "server")

                # Convert s to ms for Phoenix
                if latency is not None:
                    try:
                        span.set_attribute("latency_ms", float(latency) * 1000.0)
                    except Exception:
                        pass
                if retrieval_time is not None:
                    try:
                        span.set_attribute("retrieval.latency_ms", float(retrieval_time) * 1000.0)
                    except Exception:
                        pass
                if generation_time is not None:
                    try:
                        span.set_attribute("generation.latency_ms", float(generation_time) * 1000.0)
                    except Exception:
                        pass

                # LLM usage metrics
                if cumulative_tokens is not None:
                    try:
                        span.set_attribute("cumulative_tokens", int(cumulative_tokens))
                    except Exception:
                        pass
                if cumulative_cost is not None:
                    try:
                        span.set_attribute("cumulative_cost", float(cumulative_cost))
                    except Exception:
                        pass

                # Existing fields
                try:
                    span.set_attribute("output.value", str(response)[:2000] if response else "")
                except Exception:
                    pass
                span.set_attribute("timestamp", datetime.utcnow().isoformat())
                try:
                    span.set_attribute("retrieval.num_sources", int(len(sources or [])))
                except Exception:
                    span.set_attribute("retrieval.num_sources", 0)
                if sources:
                    try:
                        span.set_attribute("retrieval.top_sources", json.dumps(sources[:10]))
                    except Exception:
                        try:
                            span.set_attribute("retrieval.top_sources_summary", str(sources[:5]))
                        except Exception:
                            pass
                if context:
                    try:
                        span.set_attribute("retrieval.context_snippet", str(context)[:1000])
                    except Exception:
                        pass
                if error:
                    try:
                        span.set_attribute("error.message", str(error))
                    except Exception:
                        pass

                # Set span status for OTEL (so Phoenix UI can show success/error)
                if error:
                    span.set_status(Status(StatusCode.ERROR, description=str(error)))
                else:
                    span.set_status(Status(StatusCode.OK))

                # Any extra keyword fields (safe-serialized)
                if kwargs:
                    try:
                        span.set_attribute("extra", json.dumps(kwargs))
                    except Exception:
                        try:
                            span.set_attribute("extra_keys", str(list(kwargs.keys())))
                        except Exception:
                            pass

            print("Phoenix log created")

        except Exception as e:
            print(f"Failed to log query to Phoenix: {e}")
            traceback.print_exc()

# Global monitor instance and accessor
monitor = OmbeeMonitor(project_name="ombee-ai")
monitor.start_monitoring()

def get_monitor():
    return monitor