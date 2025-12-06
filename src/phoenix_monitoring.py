"""
Arize Phoenix Cloud Monitoring Setup for Ombee AI
Sends data to hosted Phoenix Cloud dashboard
"""

import os
import json
from datetime import datetime
from phoenix.otel import register
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from src.config import PHOENIX_API_KEY, PHOENIX_COLLECTOR_ENDPOINT
import warnings
import logging
import io
import contextlib

# Reduce noisy logs from OpenTelemetry / phoenix / http libs
logging.getLogger("opentelemetry").setLevel(logging.WARNING)
logging.getLogger("phoenix").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Silence specific Phoenix user warning about inferring protocol
warnings.filterwarnings("ignore", message="Could not infer collector endpoint protocol")

class OmbeeMonitor:
    """Monitor and trace all RAG interactions to Phoenix Cloud"""

    def __init__(self, project_name="ombee-ai-demo"):
        self.project_name = project_name
        self.api_key = PHOENIX_API_KEY
        self.phoenix_collector_endpoint = PHOENIX_COLLECTOR_ENDPOINT or "https://app.phoenix.arize.com"
        # tracer will be set if monitoring successfully starts; callers can check truthiness
        self.tracer = None

    def start_monitoring(self):
        """Start Phoenix Cloud tracing; register() reads env vars set below."""
        try:
            if not self.api_key:
                print("⚠️ PHOENIX_API_KEY not found. Monitoring disabled.")
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
            print("✅ Phoenix Cloud monitoring active!")
            print(f"📊 View dashboard at: {self.phoenix_collector_endpoint}")
            return True

        except Exception as e:
            print(f"⚠️ Phoenix monitoring failed to start: {e}")
            self.tracer = None
            return None

    def log_query(
        self,
        query: str,
        domain: str,
        confidence: float,
        response: str,
        sources: list,
        latency: float,
        context: str = "",
        error: str = None,
        status: str | None = None,
        retrieval_time: float | None = None,
        generation_time: float | None = None,
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
                span.set_attribute("routing.confidence", float(confidence))
                span.set_attribute("output.value", str(response)[:2000] if response else "")
                span.set_attribute("latency.seconds", float(latency) if latency is not None else 0.0)
                span.set_attribute("timestamp", datetime.utcnow().isoformat())

                # Retrieval / generation details
                if retrieval_time is not None:
                    span.set_attribute("retrieval.latency_ms", float(retrieval_time) * 1000.0)
                if generation_time is not None:
                    span.set_attribute("generation.latency_ms", float(generation_time) * 1000.0)

                # Sources / context / status / error
                span.set_attribute("retrieval.num_sources", int(len(sources or [])))
                if sources:
                    try:
                        span.set_attribute("retrieval.top_sources", json.dumps(sources[:10]))
                    except Exception:
                        span.set_attribute("retrieval.top_sources_summary", str(sources[:5]))
                if context:
                    span.set_attribute("retrieval.context_snippet", str(context)[:1000])
                if status is not None:
                    span.set_attribute("response.status", str(status))
                if error:
                    span.set_attribute("error.message", str(error))

                # Any extra keyword fields (safe-serialized)
                if kwargs:
                    try:
                        span.set_attribute("extra", json.dumps(kwargs))
                    except Exception:
                        span.set_attribute("extra_keys", str(list(kwargs.keys())))

            # Confirmation print — export is async/batched, this confirms span was emitted
            print("✅ Phoenix log created")

        except Exception as e:
            # Don't fail the app if logging fails; print for debugging
            import traceback
            print(f"⚠️ Failed to log query to Phoenix: {e}")
            traceback.print_exc()

# Global monitor instance and accessor
monitor = OmbeeMonitor(project_name="ombee-ai-demo")
monitor.start_monitoring()

def get_monitor():
    return monitor