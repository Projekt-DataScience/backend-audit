import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from routes.lpa_question_category import router as lpa_question_category_router
from routes.lpa_question import router as lpa_question_router
from routes.lpa_audit import router as lpa_audit_router
from routes.audit_answers import router as lpa_answer_router
from routes.recurrence import router as recurrence_router
from routes.analytics import router as analytics_router


from settings import settings


app = FastAPI(docs_url="/api/audit/docs", redoc_url="/api/audit/redoc",
              openapi_url="/api/audit/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lpa_question_category_router)
app.include_router(lpa_question_router)
app.include_router(lpa_audit_router)
app.include_router(lpa_answer_router)
app.include_router(recurrence_router)
app.include_router(analytics_router)

client = TestClient(app)


@app.get("/api/audit/")
@app.get("/api/audit/healthcheck")
def healthcheck():
    return {"Status": "Up"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
