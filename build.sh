#!/usr/bin/env bash
# Host entry point: builds the ISO inside a privileged Docker container.
# ARCH=amd64 (default, MacBook Intel) or ARCH=arm64 (VM on Apple Silicon: native speed, no emulation).
# Works from macOS (Apple Silicon runs it under emulation: expect 1-3 h) or any Linux host with Docker.
set -euo pipefail
ARCH=${ARCH:-amd64}
SUFFIX=; [ "$ARCH" = amd64 ] || SUFFIX=-$ARCH  # keep the existing amd64 cache volume name
cd "$(dirname "$0")"
docker build --platform linux/$ARCH --build-arg ARCH=$ARCH -t macbookos-builder builder
docker run --rm --privileged --platform linux/$ARCH -e ARCH=$ARCH \
  -v "$PWD":/src:ro -v "$PWD/output":/output \
  -v macbookos-lbcache${SUFFIX}:/cache \
  macbookos-builder bash /src/builder/build-iso.sh
ls -lh output/*.iso
