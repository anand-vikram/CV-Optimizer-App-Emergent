"""End-to-end backend tests for CV Optimizer / ATS Enhancer."""
import os
import io
import time
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://resume-optimizer-382.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

SAMPLE_CV_TEXT = """John Doe
Senior Software Engineer
john.doe@example.com | +1-415-555-0123 | San Francisco, CA | linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Senior software engineer with 8+ years of experience building scalable backend systems
and data platforms. Expert in Python, distributed systems, and cloud infrastructure on
AWS. Led teams of 5+ engineers and shipped products serving millions of users.

EXPERIENCE
Acme Corp — Senior Software Engineer (2021 - Present)
- Designed and built microservices in Python (FastAPI) and Go serving 50M+ daily requests.
- Migrated legacy monolith to Kubernetes on AWS EKS, reducing deploys from 2h to 8m.
- Mentored 6 junior engineers; led code review culture; improved test coverage from 45% to 92%.

Globex — Software Engineer (2017 - 2021)
- Built event-driven data pipelines using Kafka, Spark and Airflow processing 5TB/day.
- Implemented CI/CD with Github Actions, Terraform, and Docker; cut release cycle by 70%.

SKILLS
Python, Go, FastAPI, Django, PostgreSQL, MongoDB, Redis, Kafka, Spark, Airflow,
Docker, Kubernetes, AWS (EKS, S3, Lambda, RDS), Terraform, Github Actions, REST, gRPC.

EDUCATION
B.S. Computer Science — University of California, Berkeley (2013 - 2017)

CERTIFICATIONS
AWS Certified Solutions Architect — Associate (2022)
"""

JOB_DESCRIPTION = """We are looking for a Senior Backend Engineer to join our Platform team at Initech.
You will design, build and operate highly scalable services in Python and Go on AWS.

Responsibilities:
- Architect and develop microservices (FastAPI/gRPC) handling tens of millions of requests per day.
- Build robust data pipelines using Kafka, Spark, and Airflow.
- Drive infrastructure-as-code with Terraform on AWS (EKS, Lambda, RDS, S3, DynamoDB).
- Mentor engineers, lead design reviews, and champion best practices in testing and observability.
- Collaborate with Product to translate business needs into reliable software.

Requirements:
- 6+ years of backend engineering experience.
- Strong Python and one of Go/Java/Rust.
- Proven experience with Kubernetes, Docker, CI/CD (Github Actions / Jenkins).
- Deep knowledge of PostgreSQL, Redis, and at least one NoSQL store (MongoDB/DynamoDB).
- Experience with distributed systems patterns, event-driven architectures, and observability (Prometheus, Grafana, OpenTelemetry).
- Excellent communication skills and a track record of mentorship.

Nice to have: experience with LLMs, vector databases, and GraphQL.
"""


# ---------- Fixtures ----------

@pytest.fixture(scope="session")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def user_creds():
    suffix = uuid.uuid4().hex[:8]
    return {
        "name": "Test User",
        "email": f"TEST_user_{suffix}@example.com",
        "password": "TestPass123!",
    }


@pytest.fixture(scope="session")
def auth(session, user_creds):
    """Register and return token + user."""
    r = session.post(f"{API}/auth/register", json=user_creds, timeout=30)
    assert r.status_code == 200, f"register failed: {r.status_code} {r.text}"
    data = r.json()
    assert "token" in data and "user" in data
    assert data["user"]["email"] == user_creds["email"].lower()
    return data


@pytest.fixture(scope="session")
def auth_headers(auth):
    return {"Authorization": f"Bearer {auth['token']}", "Content-Type": "application/json"}


# ---------- Auth tests ----------

class TestAuth:
    def test_register_duplicate(self, auth, session, user_creds):
        r = session.post(f"{API}/auth/register", json=user_creds, timeout=15)
        assert r.status_code == 409

    def test_login_success(self, session, user_creds):
        r = session.post(f"{API}/auth/login",
                         json={"email": user_creds["email"], "password": user_creds["password"]},
                         timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert "token" in data
        assert data["user"]["email"] == user_creds["email"].lower()

    def test_login_bad_password(self, session, user_creds):
        r = session.post(f"{API}/auth/login",
                         json={"email": user_creds["email"], "password": "WrongPass!"},
                         timeout=15)
        assert r.status_code == 401

    def test_me_with_token(self, auth_headers, user_creds):
        r = requests.get(f"{API}/auth/me", headers=auth_headers, timeout=15)
        assert r.status_code == 200
        assert r.json()["email"] == user_creds["email"].lower()

    def test_me_without_token(self):
        r = requests.get(f"{API}/auth/me", timeout=15)
        assert r.status_code == 401

    def test_protected_routes_require_auth(self):
        for path in ["/analyses", "/cv/list"]:
            r = requests.get(f"{API}{path}", timeout=15)
            assert r.status_code == 401, f"{path} should be 401, got {r.status_code}"


# ---------- CV Upload ----------

class TestCVUpload:
    def test_upload_txt_cv(self, auth, request):
        headers = {"Authorization": f"Bearer {auth['token']}"}
        files = {"file": ("sample_cv.txt", io.BytesIO(SAMPLE_CV_TEXT.encode("utf-8")), "text/plain")}
        r = requests.post(f"{API}/cv/upload", headers=headers, files=files, timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "id" in data and data["filename"] == "sample_cv.txt"
        assert data["text_length"] >= 800
        # stash for later tests
        request.config.cache.set("cv_id", data["id"])

    def test_upload_requires_auth(self):
        files = {"file": ("x.txt", io.BytesIO(b"hello world"), "text/plain")}
        r = requests.post(f"{API}/cv/upload", files=files, timeout=15)
        assert r.status_code == 401

    def test_upload_too_short(self, auth):
        headers = {"Authorization": f"Bearer {auth['token']}"}
        files = {"file": ("tiny.txt", io.BytesIO(b"hi"), "text/plain")}
        r = requests.post(f"{API}/cv/upload", headers=headers, files=files, timeout=15)
        assert r.status_code == 400

    def test_cv_list(self, auth_headers):
        r = requests.get(f"{API}/cv/list", headers=auth_headers, timeout=15)
        assert r.status_code == 200
        lst = r.json()
        assert isinstance(lst, list) and len(lst) >= 1


# ---------- Analyze ----------

class TestAnalyze:
    def test_analyze_runs(self, auth_headers, request):
        cv_id = request.config.cache.get("cv_id", None)
        assert cv_id, "cv_id missing"
        payload = {
            "cv_id": cv_id,
            "job_title": "Senior Backend Engineer",
            "company": "Initech",
            "job_description": JOB_DESCRIPTION,
        }
        r = requests.post(f"{API}/analyze", headers=auth_headers, json=payload, timeout=90)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "id" in data
        assert 0 <= data["ats_score"] <= 100
        assert isinstance(data["score_breakdown"], dict)
        assert isinstance(data["matched_keywords"], list)
        assert isinstance(data["missing_keywords"], list)
        assert isinstance(data["gaps"], list)
        assert isinstance(data["strengths"], list)
        assert isinstance(data["section_suggestions"], dict)
        assert isinstance(data["overall_recommendation"], str) and len(data["overall_recommendation"]) > 0
        # Confirm at least some matched keywords (model usually picks Python/AWS/Kafka etc.)
        assert len(data["matched_keywords"]) >= 1
        request.config.cache.set("analysis_id", data["id"])

    def test_list_analyses(self, auth_headers, request):
        r = requests.get(f"{API}/analyses", headers=auth_headers, timeout=15)
        assert r.status_code == 200
        lst = r.json()
        assert isinstance(lst, list) and len(lst) >= 1
        analysis_id = request.config.cache.get("analysis_id", None)
        assert any(a["id"] == analysis_id for a in lst)

    def test_get_analysis(self, auth_headers, request):
        analysis_id = request.config.cache.get("analysis_id", None)
        r = requests.get(f"{API}/analyses/{analysis_id}", headers=auth_headers, timeout=15)
        assert r.status_code == 200
        a = r.json()
        assert a["id"] == analysis_id
        assert "job_description" in a  # full record


# ---------- Optimize + Downloads ----------

class TestOptimizeAndDownload:
    def test_optimize_runs(self, auth_headers, request):
        analysis_id = request.config.cache.get("analysis_id", None)
        assert analysis_id, "analysis_id missing"
        r = requests.post(f"{API}/optimize", headers=auth_headers,
                          json={"analysis_id": analysis_id}, timeout=150)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["analysis_id"] == analysis_id
        sc = data["structured_cv"]
        assert isinstance(sc, dict)
        for key in ["full_name", "headline", "contact", "professional_summary",
                    "core_skills", "experience", "education", "certifications", "projects"]:
            assert key in sc, f"missing key {key} in structured_cv"
        assert isinstance(sc["experience"], list)
        assert isinstance(data["cover_letter"], str) and len(data["cover_letter"]) > 100
        request.config.cache.set("opt_id", data["id"])

    def test_download_cv_pdf_header_auth(self, auth, request):
        opt_id = request.config.cache.get("opt_id", None)
        headers = {"Authorization": f"Bearer {auth['token']}"}
        r = requests.get(f"{API}/optimized/{opt_id}/download",
                         params={"kind": "cv", "fmt": "pdf"},
                         headers=headers, timeout=30)
        assert r.status_code == 200, r.text
        assert "application/pdf" in r.headers.get("content-type", "")
        assert r.content[:4] == b"%PDF"
        assert len(r.content) > 1024

    def test_download_cv_docx_query_token(self, auth, request):
        opt_id = request.config.cache.get("opt_id", None)
        r = requests.get(f"{API}/optimized/{opt_id}/download",
                         params={"kind": "cv", "fmt": "docx", "token": auth["token"]},
                         timeout=30)
        assert r.status_code == 200, r.text
        ct = r.headers.get("content-type", "")
        assert "officedocument.wordprocessingml.document" in ct
        # DOCX is a ZIP -> starts with PK
        assert r.content[:2] == b"PK"
        assert len(r.content) > 1024

    def test_download_cover_pdf(self, auth, request):
        opt_id = request.config.cache.get("opt_id", None)
        headers = {"Authorization": f"Bearer {auth['token']}"}
        r = requests.get(f"{API}/optimized/{opt_id}/download",
                         params={"kind": "cover_letter", "fmt": "pdf"},
                         headers=headers, timeout=30)
        assert r.status_code == 200, r.text
        assert r.content[:4] == b"%PDF"
        assert len(r.content) > 1024

    def test_download_cover_docx(self, auth, request):
        opt_id = request.config.cache.get("opt_id", None)
        headers = {"Authorization": f"Bearer {auth['token']}"}
        r = requests.get(f"{API}/optimized/{opt_id}/download",
                         params={"kind": "cover_letter", "fmt": "docx"},
                         headers=headers, timeout=30)
        assert r.status_code == 200, r.text
        assert r.content[:2] == b"PK"
        assert len(r.content) > 1024

    def test_download_requires_token(self, request):
        opt_id = request.config.cache.get("opt_id", None)
        r = requests.get(f"{API}/optimized/{opt_id}/download",
                         params={"kind": "cv", "fmt": "pdf"}, timeout=15)
        assert r.status_code == 401

    def test_download_invalid_kind(self, auth, request):
        opt_id = request.config.cache.get("opt_id", None)
        headers = {"Authorization": f"Bearer {auth['token']}"}
        r = requests.get(f"{API}/optimized/{opt_id}/download",
                         params={"kind": "bogus", "fmt": "pdf"},
                         headers=headers, timeout=15)
        assert r.status_code == 400
