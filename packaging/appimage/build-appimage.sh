#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:?Version argument required (e.g. 1.3.0)}"
ARCH="x86_64"
PYTHON_VERSION="3.12"

# Install native system libs that tempren uses via ctypes
sudo apt-get install -y --no-install-recommends \
    libmagic1 libmediainfo0v5 libzen0v5

# Install build tooling
pip install --quiet python-appimage

# Build base Python AppImage and install tempren into it
# python-appimage looks for .desktop and icon alongside the entrypoint script
python -m python_appimage build app \
    --python-version "${PYTHON_VERSION}" \
    packaging/appimage/entrypoint.py

# Find the generated AppDir (python-appimage names it based on the script)
APPDIR="$(ls -d *.AppDir 2>/dev/null | head -1)"
[ -z "${APPDIR}" ] && { echo "AppDir not found"; exit 1; }

# Install tempren (with video extras) into the AppDir's Python
"${APPDIR}/usr/bin/python${PYTHON_VERSION}" -m pip install --quiet \
    "tempren[video]==${VERSION}"

# Bundle native shared libraries into AppDir/usr/lib so ctypes can find them
APPDIR_LIB="${APPDIR}/usr/lib"
mkdir -p "${APPDIR_LIB}"

for lib in libmagic.so.1 libmediainfo.so.0 libzen.so.0; do
    LIBPATH=$(ldconfig -p | grep " ${lib}" | awk '{print $NF}' | head -1)
    [ -n "${LIBPATH}" ] && cp -v "${LIBPATH}" "${APPDIR_LIB}/"
done

# Copy magic database (libmagic needs it at runtime)
SYSTEM_MAGIC_DB="/usr/share/misc/magic.mgc"
[ -f "${SYSTEM_MAGIC_DB}" ] && cp -v "${SYSTEM_MAGIC_DB}" "${APPDIR_LIB}/"

# Patch AppRun to expose bundled libs to the dynamic linker
sed -i '2i export LD_LIBRARY_PATH="${APPDIR}/usr/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"' \
    "${APPDIR}/AppRun"

# Download appimagetool and squash into final AppImage
wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${ARCH}.AppImage" \
    -O appimagetool
chmod +x appimagetool
ARCH="${ARCH}" ./appimagetool "${APPDIR}" "tempren-${VERSION}-${ARCH}.AppImage"

echo "Built: tempren-${VERSION}-${ARCH}.AppImage"
