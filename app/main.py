
from fastapi import FastAPI

app = FastAPI(
    title="Automated Multi-Platform Posting API",
    description="Publish messages across multiple platforms through a single API.",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "application": "automated-posting"
    }
