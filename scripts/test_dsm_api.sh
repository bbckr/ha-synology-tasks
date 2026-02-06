#!/usr/bin/env bash
# Manual test for Synology DSM Task Scheduler / Event Scheduler API.
# Set HOST, PORT, USER, PASS (and optionally USE_SSL=false) then run.
#
# Example:
#   export HOST=192.168.1.10 PORT=5001 USER=admin PASS=mypass
#   ./scripts/test_dsm_api.sh
#
# Raw curl one-liners (replace HOST, PORT, USER, PASS; use -k for self-signed HTTPS):
#
#   # 1) Login – response has .data.sid and .data.synotoken
#   curl -sk "https://HOST:PORT/webapi/entry.cgi?api=SYNO.API.Auth&version=7&method=login&enable_syno_token=yes&account=USER&passwd=PASS"
#
#   # 2) List tasks (use SID and SynoToken from login)
#   curl -sk "https://HOST:PORT/webapi/entry.cgi?api=SYNO.Core.TaskScheduler&version=3&method=list&sort_by=name&sort_direction=asc&limit=50&offset=0&SynoToken=TOKEN&_sid=SID"
#
#   # 3) Run task (replace TASK_NAME with a task name from list)
#   curl -sk "https://HOST:PORT/webapi/entry.cgi?api=SYNO.Core.EventScheduler&version=1&method=run&task_name=TASK_NAME&SynoToken=TOKEN&_sid=SID"
#
#   # 4) Force session error (invalid SID) – expect success: false, error.code 119
#   curl -sk "https://HOST:PORT/webapi/entry.cgi?api=SYNO.Core.TaskScheduler&version=3&method=list&SynoToken=TOKEN&_sid=invalid"

set -e
: "${HOST:?Set HOST (e.g. 192.168.1.10)}"
: "${USER:?Set USER}"
: "${PASS:?Set PASS}"
: "${PORT:=5001}"
: "${USE_SSL:=true}"

if [[ "$USE_SSL" == true ]]; then
  BASE="https://${HOST}:${PORT}"
  INSECURE="-k"
else
  BASE="http://${HOST}:${PORT}"
  INSECURE=""
fi
ENDPOINT="${BASE}/webapi/entry.cgi"

# Print response; use jq if it looks like JSON, otherwise show raw (e.g. HTML/error)
print_response() {
  local raw="$1"
  if echo "$raw" | jq -e . >/dev/null 2>&1; then
    echo "$raw" | jq .
  else
    echo "(response is not JSON, showing raw)"
    echo "$raw"
  fi
}

echo "=== 1. Login (get SID + SynoToken) ==="
LOGIN_RESP=$(curl -s $INSECURE "${ENDPOINT}?api=SYNO.API.Auth&version=7&method=login&enable_syno_token=yes&account=${USER}&passwd=${PASS}")
print_response "$LOGIN_RESP"

SUCCESS=$(echo "$LOGIN_RESP" | jq -r '.success' 2>/dev/null || echo "false")
if [[ "$SUCCESS" != "true" ]]; then
  echo "Login failed or response was not JSON. Check host, port, credentials, and that DSM Web API is reachable."
  exit 1
fi

SID=$(echo "$LOGIN_RESP" | jq -r '.data.sid')
TOKEN=$(echo "$LOGIN_RESP" | jq -r '.data.synotoken')
echo "SID=${SID}"
echo "SynoToken=${TOKEN}"

echo ""
echo "=== 2. List tasks (TaskScheduler) ==="
print_response "$(curl -s $INSECURE "${ENDPOINT}?api=SYNO.Core.TaskScheduler&version=3&method=list&sort_by=name&sort_direction=asc&limit=50&offset=0&SynoToken=${TOKEN}&_sid=${SID}")"

echo ""
echo "=== 3. Run a task (EventScheduler) – replace TASK_NAME with a real task name from step 2 ==="
TASK_NAME="${TASK_NAME:-MyScheduledTask}"
echo "Using task_name=${TASK_NAME}"
print_response "$(curl -s $INSECURE "${ENDPOINT}?api=SYNO.Core.EventScheduler&version=1&method=run&task_name=${TASK_NAME}&SynoToken=${TOKEN}&_sid=${SID}")"

echo ""
echo "=== 4. (Optional) Call list again with wrong SID – expect invalid session response ==="
STEP4_RESP=$(curl -s $INSECURE "${ENDPOINT}?api=SYNO.Core.TaskScheduler&version=3&method=list&sort_by=name&sort_direction=asc&limit=50&offset=0&SynoToken=${TOKEN}&_sid=invalid_sid_here")
print_response "$STEP4_RESP"
# DSM returns: {"error": {"code": 119}, "success": false} for invalid/expired session
STEP4_SUCCESS=$(echo "$STEP4_RESP" | jq -r '.success' 2>/dev/null)
STEP4_CODE=$(echo "$STEP4_RESP" | jq -r '.error.code' 2>/dev/null)
if [[ "$STEP4_SUCCESS" == "false" && "$STEP4_CODE" == "119" ]]; then
  echo "Expected: invalid session (error 119) – integration will re-login on this."
fi
