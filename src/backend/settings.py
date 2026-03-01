import os
from pathlib import Path


BACKEND_PORT = int(os.getenv("BACKEND_PORT") or "8000")

CV_URL = (
    "https://raw.githubusercontent.com/scopreon/CV/main"
    "/rendercv_output/Saul_Cooperman_CV.pdf"
)
CV_PATH = Path(os.getenv("CV_PATH", "/tmp/Saul_Cooperman_CV.pdf"))
CV_SYNC_INTERVAL = int(os.getenv("CV_SYNC_INTERVAL", "300"))
