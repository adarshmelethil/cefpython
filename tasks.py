#!/usr/bin/env python

import invoke
import shutil
from pathlib import Path


@invoke.task
def sync_cef(
    c,
    build_dir="cef_build",
    branch="master",
    url="https://bitbucket.org/chromiumembedded/cef.git",
    clean=False,
    update=True,
):
    """Create cef/ directories in cef_build_dir/ and in chromium/src/ ."""
    # Clone cef repo and checkout branch
    dest = Path(build_dir) / "cef"
    if dest.exists():
        if clean:
            shutil.rmtree(dest, ignore_errors=True)
        elif update:
            with c.cd(dest):
                c.run("git pull")
            return
    c.run(f"git clone {url} {dest}")


@invoke.task
def build_cef(c, build_dir="cef_build"):
    build_dir = Path(build_dir)
    flags = {
        "download-dir": build_dir,
    }
    if dry_run:
        flags["dry-run"] = True


def build_cef():
    """Build CEF from sources."""

    # Delete binary_distrib
    if os.path.exists(Options.binary_distrib):
        rmdir(Options.binary_distrib)

    # Run automate-git.py
    run_automate_git()
    print("[automate.py] Binary distrib created in %s" % Options.binary_distrib)

    if Options.x86:
        print(
            "[automate.py] INFO: Build CEF projects and create prebuilt"
            " binaries on Linux 32-bit using eg. VirtualBox. Copy the binary"
            " distrib's cef_binary_*/ directory (path displayed above) to"
            " cefpython's build/ directory. Then run automate.py"
            " --prebuilt-cef on Linux 32-bit."
        )
        sys.exit(0)
    else:
        # Build cefclient, cefsimple, ceftests, libcef_dll_wrapper
        build_cef_projects()
        create_prebuilt_binaries()


def main():
    pass


if __name__ == "__main__":
    main()
