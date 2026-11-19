# Regenerates manifest.json from the locale directories.
#
# Run this after editing any dictionary file, then commit both the change and
# the new manifest: Path of Building compares the SHA1 listed here against the
# file on disk to decide what to download, so a manifest that disagrees with
# the payload is the only way to ship a broken update.
#
#   python tools/build_manifest.py
#
# The version is bumped by hand in this file when a release is cut; clients
# ignore it and diff per file, but it makes "which dictionary am I on" easy to
# answer in a bug report.
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Display data for each locale. Anything not listed here still appears in the
# manifest, just under its directory name.
LOCALE_INFO = {
    "zh-rCN": {
        "name": "Simplified Chinese",
        "nativeName": "简体中文",
    },
}

# Files that describe the locale but are not part of it.
SKIP = {"meta.json"}


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
            full = os.path.join(path, name)
            with open(full, "rb") as f:
                files[name] = hashlib.sha1(f.read()).hexdigest()
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
