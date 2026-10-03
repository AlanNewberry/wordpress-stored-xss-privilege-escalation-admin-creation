# WordPress Stored XSS - Escalacion de Privilegios y Creacion de Admin

## Descripcion

Desarrolle este script para explotar una vulnerabilidad de Cross-Site Scripting (XSS) almacenado en un plugin de WordPress que permite subir mensajes de voz. El script inyecta un payload XSS que, cuando el administrador visita la pagina, ejecuta JavaScript en su sesion para crear una nueva cuenta de administrador sin que se de cuenta.

## Como funciona

1. **Extraccion de nonce**: Obtiene el token CSRF desde la pagina principal
2. **Subida de archivo WAV**: Sube un archivo WAV dummy para obtener un `post_id` valido
3. **Encriptacion del payload**: Cifra el payload XSS usando AES-GCM con la clave de encriptacion del plugin
4. **Inyeccion XSS**: Guarda una transcripcion maliciosa que contiene el JavaScript
5. **Ejecucion automatica**: Cuando el admin ve el mensaje, el JS crea un usuario administrador via la API interna de WordPress

## Requisitos

```bash
pip install requests cryptography
```

## Uso

Configura las variables al inicio del script:

```python
TARGET = "https://TARGET_HOST"
ENCRYPTION_KEY = "ENCRYPTION_KEY_HERE"
LISTENER_IP = "ATTACKER_IP"
LISTENER_PORT = 8000
NEW_ADMIN_USER = "newadmin"
NEW_ADMIN_PASS = "NewAdminPass123!"
```

Levanta un listener para recibir la confirmacion:

```bash
python3 -m http.server 8000
```

Ejecuta el exploit:

```bash
python3 wordpress-stored-xss-privilege-escalation-admin-creation.py
```

## Cadena de ataque

```
Subida de WAV → Transcripcion con XSS cifrado → Admin visita la pagina →
JS se ejecuta en sesion del admin → Crea usuario administrador → Callback al atacante
```

## Consideraciones

- Necesitas conocer la `ENCRYPTION_KEY` del plugin (generalmente en archivos de configuracion o codigo fuente)
- El ataque es asincrono — depende de que el admin visite la pagina
- El listener HTTP recibe un callback cuando el usuario es creado exitosamente
- Funciona con plugins que almacenan transcripciones de audio sin sanitizar la salida

## Aviso legal

Este script es unicamente para pruebas de seguridad autorizadas y fines educativos. Siempre obtene la autorizacion correspondiente antes de testear contra cualquier sistema.

## Autor

**Alan Newberry**
