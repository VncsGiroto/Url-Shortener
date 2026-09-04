#!/bin/sh
# Entrypoint do url_shortener: espera o banco aceitar TCP (wait-for-db com
# retry), aplica migrations e sobe o Flask. Falhas saem como diagnostico
# classificado — nunca traceback cru.
set -eu

host="${DB_HOST:-host.docker.internal}"
port="${DB_PORT:-5432}"
name="${DB_NAME:-urlshortener}"
retries="${DB_CONNECT_RETRIES:-30}"
interval="${DB_CONNECT_RETRY_INTERVAL:-2}"

# Imprime só o útil do log de falha do upgrade (sem frames de traceback).
diagnose_db_error() {
    log="$1"
    if grep -qi "password authentication failed" "$log"; then
        echo "Causa: usuario/senha rejeitados pelo Postgres." >&2
        echo "Confira DB_USER/DB_PASSWORD (o compose le de src/.env via env_file)." >&2
    elif grep -qiE "could not connect|connection refused|connection timed out" "$log"; then
        echo "Causa: sem rota ate ${host}:${port}." >&2
        echo "Confira DB_HOST/DB_PORT, listen_addresses e pg_hba do cluster." >&2
    elif grep -qi "pg_hba.conf entry" "$log"; then
        echo "Causa: pg_hba.conf nao autoriza a sub-rede do container." >&2
        echo "Adicione 'host all all 172.16.0.0/12 scram-sha-256' e recarregue." >&2
    elif grep -qi "does not exist" "$log"; then
        echo "Causa: banco ou role '${name}' nao existe no cluster." >&2
        echo "Crie com CREATE USER / CREATE DATABASE no Postgres do WSL." >&2
    else
        echo "Detalhe (ultimas linhas uteis, sem traceback):" >&2
        grep -vE '^[[:space:]]*File "|^[[:space:]]*\^|Traceback \(most recent' "$log" | tail -n 5 >&2
    fi
}

attempt=1
until python3 -c 'import os, socket; socket.create_connection((os.environ.get("DB_HOST", "host.docker.internal"), int(os.environ.get("DB_PORT", "5432"))), timeout=5).close()' 2>/dev/null; do
    if [ "$attempt" -gt "$retries" ]; then
        echo "ERRO: banco inacessivel em ${host}:${port} (db=${name}) apos ${retries} tentativas." >&2
        echo "Verifique: 1) DB_HOST/extra_hosts alcançam o WSL (host-gateway);" >&2
        echo "  2) pg_hba.conf do cluster autoriza a sub-rede do container; 3) listen_addresses expoe a interface;" >&2
        echo "  4) DB_USER/DB_PASSWORD/DB_NAME corretos." >&2
        exit 1
    fi
    echo "Aguardando banco em ${host}:${port} (tentativa ${attempt}/${retries})..."
    attempt=$((attempt + 1))
    sleep "$interval"
done

echo "Banco acessivel em ${host}:${port} - aplicando migrations..."
upgrade_log="$(mktemp)"
if flask --app wsgi db upgrade >"$upgrade_log" 2>&1; then
    rm -f "$upgrade_log"
else
    echo "ERRO: migrations falharam contra ${host}:${port} (db=${name})." >&2
    diagnose_db_error "$upgrade_log"
    rm -f "$upgrade_log"
    exit 1
fi

exec flask --app wsgi run --host=0.0.0.0 --port=8000
