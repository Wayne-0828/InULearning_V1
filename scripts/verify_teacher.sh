#!/usr/bin/env bash
set -euo pipefail

echo "[1/6] Login as teacher01@test.com"
LOGIN_BODY=/tmp/login_body.json
echo -n '{"email":"teacher01@test.com","password":"password123"}' > "$LOGIN_BODY"
curl -s -X POST http://localhost/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  --data-binary @"$LOGIN_BODY" | tee /tmp/login.json >/dev/null

python3 - <<'PY'
import json
token = json.load(open('/tmp/login.json')).get('access_token','')
open('/tmp/token.txt','w').write(token)
print('TOKEN_PREFIX=', token[:20])
PY

TOKEN=$(cat /tmp/token.txt)

echo "[2/6] Get teacher classes"
curl -s http://localhost/api/v1/teacher/classes -H "Authorization: Bearer $TOKEN" \
  | tee /tmp/classes.json | sed -n '1,200p' >/dev/null

echo "[3/6] Find class id for 七年一班"
python3 - <<'PY'
import json
arr=json.load(open('/tmp/classes.json'))
cid = next((str(c.get('id')) for c in arr if (c.get('name') or '').strip()=='七年一班'), '')
open('/tmp/class_id.txt','w').write(cid)
print('CLASS_ID=', cid)
PY

CLASS_ID=$(cat /tmp/class_id.txt)
if [ -z "$CLASS_ID" ]; then
  echo "Class 七年一班 not found in classes list" >&2
  exit 2
fi

echo "[4/6] Get students of class $CLASS_ID"
curl -s http://localhost/api/v1/teacher/classes/$CLASS_ID/students -H "Authorization: Bearer $TOKEN" \
  | tee /tmp/students.json | sed -n '1,200p' >/dev/null

echo "[5/6] Students count"
python3 - <<'PY'
import json
arr=json.load(open('/tmp/students.json'))
print('students_count=', len(arr))
print('sample=', json.dumps(arr[:3], ensure_ascii=False))
PY

echo "[6/6] Done"


