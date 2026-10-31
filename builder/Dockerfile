ARG ARCH=amd64
FROM --platform=linux/${ARCH} debian:bookworm
ARG ARCH
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    live-build debootstrap squashfs-tools xorriso mtools dosfstools ca-certificates git curl \
    imagemagick gnupg rsync xz-utils zsync \
 && if [ "$ARCH" = amd64 ]; then \
      apt-get install -y --no-install-recommends isolinux syslinux-common syslinux-utils \
        grub-pc-bin grub-efi-amd64-bin grub-efi-ia32-bin; \
    else \
      apt-get install -y --no-install-recommends grub-efi-arm64-bin; \
    fi \
 && rm -rf /var/lib/apt/lists/*
