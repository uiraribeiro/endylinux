#!/usr/bin/env bash
# Runs INSIDE the container. Builds in /build (native fs; live-build breaks on macOS bind mounts).
set -euo pipefail
rm -rf /build && mkdir /build && cd /build
cp -a /src/config .
lb config \
  --distribution bookworm --architectures amd64 \
  --archive-areas "main contrib non-free non-free-firmware" \
  --parent-archive-areas "main contrib non-free non-free-firmware" \
  --debian-installer none \
  --binary-images iso-hybrid \
  --bootloaders "syslinux,grub-efi" \
  --bootappend-live "boot=live components quiet splash username=macbook hostname=macbookos locales=en_US.UTF-8 keyboard-layouts=us keyboard-variants=intl keyboard-options=altwin:ctrl_win timezone=America/Sao_Paulo" \
  --zsync false --iso-application "MacBookOS" --iso-volume "MacBookOS" \
  --apt-recommends false --firmware-chroot true \
  --compression xz --memtest none --win32-loader false \
  --linux-flavours amd64 --security true --updates true
# Persist live-build's bootstrap + package cache across runs (docker volume mounted at /cache)
mkdir -p /cache && rm -rf /build/cache && ln -s /cache /build/cache
lb build 2>&1 | tee /output/build.log || true
# Keep the ISO even if a late optional step (e.g. zsync) fails
ls ./*.iso >/dev/null 2>&1 || { echo 'no ISO produced'; exit 1; }
mv -v ./*.iso /output/MacBookOS-amd64.iso
( cd /output && sha256sum MacBookOS-amd64.iso > MacBookOS-amd64.iso.sha256 )
