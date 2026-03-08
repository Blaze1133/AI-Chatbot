from fastapi import FastAPI
from app.routes import documents, chat, session
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Document Assistant API",
    description="AI-powered document question answering system",
    version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(session.router)

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*60)
    print("🚀 AI Document Assistant API Starting...")
    print("🔒 Session-based storage enabled - Data clears on restart")
    print("="*60 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    print("\n🔄 AI Document Assistant API Shutting down...")
    print("🗑️  Session data will be cleared automatically")
    print("="*60 + "\n")

@app.get("/")
async def root():
    return {"message": "AI Document Assistant API is running", "session_based": True}
 
@app.get("/health")
async def health_check():
    return {"status": "healthy", "session_storage": True}
