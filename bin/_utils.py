from pathlib import Path
import shutil
import re
import platform
import sys
import struct


from collections import namedtuple

CEFVersion = namedtuple("CEFVersion", "version,chrome")
ARCH = 8 * struct.calcsize('P')  # 32 or 64
platform_postfix = {
    "Windows": "win",
    "Linux": "linux",
    "Darwin": "mac",
}
# directories/files names in cefpython sources
# doesn't include architecture type, just OS name.
OS_POSTFIX = platform_postfix.get(platform.system(), "unknown")
# platform name in cefpython binaries
# includes architecture type (32bit/64bit).
OS_POSTFIX2 = f"{OS_POSTFIX}{ARCH}"
# platform name in upstream CEF binaries
# includes architecture type (32bit/64bit)
CEF_POSTFIX2 = platform.system()
if CEF_POSTFIX2 not in platform_postfix:
    CEF_POSTFIX2 = "unknown"
else:
    if CEF_POSTFIX2 == "Darwin":
        CEF_POSTFIX2 = "macosx"
    CEF_POSTFIX2 = f"{CEF_POSTFIX2.lower()}{ARCH}"

MODULE_EXT = "pyd" if platform.system() == "Windows" else "so"
PYVERSION = "{}{}".format(*sys.version_info)
MODULE_NAME = f"cefpython_py{PYVERSION}"


class DIR:
    """Project Directories."""

    ROOT = Path(__file__).parent
    SRC = ROOT / "src"
    API = ROOT / "api"
    DOCS = ROOT / "docs"
    BUILD = ROOT / "build"


class EXAMPLES:
    ROOT = DIR.ROOT / "examples"

    BLOB_STORAGE = ROOT / "blob_storage"
    WEBRTC_EVENT_LOGS = ROOT / "webrtc_event_logs"
    WEBCACHE = ROOT / "webcache"


class SNIPPETS:
    ROOT = DIR.ROOT / "snippets"

    BLOB_STORAGE = ROOT / "blob_storage"
    WEBRTC_EVENT_LOGS = ROOT / "webrtc_event_logs"
    WEBCACHE = ROOT / "webcache"


def cleanup():
    """Clean up directories.

    # Auto cleanup in the examples/ directory, so that build scripts
    # do not include trash directories. See Issue #432.
    """
    for n, v in (vars(EXAMPLES) | vars(SNIPPETS)).items():
        if n == "ROOT":
            continue
        shutil.rmtree(v, ignore_errors=True)


def version_from_header_file(header_file):
    """Read version hardcoded in header files."""
    contents = Path(header_file).read_text(encoding="utf8")
    return {
        match[0]: match[1]
        for match in re.findall(r'^#define (\w+) "?([^\s"]+)"?', contents, re.MULTILINE)
    }


def get_msvs_for_python(vs_prefix=False):
    """Get MSVS version (eg 2008) for current python running."""
    version_mapping = {
        (2, 7): "2008",
        (3, 4): "2010",
        (3, 5): "2015",
        (3, 6): "2015",
        (3, 7): "2015",
        (3, 8): "2015",
        (3, 9): "2015",
    }
    if version := version_mapping.get(sys.version_info[:2]):
        return f"VS{version}" if vs_prefix else version

    raise Exception("ERROR: This version of Python is not supported")


class Info:
    @property
    def cef_versions(self):
        """Get CEF version from the 'src/version/' directory."""
        header_file = DIR.SRC / "version" / f"cef_version_{OS_POSTFIX}.h"
        version = version_from_header_file(header_file)
        breakpoint()
        return CEFVersion(version["CEF_VERSION"], version["CHROME_VERSION_MAJOR"])

    def cef_binaries_libraries_basename(self, postfix2):
        """CEF lib base name."""
        chrome_version, version = self.cef_versions
        return f"cef{chrome_version}_{version}_{postfix2}"

    def cefpython_binary_basename(self, postfix2, version):
        return f"cefpython_binary_{version}_{postfix2}"

    @property
    def cef_binaries_libraries(self):
        """Detect cef binary directory created by automate.py.

        eg. build/cef55_3.2883.1553.g80bd606_win32/
        and set CEF_BINARIES_LIBRARIES to it, otherwise it will
        point to eg. build/cef_win32/ .
        """
        path = DIR.BUILD / f"cef_{OS_POSTFIX2}"
        if not path.exists():
            path = DIR.BUILD / self.cef_binaries_libraries_basename(OS_POSTFIX2)
        if not path.exists():
            raise Exception("CEF binary libraries not found.")

        return path

    def cefpython_binary(self, version):
        """Detect cefpython binary directory where cefpython modules.

        will be put. Eg. build/cefpython_56.0_win32/.
        """
        dirname = self.cefpython_binary_basename(OS_POSTFIX2, version)
        binary_dir = DIR.BUILD / dirname
        if not binary_dir.exists():
            return "CEFPYTHON_BINARY_NOTSET"
        return binary_dir

    @property
    def system(self):
        system = platform.system().upper()
        return system if system == "DARWIN" else "MAC"

    @property
    def unix(self):
        return self.system in {"LINUX", "MAC"}

    @property
    def windows(self):
        return self.system == "WINDOWS"

    def distrib_dir(self, version):
        dirname = "DISTRIB_NOTSET"
        if version:
            if self.unix:
                dirname = f"distrib_{version}_{OS_POSTFIX2}"
            elif self.windows:
                dirname = f"distrib_{version}_win32_win64"
            else:
                dirname = "distrib_{version}_{OS_POSTFIX}"
        return DIR.BUILD / dirname
