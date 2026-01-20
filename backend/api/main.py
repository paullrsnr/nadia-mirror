from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Nadia API")

# Pour plus tard, quand on aura des routes à inclure
# app.include_router(auth_router.router, prefix="/auth")
# app.include_router(emails_router.router, prefix="/emails")
# app.include_router(llm_router.router, prefix="/llm")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/hello")
def hello():
    return {"message": "hello"}