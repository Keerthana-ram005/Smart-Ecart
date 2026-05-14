from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import analyze

app = FastAPI(title="Smart-eCart Analyzer API")

# Enable CORS for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(analyze.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart-eCart Analyzer API"}
