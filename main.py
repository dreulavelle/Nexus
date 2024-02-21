import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.home import base
from routers.search import search
from utils.settings import settings

app = FastAPI(
    title="Nexus",
    version=settings.version,
    description="On Demand Cache Real-Debrid Indexer",
    docs_url="/docs",
    contact={"name": "Nexus", "url": "https://github.com/Pukabyte/Nexus"},
)

app.include_router(base)
app.include_router(search)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8978)
