from fastapi import FastAPI

app = FastAPI(title="Chatbot Platform")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
