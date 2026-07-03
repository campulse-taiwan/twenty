#!/usr/bin/env sh
# Verify a deployed Twenty instance (e.g. on Zeabur).
# Usage: ./scripts/verify-zeabur-deployment.sh https://your-domain.zeabur.app

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <SERVER_URL>"
  echo "Example: $0 https://crm.example.com"
  exit 1
fi

BASE_URL="${1%/}"

echo "Checking ${BASE_URL}/healthz ..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/healthz")

if [ "$HTTP_CODE" = "200" ]; then
  echo "OK: /healthz returned 200"
else
  echo "FAIL: /healthz returned ${HTTP_CODE} (expected 200)"
  exit 1
fi

echo "Checking ${BASE_URL}/ (frontend) ..."
FRONT_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/")

if [ "$FRONT_CODE" = "200" ]; then
  echo "OK: frontend returned 200"
else
  echo "WARN: frontend returned ${FRONT_CODE} (expected 200)"
fi

echo "Checking ${BASE_URL}/client-config ..."
CONFIG_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/client-config")

if [ "$CONFIG_CODE" = "200" ]; then
  echo "OK: /client-config returned 200"
else
  echo "WARN: /client-config returned ${CONFIG_CODE}"
fi

echo "Done. Open ${BASE_URL} in a browser to complete sign-in verification."
