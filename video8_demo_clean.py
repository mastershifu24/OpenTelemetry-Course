from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
import logging
import time

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
console_span_exporter = ConsoleSpanExporter()
span_processor = SimpleSpanProcessor(console_span_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

console_metric_exporter = ConsoleMetricExporter()
reader = PeriodicExportingMetricReader(
    console_metric_exporter,
    export_interval_millis=1000
)
metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))
meter = metrics.get_meter(__name__)

request_counter = meter.create_counter(
    name="http_requests_total",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("demo_app")

for i in range(3):
    with tracer.start_as_current_span("process_request") as span:
        request_counter.add(1)
        logger.info(f"User login successful (iteration {i+1})")
        if i == 1:
            logger.error("Database connection failed")
        time.sleep(0.5)
