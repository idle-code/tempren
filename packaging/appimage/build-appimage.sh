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

# Build base Python AppDir (--no-packaging skips appimagetool inside python-appimage,
# which always downloads from AppImage/appimagetool/continuous — an unreliable URL)
# python-appimage looks for .desktop and icon alongside the entrypoint script
python -m python_appimage build app \
    --no-packaging \
    --python-version "${PYTHON_VERSION}" \
    packaging/appimage/entrypoint.py

# python-appimage names the AppDir {script_name}-{ARCH} when --no-packaging is used
APPDIR="entrypoint.py-${ARCH}"
[ -d "${APPDIR}" ] || { echo "AppDir not found: ${APPDIR}"; exit 1; }

# Install tempren (with video extras) into the AppDir's Python
"${APPDIR}/usr/bin/python${PYTHON_VERSION}" -m pip install --quiet \
    "tempren[video]==${VERSION}"

# Patch AppRun to invoke tempren instead of starting a bare Python interpreter
sed -i 's|"$APPDIR/opt/python'"${PYTHON_VERSION}"'/bin/python'"${PYTHON_VERSION}"'" "$@"|"$APPDIR/opt/python'"${PYTHON_VERSION}"'/bin/python'"${PYTHON_VERSION}"'" "$APPDIR/opt/python'"${PYTHON_VERSION}"'/bin/tempren" "$@"|' \
    "${APPDIR}/AppRun"

# Replace generic Python desktop entry and icon with tempren's own
cp packaging/appimage/tempren.desktop "${APPDIR}/tempren.desktop"
rm -f "${APPDIR}"/python*.desktop
cp packaging/appimage/tempren.svg "${APPDIR}/tempren.svg"
ln -sf tempren.svg "${APPDIR}/.DirIcon"

# Bundle native shared libraries into AppDir/usr/lib so ctypes can find them
APPDIR_LIB="${APPDIR}/usr/lib"
mkdir -p "${APPDIR_LIB}"

for lib in libmagic.so.1 libmediainfo.so.0 libzen.so.0; do
    LIBPATH=$(ldconfig -p | grep "[[:space:]]${lib}" | awk '{print $NF}' | head -1)
    [ -n "${LIBPATH}" ] && cp -v "${LIBPATH}" "${APPDIR_LIB}/"
done

# Copy magic database (libmagic needs it at runtime)
SYSTEM_MAGIC_DB="/usr/share/misc/magic.mgc"
[ -f "${SYSTEM_MAGIC_DB}" ] && cp -v "${SYSTEM_MAGIC_DB}" "${APPDIR_LIB}/"

# Patch AppRun to expose bundled libs to the dynamic linker
sed -i '2i export LD_LIBRARY_PATH="${APPDIR}/usr/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"' \
    "${APPDIR}/AppRun"

# Download appimagetool and pack the final AppImage
# APPIMAGE_EXTRACT_AND_RUN avoids FUSE dependency on GitHub-hosted runners
wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${ARCH}.AppImage" \
    -O appimagetool
chmod +x appimagetool
APPIMAGE_EXTRACT_AND_RUN=1 ARCH="${ARCH}" ./appimagetool --no-appstream "${APPDIR}" "tempren-${VERSION}-${ARCH}.AppImage"

echo "Built: tempren-${VERSION}-${ARCH}.AppImage"
