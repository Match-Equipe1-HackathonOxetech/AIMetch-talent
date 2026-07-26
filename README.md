# API de recrutamento por softskills

API Flask para uma plataforma de recrutamento que avalia softskills através de
uma entrevista conversacional com IA (Gemini). Construída em **arquitetura
hexagonal (ports & adapters)** para que a mesma lógica de entrevista possa,
no futuro, ser consumida por site, bot do Telegram e bot do WhatsApp sem
duplicar regra de negócio.

## Estrutura

```
app/
  domain/                     núcleo — sem Flask, Gemini ou ORM
    entities.py                Empresa, Candidato, Vaga, Entrevista, Resultado...
    value_objects.py           Memoria, ResultadoIA, ResumoIA
    exceptions.py               erros de negócio (traduzidos em HTTP pelos adapters)
    services/
      entrevista_service.py     iniciar_entrevista() / responder() / obter_estado() / gerar_resultado()
      auth_service.py           registrar / login / refresh / logout
      vaga_service.py           criar_vaga / listar_resultados

  ports/                       interfaces que o domínio depende
    llm_port.py                 LLMPort — implementada pelo GeminiAdapter
    repositories.py             *Repository — implementadas pelos Sql*Repository
    security_ports.py           PasswordHasherPort, TokenServicePort

  adapters/
    inbound/http/               tradução HTTP <-> services (rotas Flask, schemas, decorators)
    outbound/
      llm/gemini_adapter.py      único lugar que conhece a API do Gemini
      persistence/                modelos SQLAlchemy + repositórios concretos
      security/                   hash de senha (Werkzeug) e JWT (PyJWT)

  config.py / extensions.py / __init__.py   composition root (app factory)

tests/
  fakes.py                      FakeLLMPort + repositórios em memória
  test_entrevista_service.py    testa o domínio sem Flask, sem banco, sem rede
```

## Por que "channel-agnostic"

`EntrevistaService` (em `app/domain/services/entrevista_service.py`) só
depende de portas (`LLMPort`, `*Repository`) — nunca de Flask, de um objeto
`request` ou de qualquer coisa HTTP. As rotas em
`app/adapters/inbound/http/entrevista_routes.py` são só tradução: pegam JSON
do `request`, chamam um método do service, devolvem `jsonify`.

Isso significa que um handler de bot do Telegram ou WhatsApp (um novo adapter
de entrada, em `app/adapters/inbound/telegram/` ou `.../whatsapp/`, por
exemplo) chamaria exatamente os mesmos métodos —
`entrevista_service.iniciar_entrevista(...)`,
`entrevista_service.responder(...)`, `entrevista_service.obter_estado(...)` —
sem duplicar nenhuma regra de negócio. O `GET /entrevistas/{id}` existe
justamente para esse cenário: um bot que reinicia no meio de uma conversa usa
esse endpoint (ou, no caso de um adapter direto, o método
`obter_estado()`) para reconstruir em que ponto da entrevista o candidato
estava.

## Setup

```bash
cp .env.example .env
# edite .env e preencha GEMINI_API_KEY e JWT_SECRET

pip install -r requirements.txt
python run.py
```

Por padrão usa SQLite (`recrutamento.db`, criado automaticamente). Para usar
Postgres, ajuste `DATABASE_URL` no `.env` (o driver `psycopg2-binary` já está
no `requirements.txt`) — veja a seção abaixo.

## Trocando SQLite por Postgres

1. Suba um Postgres (local, Docker ou serviço gerenciado) e crie o banco:
   ```bash
   createdb recrutamento
   # ou, com Docker:
   docker run --name recrutamento-db -e POSTGRES_PASSWORD=senha \
     -e POSTGRES_DB=recrutamento -p 5432:5432 -d postgres:16
   ```
2. No `.env`, aponte `DATABASE_URL` para o Postgres:
   ```
   DATABASE_URL=postgresql://usuario:senha@localhost:5432/recrutamento
   ```
3. `pip install -r requirements.txt` (já inclui `psycopg2-binary`).
4. Rode a aplicação normalmente (`python run.py`) — `db.create_all()` cria as
   tabelas no Postgres na primeira execução, do mesmo jeito que fazia no
   SQLite. Nada no código muda: `config.py` já lê `DATABASE_URL` do
   ambiente, e os modelos (`app/adapters/outbound/persistence/models.py`) só
   usam tipos padrão do SQLAlchemy (`String`, `Text`, `JSON`, `DateTime`,
   `Boolean`), todos suportados nativamente pelo Postgres.

Se o projeto crescer, vale trocar o `db.create_all()` por migrações com
Flask-Migrate/Alembic — em produção isso evita recriar/alterar tabelas
silenciosamente a cada deploy.

## Rodando os testes

```bash
pytest
```

Os testes cobrem só o domínio (`EntrevistaService`), usando um
`FakeLLMPort` que devolve respostas fixas e determinísticas e repositórios em
memória — nenhum teste chama o Gemini de verdade nem depende de rede ou
banco.

## Endpoints

| Método | Rota | Role | Descrição |
|---|---|---|---|
| POST | `/empresas` | — | cria conta de empresa |
| POST | `/candidatos` | — | cria conta de candidato |
| POST | `/login` | — | retorna `access_token` + `refresh_token` |
| POST | `/refresh` | — | rotaciona o `refresh_token` e emite novo `access_token` |
| POST | `/logout` | — | revoga o `refresh_token` |
| POST | `/vagas` | recrutador | cria vaga com `softskills_alvo` |
| GET | `/vagas/{vaga_id}/resultados` | recrutador (dono) | lista resultados dos candidatos da vaga |
| POST | `/entrevistas` | recrutado | inicia entrevista, retorna `entrevista_id` + primeira pergunta |
| POST | `/entrevistas/{id}/respostas` | recrutado (dono) | envia resposta, retorna próxima pergunta ou conclusão |
| GET | `/entrevistas/{id}` | recrutado (dono) | estado atual (memória, softskills avaliadas) |
| POST | `/entrevistas/{id}/resultado` | autenticado (dono ou recrutador da vaga) | gera/retorna resultado consolidado |

Autenticação via header `Authorization: Bearer <access_token>`.

## Banco de perguntas-modelo

`PerguntaTemplateRepository.buscar_por_softskill(softskill)` busca o modelo
de pergunta cadastrado para a softskill em foco — popule a tabela
`perguntas_template` com pelo menos uma linha por softskill que suas vagas
possam usar (ex.: `comunicacao`, `trabalho_em_equipe`, `lideranca`...), senão
`GeminiAdapter` recebe `pergunta_template=None` e monta a pergunta livremente.
