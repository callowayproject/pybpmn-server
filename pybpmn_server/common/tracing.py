"""OpenTelemetry Configuration."""

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
)

from pybpmn_server.common.memory_exporter import ConsoleSpanExporter, InMemorySpanExporter


def configure() -> ConsoleSpanExporter:
    provider = TracerProvider(resource=Resource.create({SERVICE_NAME: "pybpmn_server"}))

    # local collector
    # span_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
    # processor = BatchSpanProcessor(span_exporter)

    # For testing
    span_exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(span_exporter)

    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return span_exporter


"""
export OTEL_RESOURCE_ATTRIBUTES="service.name=<service-name>"
export OTEL_EXPORTER_OTLP_ENDPOINT="https://ingest.<region>.signoz.cloud:443"
export OTEL_EXPORTER_OTLP_HEADERS="signoz-ingestion-key=<your-ingestion-key>"
export OTEL_EXPORTER_OTLP_PROTOCOL="grpc"
"""
