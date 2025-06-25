from fastapi import FastAPI
import requests
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.propagate import inject

OTEL_EXPORTER_ENDPOINT = "http://localhost:4317"
API_URL_CONTAGEM = "http://localhost:5251/contador/secundario"

# Configurando o nome do serviço para o OpenTelemetry
trace.set_tracer_provider(TracerProvider(resource=Resource.create({"service.name": "apiconsumocontagem"})))
tracer_provider = trace.get_tracer_provider()

otlp_exporter = OTLPSpanExporter(endpoint=OTEL_EXPORTER_ENDPOINT, insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

app = FastAPI()

FastAPIInstrumentor.instrument_app(app)

@app.get("/consumir-contador")
def consumir_contador():
    headers = {}
    inject(headers)
    try:
        response = requests.get(API_URL_CONTAGEM, headers=headers)
        response.raise_for_status()
        return JSONResponse(content={
            "contexto": "Python - apiconsumocontagem",
            "apiDotNet": response.json()
        })
    except requests.RequestException as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
