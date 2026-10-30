#!/usr/bin/python3
"""Run via pkexec (asks for the user's password). Writes/removes ONLY the invoking user's template.

  store.py save     < templates.npy   (stdin: raw .npy bytes)
  store.py remove
"""
import io
import os
import pwd
import sys

import numpy as np

DATA_DIR = "/var/lib/endy-face"

uid = int(os.environ.get("PKEXEC_UID", "-1"))
if uid < 1000:
    sys.exit("recusado: so o proprio usuario pode cadastrar o rosto")
user = pwd.getpwuid(uid).pw_name
path = os.path.join(DATA_DIR, user + ".npy")
os.makedirs(DATA_DIR, mode=0o700, exist_ok=True)
os.chmod(DATA_DIR, 0o700)

if sys.argv[1:] == ["remove"]:
    if os.path.exists(path):
        os.remove(path)
    print("rosto removido")
elif sys.argv[1:] == ["save"]:
    arr = np.load(io.BytesIO(sys.stdin.buffer.read()), allow_pickle=False)
    if arr.ndim != 2 or arr.shape[1] != 128 or not (3 <= len(arr) <= 64):
        sys.exit("dados invalidos")
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        np.save(f, arr.astype(np.float32))
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)
    print("rosto salvo (%d amostras)" % len(arr))
else:
    sys.exit("uso: store.py save|remove")
