"""Endy face unlock: OpenCV YuNet (detect) + SFace (embed). Login-screen convenience only.

Weak by design on a plain webcam: a photo of the user can pass. Password login always remains available.
"""
import os
import stat
import time

import cv2
import numpy as np

MODEL_DIR = "/usr/share/endy-face"
DETECTOR = os.path.join(MODEL_DIR, "face_detection_yunet_2022mar.onnx")
RECOGNIZER = os.path.join(MODEL_DIR, "face_recognition_sface_2021dec.onnx")
DATA_DIR = "/var/lib/endy-face"
THRESHOLD = 0.5      # cosine similarity; SFace's own default is 0.363. Same person ~0.7-0.95, others < 0.3
MIN_HITS = 2         # matching frames required within the time budget
WARMUP_FRAMES = 6    # iSight auto-exposure needs a few frames


def _engine():
    det = cv2.FaceDetectorYN.create(DETECTOR, "", (320, 240), 0.9, 0.3, 5000)
    rec = cv2.FaceRecognizerSF.create(RECOGNIZER, "")
    return det, rec


def embed(det, rec, frame):
    """Unit-length embedding of the largest face in the frame, or None."""
    h, w = frame.shape[:2]
    det.setInputSize((w, h))
    _, faces = det.detect(frame)
    if faces is None or len(faces) == 0:
        return None
    face = faces[int(np.argmax(faces[:, 2] * faces[:, 3]))]
    feat = rec.feature(rec.alignCrop(frame, face)).ravel()
    return feat / np.linalg.norm(feat)


def frames(source=0, seconds=4.0):
    """Yield frames from a camera index or (tests only) from an image file path."""
    deadline = time.monotonic() + seconds
    if isinstance(source, str) and not source.isdigit():
        img = cv2.imread(source)
        while img is not None and time.monotonic() < deadline:
            yield img
            time.sleep(0.05)
        return
    cap = cv2.VideoCapture(int(source), cv2.CAP_V4L2)
    try:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        skipped = 0
        while time.monotonic() < deadline:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.05)
                continue
            if skipped < WARMUP_FRAMES:
                skipped += 1
                continue
            yield frame
    finally:
        cap.release()


def _path(user):
    if not user or "/" in user or user.startswith("."):
        raise ValueError("bad user name")
    return os.path.join(DATA_DIR, user + ".npy")


def is_enrolled(user):
    return os.path.isfile(_path(user))


def _trusted(path):
    """Only trust templates owned by root and not writable by anyone else."""
    st = os.stat(path)
    return st.st_uid == 0 and not (st.st_mode & (stat.S_IWGRP | stat.S_IWOTH))


def load(user):
    p = _path(user)
    if not _trusted(p):
        raise PermissionError("untrusted template file")
    return np.load(p)


def verify(user, source=0, seconds=4.0):
    templates = load(user)
    det, rec = _engine()
    hits = 0
    for frame in frames(source, seconds):
        e = embed(det, rec, frame)
        if e is not None and float(np.max(templates @ e)) >= THRESHOLD:
            hits += 1
            if hits >= MIN_HITS:
                return True
    return False


def capture_templates(source=0, count=8, seconds=20.0, say=print, show=None):
    """Capture up to `count` embeddings (spaced out so poses/lighting vary)."""
    det, rec = _engine()
    out, last = [], 0.0
    for frame in frames(source, seconds):
        if show:
            show(frame)
        if time.monotonic() - last < 0.7:
            continue
        e = embed(det, rec, frame)
        if e is not None:
            out.append(e)
            last = time.monotonic()
            say("  captura %d/%d" % (len(out), count))
            if len(out) >= count:
                break
    return np.array(out, dtype=np.float32)
