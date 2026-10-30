#!/usr/bin/env bash
# Host entry point: builds the ISO inside a privileged linux/amd64 Docker container.
# Works from macOS (Apple Silicon runs it under emulation: expect 1-3 h) or any Linux host with Docker.
set -euo pipefail
cd "$(dirname "$0")"
docker build --platform linux/amd64 -t macbookos-builder builder
docker run --rm --privileged --platform linux/amd64 \
  -v "$PWD":/src:ro -v "$PWD/output":/output \
  -v macbookos-lbcache:/cache \
  macbookos-builder bash /src/builder/build-iso.sh
ls -lh output/*.iso
