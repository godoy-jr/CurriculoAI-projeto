from fastapi.testclient import TestClient

from app.main import app
from app.services import AIServiceError

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_rejects_short_input():
    response = client.post("/api/analyze", json={"candidate_name": "Ana", "resume": "curto", "job_description": "curta"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Dados inválidos."


def test_demo_analysis(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "true")
    payload = {
        "candidate_name": "Ana Lima",
        "resume": "Desenvolvedora Python com experiência em FastAPI, SQL, APIs REST, testes automatizados e Git em projetos de tecnologia.",
        "job_description": "Buscamos pessoa desenvolvedora com domínio de Python, FastAPI, SQL, APIs REST, Git, Docker e testes para criar serviços escaláveis.",
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["match_score"] <= 100
    assert body["mode"] == "demo"
    assert isinstance(body["matching_skills"], list)


def test_demo_score_is_zero_without_matching_terms(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "true")
    payload = {
        "candidate_name": "Chico",
        "resume": "Sou cozinheiro com ampla trajetória na área de alimentação e gestão de restaurantes.",
        "job_description": "Buscamos engenheiro de software com Python, JavaScript, Kubernetes, APIs, banco de dados e segurança digital.",
    }
    response = client.post("/api/analyze", json=payload)

    assert response.status_code == 200
    assert response.json()["match_score"] == 0


def test_demo_competencies_exclude_generic_job_language(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "true")
    payload = {
        "candidate_name": "Chico",
        "resume": "Sou analista financeiro e trabalhei com conciliação bancária e Excel avançado em relatórios mensais para controladoria.",
        "job_description": (
            "Estamos procurando uma pessoa desenvolvedora backend para trabalhar na construção de APIs e serviços escaláveis. "
            "A vaga exige experiência com Python, FastAPI, APIs REST, PostgreSQL, Git, testes automatizados e metodologias ágeis. "
            "Conhecimentos em Docker, AWS, integração contínua e arquitetura de microsserviços serão considerados diferenciais. "
            "A pessoa deverá colaborar com a equipe, participar de revisões de código e documentar as soluções desenvolvidas."
        ),
    }
    response = client.post("/api/analyze", json=payload)

    assert response.status_code == 200
    body = response.json()
    missing_names = {skill["skill"].lower() for skill in body["missing_skills"]}
    assert missing_names.isdisjoint({"estamos", "procurando", "pessoa", "desenvolvedora"})
    assert missing_names.isdisjoint({"escaláveis", "escaláveis."})
    assert "apis" in missing_names
    assert missing_names.intersection({"back-end", "python", "fastapi", "rest"})
    assert all("projeto" in skill["suggestion"] for skill in body["missing_skills"])
    assert all("não declare domínio" in skill["suggestion"] for skill in body["missing_skills"])


def test_rate_limit_returns_429(monkeypatch):
    async def rate_limited(_):
        raise AIServiceError("Limite de requisições atingido.", status_code=429)

    monkeypatch.setattr("app.main.analyze", rate_limited)
    payload = {
        "candidate_name": "Ana Lima",
        "resume": "Desenvolvedora Python com experiência em FastAPI, SQL, APIs REST, testes automatizados e Git em projetos de tecnologia.",
        "job_description": "Buscamos pessoa desenvolvedora com domínio de Python, FastAPI, SQL, APIs REST, Git, Docker e testes para criar serviços escaláveis.",
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 429
    assert "Limite de requisições" in response.json()["detail"]


def test_timeout_returns_503(monkeypatch):
    async def timed_out(_):
        raise AIServiceError("A IA demorou demais para responder. Tente novamente.")

    monkeypatch.setattr("app.main.analyze", timed_out)
    response = client.post("/api/analyze", json={
        "candidate_name": "Ana Lima",
        "resume": "Desenvolvedora Python com experiência em FastAPI, SQL, APIs REST, testes automatizados e Git em projetos de tecnologia.",
        "job_description": "Buscamos pessoa desenvolvedora com domínio de Python, FastAPI, SQL, APIs REST, Git, Docker e testes para criar serviços escaláveis.",
    })
    assert response.status_code == 503
    assert "demorou demais" in response.json()["detail"]


def test_provider_auth_failure_is_safe_and_diagnostic(caplog):
    import httpx
    from app.services import _provider_failure

    error = _provider_failure(
        httpx.Response(403, json={"error": {"status": "PERMISSION_DENIED", "message": "secret"}}),
        "gemini-3.6-flash",
    )
    assert error.status_code == 503
    assert "chave" in str(error)
    assert "secret" not in caplog.text
    assert "permission" in caplog.text


def test_provider_model_failure_is_safe(caplog):
    import httpx
    from app.services import _provider_failure

    error = _provider_failure(httpx.Response(404, json={"error": {"status": "NOT_FOUND"}}), "invalid-model")
    assert error.status_code == 503
    assert "GEMINI_MODEL" in str(error)
    assert "model_not_found" in caplog.text


def test_provider_invalid_request_is_safe(caplog):
    import httpx
    from app.services import _provider_failure

    error = _provider_failure(httpx.Response(400, json={"error": {"status": "INVALID_ARGUMENT"}}), "gemini-3.6-flash")
    assert error.status_code == 503
    assert "formato" in str(error)
    assert "invalid_request" in caplog.text


def test_invalid_ai_response_returns_503(monkeypatch):
    async def invalid_response(_):
        raise AIServiceError("A IA retornou uma resposta em formato inválido.")

    monkeypatch.setattr("app.main.analyze", invalid_response)
    response = client.post("/api/analyze", json={
        "candidate_name": "Ana Lima",
        "resume": "Desenvolvedora Python com experiência em FastAPI, SQL, APIs REST, testes automatizados e Git em projetos de tecnologia.",
        "job_description": "Buscamos pessoa desenvolvedora com domínio de Python, FastAPI, SQL, APIs REST, Git, Docker e testes para criar serviços escaláveis.",
    })
    assert response.status_code == 503
    assert "formato inválido" in response.json()["detail"]

