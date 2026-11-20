# Regenerates manifest.json from the locale directories.
#
# Run this after editing any dictionary file, then commit both the change and
# the new manifest: Path of Building compares the SHA1 listed here against the
# file on disk to decide what to download, so a manifest that disagrees with
# the payload is the only way to ship a broken update.
#
#   python tools/build_manifest.py
#
# The hash describes the bytes the repository publishes, which are the bytes
# git stores -- not necessarily the bytes in the working copy. A checkout made
# before .gitattributes landed can still hold CRLF while git's stat cache
# calls the file clean, and a manifest built from those bytes records a hash
# that raw.githubusercontent never serves, leaving clients to re-download the
# file on every check. So committed files are read back from HEAD and
# uncommitted ones are hashed the way git will store them.
#
# The version is bumped by hand in this file when a release is cut; clients
# ignore it and diff per file, but it makes "which dictionary am I on" easy to
# answer in a bug report.
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Display data for each locale. Anything not listed here still appears in the
# manifest, just under its directory name.
LOCALE_INFO = {
    "zh-rCN": {
        "name": "Simplified Chinese",
        "nativeName": "简体中文",
    },
}


def git(*args):
    try:
        return subprocess.run(("git",) + args, cwd=ROOT, check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
    except FileNotFoundError:
        sys.exit("build_manifest: 'git' is required to hash the payload")
    except subprocess.CalledProcessError as e:
        sys.exit("build_manifest: git %s failed: %s"
                 % (" ".join(args), e.stderr.decode("utf-8", "replace").strip()))


def published_bytes(rel):
    """The bytes a push will publish for `rel`."""
    if not git("status", "--porcelain", "--", rel).strip():
        return git("cat-file", "blob", "HEAD:" + rel)
    obj = git("hash-object", "-w", "--", rel).decode().strip()
    return git("cat-file", "blob", obj)


def main():
    locales = []
    for entry in sorted(os.listdir(ROOT)):
        path = os.path.join(ROOT, entry)
        if not os.path.isdir(path) or entry in ("tools", ".git"):
            continue
        files = {}
        for name in sorted(os.listdir(path)):
            if not name.endswith(".json"):
                continue
            files[name] = hashlib.sha1(published_bytes(entry + "/" + name)).hexdigest()
        if not files:
            continue
        info = LOCALE_INFO.get(entry, {})
        locales.append({
            "id": entry,
            "name": info.get("name", entry),
            "nativeName": info.get("nativeName", info.get("name", entry)),
            "files": files,
        })

    manifest = {
        "schema": 2,
        "defaultLocale": "zh-rCN",
        "locales": locales,
    }
    out = os.path.join(ROOT, "manifest.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")

    total = sum(len(l["files"]) for l in locales)
    print("wrote %s (%d locale(s), %d files)" % (out, len(locales), total))


if __name__ == "__main__":
    main()
