# CurrículoAI

Aplicação web que compara um currículo com uma vaga usando IA generativa. O sistema devolve uma análise estruturada com compatibilidade, competências encontradas, lacunas, melhorias, dicas para entrevista e uma carta de apresentação.

## Categoria do trabalho

**Análise e Insights**, com geração auxiliar de recomendações e carta de apresentação.

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

O projeto começa com `DEMO_MODE=true`, portanto funciona sem chave. A interface identifica o modo no resultado. Para usar a IA real, edite `.env`:

```env
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-3.6-flash
DEMO_MODE=false
```

Nunca envie o arquivo `.env` para o repositório. Ele já está listado no `.gitignore`.

### Variáveis de ambiente

Além das variáveis acima, `REQUEST_TIMEOUT_SECONDS` define o limite da chamada à IA e `ALLOWED_ORIGINS` aceita uma lista de origens externas separadas por vírgula. Deixe `ALLOWED_ORIGINS` vazio quando frontend e API estiverem no mesmo domínio.

## Rotas

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/health` | Verifica se a API está funcionando |
| POST | `/api/analyze` | Analisa currículo e vaga |
| GET | `/docs` | Interface Swagger |

Em produção, a interface e a API são servidas pelo mesmo domínio: [https://curriculoai-projeto.onrender.com/](https://curriculoai-projeto.onrender.com/). O Swagger público fica em [https://curriculoai-projeto.onrender.com/docs](https://curriculoai-projeto.onrender.com/docs) quando o serviço está ativo.

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
- A validação Pydantic confirma o formato e os limites da resposta; ela não comprova a exatidão factual das afirmações da IA.

## Cenários fictícios para demonstração

Use a mesma vaga de desenvolvedor(a) backend com Python, FastAPI, PostgreSQL, APIs REST, Docker e testes automatizados.

| Cenário | Currículo fictício | Evidências esperadas | Lacunas esperadas |
|---|---|---|---|
| Baixa compatibilidade | Ana atua há três anos em atendimento, vendas e rotinas administrativas, sem projetos de software descritos. | Poucas ou nenhuma competência técnica comprovada. | Python, FastAPI, PostgreSQL, APIs REST, Docker e testes. |
| Média compatibilidade | Bruno desenvolveu scripts em Python, criou APIs REST simples e participou de testes, mas não descreve FastAPI, PostgreSQL ou Docker em produção. | Python, APIs REST e testes, com evidências textuais. | FastAPI, PostgreSQL e Docker. |
| Alta compatibilidade | Carla desenvolveu serviços com Python e FastAPI, integrou PostgreSQL, publicou APIs REST em Docker e automatizou testes em projetos reais. | Correspondência ampla com exemplos de projeto e resultado. | Apenas requisitos não mencionados explicitamente na vaga. |

As porcentagens não são fixas: o critério da demonstração é comparar as evidências e as lacunas exibidas.

## Roteiro da banca

1. Visão geral e evolução do Trabalho 1 (2 min).
2. Arquitetura, variáveis de ambiente e deploy (3 min).
3. Demonstração ao vivo pela URL pública, incluindo uma análise (5 min).
4. Segurança, modo demo e casos de erro simulados (3 min).
5. Perguntas (2 min).

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

## Deploy público

O projeto possui configuração para Render em `render.yaml` e um `Dockerfile` para execução reproduzível. Depois do deploy, registre a URL pública nesta seção:

`URL pública: <preencher após o deploy>`

