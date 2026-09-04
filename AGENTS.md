# AGENTS.md

## Stack
- Flask factory (`src/__init__.py:8` `create_app`, `wsgi.py:1` `app = create_app()`). Python 3.14 venv at repo root (`pyvenv.cfg:3`) vs Docker `python:3.11-slim`.
- `src/config.py:7` (`BaseConfig`/`DevelopmentConfig`/`TestingConfig`/`ProductionConfig` com `SQLALCHEMY_DATABASE_URI` + `SQLALCHEMY_ENGINE_OPTIONS` `pool_size`/`max_overflow`/`pool_pre_ping`; `load_dotenv` aponta para `src/.env`, env do compose/shell prevalece), `src/extensions.py:1` (`db = SQLAlchemy()`, `migrate = Migrate()`, `limiter = Limiter(...)` com defaults `200/day`+`50/hour`), `requirements.txt:1` (`Flask==3.1.0`, `Flask-SQLAlchemy==3.1.1`, `Flask-Migrate==4.1.0`, `SQLAlchemy==2.0.52`, `psycopg2-binary==2.9.12`, `python-dotenv==1.2.3`, `Flask-Limiter==4.1.1`). `migrations/` gerado por `flask db init`.
- `Scripts/`, `Lib/`, `Include/`, `pyvenv.cfg` — Windows venv at repo root (gitignored, not portable to WSL/Linux).

## Structure
- `wsgi.py:1` — entrypoint (`app = create_app()`). `src/__init__.py:8` defines `create_app()` (resolve `config_by_name`, `from_object`, `db.init_app` + `migrate.init_app`, `import src.urls.models` para registrar `Url` no `metadata`, registers `src/urls/routes.py:5` `urls_bp`).
- `src/urls/routes.py:5` `urls_bp` (`POST /urls/shorten` `shorten_url:10` com `@limiter.limit("10 per minute")`, `GET /<short_code>` `resolve_short_url:17` com `redirect`). 429 sai no envelope `HttpResponse` via `errorhandler` na factory.
- `src/urls/controller.py:7` `UrlController.create_url`/`resolve_url`, `src/urls/services.py:1` `UrlService.create`/`resolve`/`_generate_code`, `src/urls/repository.py:4` `UrlRepository.save`/`get_by_code` via `db.session`, `src/urls/models.py:1` `Url(db.Model)`, `src/common/http.py:2` `HttpResponse.success`/`error`.
- `migrations/` — `alembic.ini`, `env.py`, `script.py.mako`, `versions/1a2cabaf6c51_create_urls.py` (`op.create_table('urls')`). Gerado via `flask --app wsgi db migrate`.
- `Dockerfile:12` `COPY src/ ./src/` + `COPY wsgi.py ./` + `COPY migrations/ ./migrations/` + `COPY docker_entrypoint.sh ./` com `ENTRYPOINT` (wait-for-db com retry via socket stdlib + `flask db upgrade` + `flask run`), `compose.yaml:1` só `  url_shortener` (`build: .`) contra o PG 18 nativo do WSL (cluster `18/main`, porta `5432`, `host-gateway` → `172.17.0.1` estável); credenciais via `env_file: src/.env`, `DB_HOST`/`DB_PORT`/`FLASK_ENV=production` em `environment` (precedem o env_file; app monta a URI das partes, sem `DATABASE_URL` fixa); `requirements.txt` only at root. `src/.env` holds `DB_*` local (`DB_HOST=localhost`, `DB_PORT=5432` = PG 18 do WSL, gitignored via `.dockerignore:14`, not via `.gitignore`).

## Naming Conventions
Regra geral: `snake_case` para arquivos/pastas/módulos e variáveis/funções; `PascalCase` para classes; `SCREAMING_SNAKE` para env vars. Sem prefixo redundante quando a pasta já dá contexto (`urls/` já implica `url_`).

| Pasta/Arquivo | Define | Classe/Variável/Função | Regra / SOLID |
|---|---|---|---|
| `wsgi.py` | entrypoint | `app = create_app()` | padrão Flask `wsgi` — S, D |
| `src/__init__.py` | factory | `create_app(config_name)` | S: criação isolada; D: injeta config/extensões |
| `src/config.py` | config | `BaseConfig`, `DevelopmentConfig`, `TestingConfig`, `SQLALCHEMY_DATABASE_URI`, `SQLALCHEMY_ENGINE_OPTIONS` | S: só config |
| `src/extensions.py` | extensões | `db = SQLAlchemy()`, `migrate = Migrate()` | D, O: fechado para modificação, aberto para novas extensões |
| `src/common/http.py` | http | `HttpResponse.success`/`error` | I: evita `utils` genérico catch-all |
| `src/urls/` | feature | — | plural, coeso por domínio (S, O: novo `auth/` sem tocar `urls/`) |
| `src/urls/routes.py` | routes | `urls_bp = Blueprint('urls')`, `shorten_url`, `resolve_short_url` | S: Flask usa `routes`/`blueprints`, não `router` |
| `src/urls/controller.py` | controller | `UrlController.create_url`, `resolve_url` | S: só orquestra; L: compat via alias |
| `src/urls/repository.py` | repository | `UrlRepository.save`, `get_by_code` | S, I: interface pequena |
| `src/urls/models.py` | model | `Url(db.Model)` | S: entidade singular |
| `migrations/` | migrations | `alembic.ini`, `env.py`, `versions/*.py` | S: só DDL versionado; O: nova migration sem tocar código |

Transversais: Blueprint `*_bp` (`urls_bp`), pastas plural para coleções (`urls`, `common`), imports absolutos `from src.*` (nunca `from app.*`), arquivos `snake_case` sem `DB` maiúsculo ou `CamelCase`.

## Commands
- Activate venv: `source Scripts/activate` (bash) or `Scripts/activate.bat` / `Activate.ps1` on Windows — `Scripts/python.exe` is Windows binary, won't run in WSL.
- Run dev: `python -m flask --app wsgi run` (ou `python wsgi.py`). `pip install -r requirements.txt` needed after fresh clone. `FLASK_ENV=testing` uses `TestingConfig` (`sqlite:///:memory:` via `db.create_all()` sem Postgres).
- Flask-Migrate: `flask --app wsgi db init` (já feito), `flask --app wsgi db migrate -m "msg"` (gera `migrations/versions/*.py`), `flask --app wsgi db upgrade` (aplica), `flask --app wsgi db downgrade`, `flask --app wsgi db current/history`.
- Docker: `docker compose up --build` (sobe só `url_shortener` contra o PG 18 nativo do WSL via `host-gateway:5432`). Pré-requisitos no WSL (com `sudo`): `listen_addresses = '*'` em `/etc/postgresql/18/main/postgresql.conf`, `host all all 172.16.0.0/12 scram-sha-256` no `pg_hba.conf` (cobre `172.17.0.0/16` da bridge `docker0` + `172.18.0.0/16` das redes do compose), `sudo pg_ctlcluster 18 main restart`, banco+role criados. Passe `DB_USER`/`DB_PASSWORD` reais no ambiente.
- No tests, lint, formatter, or CI — nothing to run.

## Gotchas
- `docker.sock` permission: `docker build` fails com `permission denied` até `newgrp docker` ou relogin (user no grupo `docker` mas não ativo).
- `.gitignore` tem CRLF — diffs mostram `^M` noise.
- `src/.env` contém segredos — ignorado via `.dockerignore:14` mas rastreável por git (adicionar a `.gitignore` se necessário).
- Sem `postgres` no compose — app usa o PG 18 nativo do WSL (`host-gateway` = `172.17.0.1` de dentro do container, `127.0.0.1:5432` de dentro do WSL). PG 17 do Windows (`localhost:5433`) segue independente, fora do caminho do app.
- `flask db upgrade` é idempotente (só aplica `alembic_version` pendente). Não usar `down -v` em prod.
- `SimpleConnectionPool` removido — `SQLALCHEMY_ENGINE_OPTIONS` (`pool_size`/`max_overflow`/`pool_pre_ping`) substitui `DB_MIN_CONN`/`DB_MAX_CONN`.

## Workflow
- Global `~/.config/opencode/AGENTS.md` applies: plan mode mandatory (enumerated plan + SOLID mapping), save large plans to `.opencode/plans/*.md`, await confirmation before coding, apply SOLID pragmatically, ask instead of guessing on missing business context.
