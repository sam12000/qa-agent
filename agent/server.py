"""import re, time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .a11y import audit
from .inspector import inspect_page
from .report import build_report
from .runner import run_agent


app = FastAPI(title="Agent QA local")
app.add_middleware(CORSMiddleware, allow_origin_regex=r"chrome-extension://.*|extension://.*",
                   allow_methods=["*"], allow_headers=["*"])
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

class Job(BaseModel):
    url: str
    request: str
    title: str = ""
    elements: list[dict] | None = None   # inventaire envoyé par l'extension
    channel: str = "chromium"            # 'chrome' ou 'msedge' possibles


@app.post("/run")
def run(job: Job):
    inv = ({"url": job.url, "title": job.title, "elements": job.elements}
           if job.elements else inspect_page(job.url))
    name = re.sub(r"\W+", "_", job.request.lower())[:40] + f"_{int(time.time())}"
    result = run_agent(job.request, inv, name, job.channel)
    rapport = build_report(result, job.url, audit(job.url))
    return {"passed": result["passed"], "probable_bug": result["probable_bug"],
            "attempts": result["attempts"],
            "report_url": "http://localhost:8765/" + rapport.replace("\\", "/")} """


import logging
import re
import shutil
import time
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .a11y import audit
from .inspector import inspect_page
from .report import build_report
from .runner import run_agent


# --------------------------------------------------
# Configuration
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("agent-qa")

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"

# Créer le dossier des rapports s'il n'existe pas.
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Agent QA local")

# Autoriser les requêtes provenant de l'extension.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"(chrome-extension://.*|extension://.*)",
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exposer les rapports via le serveur FastAPI.
app.mount(
    "/reports",
    StaticFiles(directory=str(REPORTS_DIR)),
    name="reports",
)


# --------------------------------------------------
# Modèle de la requête envoyée par l'extension
# --------------------------------------------------

class Job(BaseModel):
    url: str
    request: str
    title: str = ""
    elements: list[dict] | None = None
    channel: str = "chromium"


# --------------------------------------------------
# Routes de diagnostic
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "status": "ok",
        "service": "Agent QA local",
        "docs": "/docs",
        "run_endpoint": "/run",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Le serveur QA répond.",
    }


# --------------------------------------------------
# Exécution d'un test QA
# --------------------------------------------------

@app.post("/run")
def run(job: Job):
    start_time = time.time()

    logger.info("========== NOUVEAU TEST QA ==========")
    logger.info("URL demandée : %s", job.url)
    logger.info("Demande : %s", job.request)
    logger.info("Navigateur : %s", job.channel)

    try:
        # Étape 1 : récupérer l'inventaire de la page.
        logger.info("[1/4] Inspection de la page")

        if job.elements:
            inv = {
                "url": job.url,
                "title": job.title,
                "elements": job.elements,
            }
        else:
            inv = inspect_page(job.url)

        logger.info("[1/4] Inspection terminée")

        # Étape 2 : générer et exécuter le test.
        name = (
            re.sub(r"\W+", "_", job.request.lower())[:40]
            or "test_qa"
        ) + f"_{int(time.time())}"

        logger.info("[2/4] Exécution de l'agent")

        result = run_agent(
            job.request,
            inv,
            name,
            job.channel,
        )

        logger.info("[2/4] Exécution terminée")

        # Étape 3 : audit d'accessibilité et génération du rapport.
        logger.info("[3/4] Audit d'accessibilité")

        accessibility_result = audit(job.url)

        logger.info("[3/4] Génération du rapport")

        rapport = build_report(
            result,
            job.url,
            accessibility_result,
        )

        logger.info("[3/4] Rapport généré : %s", rapport)

        # Étape 4 : rendre le rapport accessible via /reports.
        report_path = Path(rapport)

        if not report_path.is_absolute():
            report_path = Path.cwd() / report_path

        report_path = report_path.resolve()

        if not report_path.is_file():
            raise FileNotFoundError(
                f"Le fichier de rapport est introuvable : {report_path}"
            )

        try:
            report_path.relative_to(REPORTS_DIR.resolve())
        except ValueError:
            # Si le rapport est ailleurs, le copier dans /reports.
            destination = REPORTS_DIR / report_path.name
            shutil.copy2(report_path, destination)
            report_path = destination.resolve()

        report_url = (
            "http://127.0.0.1:8000/reports/"
            + quote(report_path.name)
        )

        elapsed = round(time.time() - start_time, 2)

        logger.info("[4/4] Test terminé en %s secondes", elapsed)
        logger.info("Rapport accessible : %s", report_url)
        logger.info("========== FIN DU TEST QA ==========")

        # Conserver les principales clés de la réponse initiale.
        return {
            "status": "completed",
            "passed": result.get("passed"),
            "probable_bug": result.get("probable_bug"),
            "attempts": result.get("attempts"),
            "report_url": report_url,
            "duration_seconds": elapsed,
        }

    except Exception as exc:
        logger.exception("Échec du traitement QA")

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Le traitement QA a échoué.",
                "error": str(exc),
                "url": job.url,
            },
        ) from exc

