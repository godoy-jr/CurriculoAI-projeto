# CurrículoAI

Aplicação web que compara um currículo com uma vaga usando IA generativa. O sistema devolve uma análise estruturada com compatibilidade, competências encontradas, lacunas, melhorias, dicas para entrevista e uma carta de apresentação.

## Categoria do trabalho

**Classificação / Análise** e **Geração de Conteúdo**.

## Tecnologias

- Python e FastAPI
- Gemini API via HTTP
- HTML, CSS e JavaScript sem framework
- Pydantic para validação e parsing do JSON

## Como executar

Requer Python 3.11 ou superior.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Acesse `http://127.0.0.1:8000`. A documentação Swagger fica em `http://127.0.0.1:8000/docs`.

O projeto começa com `DEMO_MODE=true`, portanto funciona sem chave. Para usar a IA real, edite `.env`:

```env
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-3.6-flash
DEMO_MODE=false
```

Nunca envie o arquivo `.env` para o repositório. Ele já está listado no `.gitignore`.

## Rotas

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/health` | Verifica se a API está funcionando |
| POST | `/api/analyze` | Analisa currículo e vaga |
| GET | `/docs` | Interface Swagger |

### Exemplo de requisição

```json
{
  "candidate_name": "Marina Silva",
  "resume": "Texto do currículo com no mínimo 80 caracteres...",
  "job_description": "Descrição da vaga com no mínimo 80 caracteres..."
}
```

## Segurança e confiabilidade

- Chave armazenada somente em variável de ambiente.
- Limites de tamanho e validação contra campos vazios.
- Prompt separa instruções dos dados para reduzir prompt injection.
- Atributos pessoais sensíveis não podem afetar a avaliação.
- Temperatura baixa e esquema Pydantic reduzem respostas inconsistentes.
- Tratamento de timeout, rate limit, indisponibilidade e JSON inválido.
- Mensagens HTTP legíveis: `400` para entrada inválida, `429` para limite de requisições e `503` para indisponibilidade da IA.
- A análise é orientativa e não substitui uma decisão humana.

## Executar testes

```bash
pip install pytest
pytest -q
```

## Estrutura

```text
app/
  main.py       # rotas e tratamento HTTP
  schemas.py    # contratos de entrada e saída
  services.py   # prompt, integração Gemini e modo demo
  static/       # interface web
tests/          # testes da API
```

## Demonstração sugerida

1. Mostrar o formulário e a documentação Swagger.
2. Enviar currículo e vaga compatíveis.
3. Explicar o score, evidências e competências ausentes.
4. Enviar um campo vazio para demonstrar o erro 400.
5. Desativar a conexão/chave para demonstrar uma falha 503 compreensível.

