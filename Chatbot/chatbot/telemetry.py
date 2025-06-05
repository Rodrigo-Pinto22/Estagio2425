import os
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor


def initialize_telemetry():
    # Carregar variáveis de ambiente
    api_key = os.getenv("PHOENIX_API_KEY")
    collector_endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "https://app.phoenix.arize.com")

    if not api_key:
        raise EnvironmentError("PHOENIX_API_KEY não está definido nas variáveis de ambiente.")

    os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={api_key}"
    os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = collector_endpoint

    tracer_provider = register(
        project_name="AssistenteTecnicoMaquinas",
        endpoint=f"{collector_endpoint}/v1/traces",
        set_global_tracer_provider=False
    )

    OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
    print("📡 Telemetria Arize Phoenix inicializada com sucesso.")
