# =============================================================================
# video8_demo.py - OpenTelemetry Demonstration Script
# =============================================================================
# This script demonstrates the three pillars of observability:
#   1. TRACING  - Tracks the journey of a request through your application
#   2. METRICS  - Numerical measurements (like counting how many requests happened)
#   3. LOGGING  - Human-readable messages about what's happening in your app
#
# OpenTelemetry (often called "OTel") is an open-source framework that helps
# developers collect and export telemetry data (traces, metrics, logs) from
# their applications. Think of it as "instrumentation" - adding sensors to
# your code so you can see what's happening inside.
# =============================================================================
#
# =============================================================================
# WHY THIS MATTERS FOR YOUR CAREER
# =============================================================================
# Observability skills are EXTREMELY valuable in today's job market because:
#
#   1. EVERY production system needs monitoring - you WILL encounter this
#   2. It's a skill gap - many developers don't understand observability well
#   3. It's critical for DevOps, SRE, Platform Engineering, and Backend roles
#   4. Companies like Google, Netflix, Uber built their success on observability
#   5. OpenTelemetry is becoming THE industry standard (backed by CNCF)
#
# Job titles that use these skills daily:
#   - Site Reliability Engineer (SRE) - $150k-250k+ salary range
#   - DevOps Engineer - $120k-200k+ salary range
#   - Platform Engineer - $140k-220k+ salary range
#   - Backend Engineer - $130k-200k+ salary range
#   - Data Engineer (for pipeline monitoring) - $130k-200k+ salary range
#
# Interview questions you might face:
#   - "How would you debug a slow API endpoint in production?"
#   - "Explain the difference between metrics, logs, and traces"
#   - "How do you monitor a distributed microservices system?"
#   - "What's your approach to alerting and on-call?"
# =============================================================================


# =============================================================================
# IMPORTS - Bringing in the tools we need
# =============================================================================
# 
# PRIORITY: MEDIUM - You don't need to memorize these imports
# Just understand WHAT each category does. You'll copy-paste these in real work.
# =============================================================================

# -----------------------------------------------------------------------------
# OpenTelemetry Core Imports
# -----------------------------------------------------------------------------

# 'trace' - The main module for creating and managing traces
# 'metrics' - The main module for creating and managing metrics
# These are like the "front doors" to OpenTelemetry's tracing and metrics systems
from opentelemetry import trace, metrics

# 'TracerProvider' - A factory that creates tracers
# Think of it as a "tracer machine" - you set it up once, then it produces tracers
# A tracer is what actually creates spans (units of work in a trace)
from opentelemetry.sdk.trace import TracerProvider

# 'MeterProvider' - A factory that creates meters (similar to TracerProvider but for metrics)
# A meter is what creates and manages metric instruments like counters and gauges
from opentelemetry.sdk.metrics import MeterProvider

# 'SimpleSpanProcessor' - Processes spans one at a time, immediately when they end
# Good for development/debugging but not recommended for production (use BatchSpanProcessor)
# 'ConsoleSpanExporter' - Sends span data to the console (terminal) so we can see it
# In production, you'd use exporters that send to Jaeger, Zipkin, or other backends
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

# 'ConsoleMetricExporter' - Sends metric data to the console (terminal)
# 'PeriodicExportingMetricReader' - Collects and exports metrics at regular intervals
# This reader periodically "reads" all the metrics and sends them to the exporter
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader

# -----------------------------------------------------------------------------
# Python Standard Library Imports
# -----------------------------------------------------------------------------

# 'logging' - Python's built-in logging module
# Allows us to write log messages at different severity levels (DEBUG, INFO, WARNING, ERROR, etc.)
# Much better than print() because you can control what gets logged and where it goes
#
# CAREER TIP: NEVER use print() in production code. Always use logging.
# This is a common junior developer mistake that will be noticed in code reviews.
import logging

# 'time' - Python's built-in time module
# We'll use time.sleep() to simulate work being done (like a slow database query)
import time


# =============================================================================
# TRACING SETUP
# =============================================================================
#
# *****************************************************************************
# PRIORITY: HIGH - TRACING IS THE MOST IMPORTANT SKILL HERE
# *****************************************************************************
#
# WHY TRACING MATTERS MOST:
#   - It's how you debug problems in production (you can't use a debugger there!)
#   - It's essential for microservices (where requests jump between services)
#   - It answers: "Why is this request slow?" and "Where did it fail?"
#   - Interviewers LOVE asking about distributed tracing
#
# KEY CONCEPTS TO MEMORIZE (these come up in interviews):
#   - TRACE: A complete journey of a request (made up of multiple spans)
#   - SPAN: A single unit of work within a trace (like "query database" or "call API")
#   - TRACE ID: Unique ID that ties all spans together (like a case number)
#   - SPAN ID: Unique ID for each individual span
#   - PARENT SPAN: The span that started the current span (creates the hierarchy)
#   - CONTEXT PROPAGATION: Passing trace IDs between services (VERY IMPORTANT!)
#
# REAL-WORLD SCENARIO:
#   User clicks "Buy" -> Web Server (span 1) -> Payment Service (span 2) 
#   -> Database (span 3) -> Email Service (span 4)
#   All 4 spans share the same TRACE ID, so you can see the whole journey!
#
# TOOLS YOU'LL USE AT WORK:
#   - Jaeger (open source, very popular)
#   - Zipkin (open source, simpler)
#   - Datadog APM (enterprise, expensive but powerful)
#   - New Relic (enterprise)
#   - AWS X-Ray (if you're on AWS)
#   - Honeycomb (modern, loved by developers)
# =============================================================================

# Create a TracerProvider and set it as the global tracer provider
# This is like saying "this is THE tracer factory for the entire application"
# set_tracer_provider() makes this provider available globally via trace.get_tracer_provider()
#
# FOCUS: This is "boilerplate" - code you write once and rarely change.
# In real projects, this setup is usually in a separate config file.
trace.set_tracer_provider(TracerProvider())

# Get a tracer from the global provider
# __name__ is a Python variable that contains the current module's name (e.g., "otl")
# This helps identify where spans came from when debugging
# The tracer is what we'll use to create spans in our code
#
# FOCUS: This line is what you'll write in YOUR code files.
# Each file/module gets its own tracer with its own name.
tracer = trace.get_tracer(__name__)

# Create a ConsoleSpanExporter - this will print span data to the terminal
# Useful for development and learning, but in production you'd use
# exporters like OTLPSpanExporter (sends to OpenTelemetry Collector)
#
# CAREER NOTE: In production, you'll use OTLPSpanExporter which sends to
# an OpenTelemetry Collector. The Collector then forwards to Jaeger/Datadog/etc.
# This pattern is called "vendor-neutral instrumentation" - a big selling point of OTel.
console_span_exporter = ConsoleSpanExporter()

# Create a SimpleSpanProcessor that uses our console exporter
# The processor is the "middleman" between your code and the exporter
# SimpleSpanProcessor exports spans immediately when they end (synchronously)
# For production, use BatchSpanProcessor which batches spans for efficiency
#
# INTERVIEW TIP: Know the difference between SimpleSpanProcessor and BatchSpanProcessor:
#   - SimpleSpanProcessor: Immediate, blocking, good for debugging, bad for performance
#   - BatchSpanProcessor: Batches spans, async, good for production, minimal overhead
span_processor = SimpleSpanProcessor(console_span_exporter)

# Add the span processor to our tracer provider
# This connects the processing pipeline: Tracer -> Span -> Processor -> Exporter -> Console
# get_tracer_provider() returns the global provider we set earlier
trace.get_tracer_provider().add_span_processor(span_processor)


# =============================================================================
# METRICS SETUP
# =============================================================================
#
# *****************************************************************************
# PRIORITY: HIGH - METRICS ARE ESSENTIAL FOR DASHBOARDS AND ALERTS
# *****************************************************************************
#
# WHY METRICS MATTER:
#   - They power your dashboards (Grafana, Datadog, etc.)
#   - They trigger your alerts ("Page me if error rate > 5%")
#   - They answer: "How many?", "How fast?", "How much?"
#   - Without metrics, you're flying blind in production
#
# KEY CONCEPTS TO MEMORIZE:
#   - COUNTER: Goes up only (requests, errors, bytes sent)
#   - GAUGE: Can go up or down (CPU%, active connections, queue size)
#   - HISTOGRAM: Tracks distribution (latency percentiles - p50, p95, p99)
#
# THE MOST IMPORTANT METRICS (memorize these - they're industry standard):
#   These are called the "Four Golden Signals" (from Google's SRE book):
#   1. LATENCY: How long requests take (use histogram for percentiles)
#   2. TRAFFIC: How many requests you're getting (use counter)
#   3. ERRORS: How many requests fail (use counter)
#   4. SATURATION: How "full" your system is (use gauge - CPU%, memory%)
#
# ANOTHER FRAMEWORK: RED Method (for microservices)
#   - Rate: Requests per second
#   - Errors: Failed requests per second
#   - Duration: Time per request (latency)
#
# TOOLS YOU'LL USE AT WORK:
#   - Prometheus (open source, VERY popular - learn this!)
#   - Grafana (for dashboards - pairs with Prometheus)
#   - Datadog (enterprise, all-in-one)
#   - CloudWatch (AWS native)
#   - InfluxDB (time-series database)
# =============================================================================

# Create a ConsoleMetricExporter - prints metric data to the terminal
console_metric_exporter = ConsoleMetricExporter()

# Create a PeriodicExportingMetricReader
# This reader will collect all metrics and export them every 1000 milliseconds (1 second)
# The reader acts as a scheduler: "every X milliseconds, gather metrics and send them out"
# export_interval_millis=1000 means metrics are exported once per second
#
# REAL-WORLD: In production, you'd typically export every 10-60 seconds.
# More frequent = more data = more cost. Less frequent = less granularity.
reader = PeriodicExportingMetricReader(
    console_metric_exporter,
    export_interval_millis=1000  # Export metrics every 1000ms (1 second)
)

# Create a MeterProvider with our reader and set it as the global meter provider
# metric_readers is a list because you can have multiple readers (e.g., one for console, one for Prometheus)
# set_meter_provider() makes this provider available globally
metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))

# Get a meter from the global provider
# Like with tracing, __name__ helps identify where metrics came from
# The meter is what we'll use to create metric instruments (counters, gauges, etc.)
meter = metrics.get_meter(__name__)

# *****************************************************************************
# FOCUS HERE: This is the code pattern you'll use most often
# *****************************************************************************
#
# Create a Counter metric instrument named "http_requests_total"
# A counter is perfect for counting events (requests, errors, logins, etc.)
#
# NAMING CONVENTION (Prometheus style - MEMORIZE THIS):
#   Format: <namespace>_<name>_<unit>
#   Examples:
#     - http_requests_total (total HTTP requests)
#     - http_request_duration_seconds (how long requests take)
#     - process_cpu_seconds_total (CPU time used)
#     - myapp_orders_created_total (business metric)
#
# CAREER TIP: Good metric names are:
#   - Descriptive (http_requests, not just "requests")
#   - Include units (duration_seconds, not just "duration")
#   - Use snake_case
#   - End with _total for counters, _seconds for time, _bytes for size
request_counter = meter.create_counter(
    name="http_requests_total",  # The name that will appear in metric output
    # Optional: you can also add description and unit
    # description="Total number of HTTP requests received",
    # unit="1"  # "1" means it's a count (dimensionless)
)


# =============================================================================
# LOGGING SETUP
# =============================================================================
#
# *****************************************************************************
# PRIORITY: MEDIUM-HIGH - Logging is simpler but still crucial
# *****************************************************************************
#
# WHY LOGGING MATTERS:
#   - It's the first thing you check when something goes wrong
#   - It provides human-readable context that traces/metrics can't
#   - It's the easiest to implement (just logger.info("message"))
#   - Every developer needs to know proper logging
#
# LOG LEVELS (from least to most severe) - MEMORIZE THESE:
#   - DEBUG: Detailed info for developers (variable values, function entries)
#   - INFO: General operational messages (user logged in, task started)
#   - WARNING: Something unexpected but not critical (deprecated API usage)
#   - ERROR: Something failed (database connection lost, file not found)
#   - CRITICAL: App is about to crash (out of memory, required service down)
#
# COMMON BEGINNER MISTAKES TO AVOID:
#   1. Using print() instead of logging - NEVER do this in real code
#   2. Logging sensitive data (passwords, credit cards, tokens)
#   3. Not including context (bad: "Error occurred", good: "Failed to save user_id=123")
#   4. Wrong log level (using ERROR for warnings, or INFO for debugging)
#   5. Logging too much (slows down app, increases costs)
#   6. Logging too little (can't debug production issues)
#
# TOOLS YOU'LL USE AT WORK:
#   - ELK Stack (Elasticsearch, Logstash, Kibana) - very popular
#   - Splunk (enterprise, powerful, expensive)
#   - CloudWatch Logs (AWS)
#   - Datadog Logs
#   - Loki + Grafana (open source alternative to ELK)
#
# STRUCTURED LOGGING (ADVANCED - learn this next):
#   Instead of: logger.info("User 123 logged in from IP 1.2.3.4")
#   Use: logger.info("User logged in", extra={"user_id": 123, "ip": "1.2.3.4"})
#   This makes logs searchable! ("Show me all logs where user_id=123")
# =============================================================================

# Configure the root logger with basic settings
# level=logging.INFO means we'll see INFO, WARNING, ERROR, and CRITICAL messages
# DEBUG messages will be hidden (you'd set level=logging.DEBUG to see them)
# basicConfig sets up a default handler that prints to console
#
# REAL-WORLD: In production, you'd configure logging to:
#   - Write to files (with rotation so they don't fill up disk)
#   - Send to a log aggregator (ELK, Splunk, CloudWatch)
#   - Include timestamps, hostnames, request IDs
logging.basicConfig(level=logging.INFO)

# Create a named logger for our application
# Using a named logger (instead of the root logger) helps you:
#   1. Filter logs by source (e.g., only show "demo_app" logs)
#   2. Apply different settings to different parts of your app
# The name "demo_app" will appear in log output so you know where it came from
#
# BEST PRACTICE: Use __name__ as the logger name in real code:
#   logger = logging.getLogger(__name__)
# This automatically uses the module name, making logs easy to trace.
logger = logging.getLogger("demo_app")


# =============================================================================
# DEMO LOOP - Simulating HTTP Requests
# =============================================================================
#
# *****************************************************************************
# FOCUS HERE: This is where the "magic" happens - the actual instrumentation
# *****************************************************************************
#
# This loop simulates a web server handling 3 HTTP requests.
# In real apps, this code would be in your request handlers (Flask routes,
# FastAPI endpoints, Django views, etc.)
#
# THE PATTERN TO INTERNALIZE:
#   1. Start a span at the beginning of an operation
#   2. Record metrics (counters, histograms) during the operation
#   3. Log important events and errors
#   4. Span automatically ends when the 'with' block exits
# =============================================================================

# Loop 3 times to simulate handling 3 HTTP requests
# range(3) produces [0, 1, 2], so 'i' will be 0, 1, then 2
for i in range(3):
    
    # -------------------------------------------------------------------------
    # START A TRACE SPAN
    # -------------------------------------------------------------------------
    #
    # *****************************************************************************
    # THIS IS THE MOST IMPORTANT PATTERN IN THE ENTIRE FILE - MEMORIZE IT
    # *****************************************************************************
    #
    # 'with' statement creates a context manager that:
    #   1. Starts the span when entering the 'with' block
    #   2. Automatically ends the span when exiting the 'with' block
    #   3. Handles errors by recording exceptions on the span
    #
    # start_as_current_span("process_request"):
    #   - Creates a new span named "process_request"
    #   - Sets it as the "current" span (so child spans know their parent)
    #   - Returns the span object so we can add attributes/events to it
    #
    # NAMING SPANS (important for readability in Jaeger/etc.):
    #   Good names: "process_request", "query_users_table", "send_email", "validate_payment"
    #   Bad names: "span1", "do_stuff", "function", "work"
    #
    # INTERVIEW QUESTION: "How does context propagation work?"
    # Answer: The trace context (trace_id, span_id) is automatically passed to child
    # spans. When calling other services, you serialize this context into HTTP headers
    # (usually 'traceparent' header) so the receiving service can continue the trace.
    # -------------------------------------------------------------------------
    with tracer.start_as_current_span("process_request") as span:
        
        # ADDING ATTRIBUTES TO SPANS (very useful for debugging):
        # Attributes are key-value pairs that add context to your span.
        # These show up in Jaeger/Zipkin and help you filter/search traces.
        #
        # SEMANTIC CONVENTIONS: OpenTelemetry defines standard attribute names.
        # Using these makes your data consistent and tools understand it better.
        # Examples:
        #   span.set_attribute("http.method", "GET")
        #   span.set_attribute("http.url", "/api/users")
        #   span.set_attribute("http.status_code", 200)
        #   span.set_attribute("db.system", "postgresql")
        #   span.set_attribute("db.statement", "SELECT * FROM users")
        #
        # You could add attributes to the span for more context:
        # span.set_attribute("request.id", i)
        # span.set_attribute("http.method", "GET")
        # span.set_attribute("http.url", "/api/users")
        
        # ---------------------------------------------------------------------
        # INCREMENT THE METRIC COUNTER
        # ---------------------------------------------------------------------
        #
        # *****************************************************************************
        # SECOND MOST IMPORTANT PATTERN - Recording metrics
        # *****************************************************************************
        #
        # add(1) increases the counter by 1
        # This is how we count events - each time this line runs, the total goes up
        # The counter remembers the total, and it gets exported every 1 second
        # 
        # ADDING LABELS/ATTRIBUTES (powerful for slicing data):
        # Labels let you break down metrics by categories:
        #   request_counter.add(1, {"http.method": "GET", "http.status_code": "200"})
        #   request_counter.add(1, {"http.method": "POST", "http.status_code": "201"})
        #
        # Now you can query:
        #   - Total requests (sum all)
        #   - GET requests only (filter by method)
        #   - Failed requests (filter by status_code >= 400)
        #
        # WARNING: Don't use high-cardinality labels (like user_id or request_id)!
        # This creates too many metric series and can crash your monitoring system.
        # Bad: {"user_id": "12345"} - millions of unique values
        # Good: {"region": "us-west"} - handful of unique values
        # ---------------------------------------------------------------------
        request_counter.add(1)
        
        # ---------------------------------------------------------------------
        # LOG A SUCCESS MESSAGE
        # ---------------------------------------------------------------------
        # logger.info() logs at the INFO level (general operational info)
        # f-string (f"...") lets us embed the variable 'i+1' in the message
        # We use i+1 because humans count from 1, not 0
        #
        # LOGGING BEST PRACTICES:
        #   - Include context: WHO (user_id), WHAT (action), RESULT (success/failure)
        #   - Be concise but informative
        #   - Don't log passwords, tokens, or PII (personally identifiable information)
        #
        # PRODUCTION PATTERN (structured logging):
        #   logger.info("User login successful", extra={
        #       "user_id": user.id,
        #       "ip_address": request.ip,
        #       "iteration": i+1
        #   })
        # ---------------------------------------------------------------------
        logger.info(f"User login successful (iteration {i+1})")
        
        # ---------------------------------------------------------------------
        # SIMULATE AN ERROR (on the second request only)
        # ---------------------------------------------------------------------
        # When i == 1 (second iteration, since we count from 0), we log an error
        # This demonstrates how errors appear in logs
        # 
        # ERROR HANDLING IN PRODUCTION:
        # When an error occurs, you should:
        #   1. Log the error with full context (logger.error or logger.exception)
        #   2. Record the exception on the span (span.record_exception(e))
        #   3. Set the span status to error (span.set_status(...))
        #   4. Increment an error counter metric (errors_total.add(1))
        #
        # EXAMPLE:
        #   try:
        #       result = database.query("SELECT * FROM users")
        #   except Exception as e:
        #       logger.exception("Database query failed")  # Logs stack trace
        #       span.record_exception(e)
        #       span.set_status(Status(StatusCode.ERROR, str(e)))
        #       error_counter.add(1, {"error_type": type(e).__name__})
        #       raise  # Re-raise so the caller knows something failed
        # ---------------------------------------------------------------------
        if i == 1:  # Only on the second request (index 1)
            logger.error("Database connection failed")
        
        # ---------------------------------------------------------------------
        # SIMULATE PROCESSING TIME
        # ---------------------------------------------------------------------
        # time.sleep(0.5) pauses execution for 0.5 seconds (500 milliseconds)
        # This simulates real work being done, like:
        #   - Querying a database
        #   - Calling an external API
        #   - Processing data
        #
        # In the trace output, you'll see the span duration reflects this sleep time
        # This helps identify slow operations in your application
        #
        # PRODUCTION INSIGHT: Tracing shows you WHERE time is spent.
        # If a request takes 2 seconds and you have spans for each step:
        #   - validate_request: 10ms
        #   - query_database: 1800ms  <- AHA! Database is slow!
        #   - send_response: 5ms
        # You immediately know to optimize the database query.
        # ---------------------------------------------------------------------
        time.sleep(0.5)
        
    # When we exit the 'with' block, the span automatically ends
    # The SimpleSpanProcessor immediately exports it to the console


# =============================================================================
# WHAT TO LOOK FOR IN THE OUTPUT
# =============================================================================
# When you run this script, you'll see:
#
# 1. LOG MESSAGES (from the logger):
#    INFO:demo_app:User login successful (iteration 1)
#    INFO:demo_app:User login successful (iteration 2)
#    ERROR:demo_app:Database connection failed
#    INFO:demo_app:User login successful (iteration 3)
#
# 2. TRACE SPANS (from the ConsoleSpanExporter):
#    {
#        "name": "process_request",
#        "context": { "trace_id": "...", "span_id": "..." },
#        "start_time": "...",
#        "end_time": "...",
#        ...
#    }
#
# 3. METRICS (from the ConsoleMetricExporter, every 1 second):
#    {
#        "resource_metrics": [...],
#        "metrics": [
#            { "name": "http_requests_total", "value": 3 }
#        ]
#    }
#
# Notice how all three types of telemetry work together:
#   - Logs tell you WHAT happened ("User login successful")
#   - Traces tell you HOW LONG things took and the request flow
#   - Metrics tell you HOW MUCH happened (3 total requests)
# =============================================================================


# =============================================================================
# NEXT STEPS FOR YOUR LEARNING JOURNEY
# =============================================================================
#
# BEGINNER (do these first):
#   [ ] Run this script and understand the output
#   [ ] Modify the span name and see it change in output
#   [ ] Add span.set_attribute() calls and see them appear
#   [ ] Change the log level to DEBUG and add debug messages
#   [ ] Create a second counter for errors and increment it in the if block
#
# INTERMEDIATE (after you're comfortable):
#   [ ] Set up Jaeger locally with Docker and send traces there
#   [ ] Set up Prometheus + Grafana and create a dashboard
#   [ ] Learn about context propagation between services
#   [ ] Implement structured logging with JSON output
#   [ ] Add histogram metrics for latency (request duration)
#
# ADVANCED (when you want to level up):
#   [ ] Set up OpenTelemetry Collector as a central hub
#   [ ] Implement auto-instrumentation for Flask/FastAPI
#   [ ] Learn about sampling strategies (head-based, tail-based)
#   [ ] Connect logs, traces, and metrics (correlation)
#   [ ] Build custom exporters
#
# RESOURCES:
#   - OpenTelemetry Docs: https://opentelemetry.io/docs/
#   - Google SRE Book (free): https://sre.google/sre-book/table-of-contents/
#   - Jaeger Docs: https://www.jaegertracing.io/docs/
#   - Prometheus Docs: https://prometheus.io/docs/
# =============================================================================


# =============================================================================
# INTERVIEW CHEAT SHEET
# =============================================================================
#
# Q: "What are the three pillars of observability?"
# A: Logs, Metrics, and Traces. Logs are human-readable events, metrics are
#    numerical measurements over time, traces track request flow through systems.
#
# Q: "What is a span?"
# A: A span represents a unit of work in a trace. It has a name, start/end time,
#    attributes, and can have parent/child relationships with other spans.
#
# Q: "What are the Four Golden Signals?"
# A: Latency, Traffic, Errors, and Saturation. These are the four key metrics
#    for monitoring any system, as defined by Google's SRE practices.
#
# Q: "What's the difference between a counter and a gauge?"
# A: A counter only goes up (total requests, total errors). A gauge can go up
#    or down (CPU usage, active connections, queue size).
#
# Q: "How does distributed tracing work across services?"
# A: Context propagation. The trace context (trace_id, span_id) is passed in
#    HTTP headers (typically 'traceparent'). Each service extracts this context
#    and creates child spans that reference the same trace_id.
#
# Q: "Why use OpenTelemetry instead of Datadog/New Relic directly?"
# A: Vendor neutrality. OTel lets you instrument once and export to any backend.
#    If you switch from Datadog to Jaeger, you just change the exporter, not
#    your application code.
#
# Q: "What's the difference between SimpleSpanProcessor and BatchSpanProcessor?"
# A: SimpleSpanProcessor exports spans immediately (blocking, good for debugging).
#    BatchSpanProcessor batches spans and exports async (better performance for
#    production, minimizes overhead).
# =============================================================================
