# PoB i18n dictionaries

Translation data for the [PoB i18n fork](../path-of-building-fork). One
directory per locale, plus a manifest the client reads to decide what to
download.

## Layout

```
manifest.json        what exists, and a SHA1 for every file
zh-rCN/              one locale; directory name is the locale id
  meta.json          per-locale load settings (load order, whitelist)
  items.json         ...
tools/build_manifest.py
```

`manifest.json` is generated — do not hand-edit it.

## Adding or changing a translation

1. Edit the JSON under the locale directory. Keys are the exact English
   strings Path of Building draws; values are the translation. A key that is
   missing simply draws English, so a blank value is never an error.
2. Regenerate the manifest:
   ```
   python tools/build_manifest.py
   ```
3. Commit both the dictionary change and `manifest.json`.

Anything committed to the default branch reaches clients on their next
update check.

## Adding a language

1. Create `<locale-id>/` with the same file set as an existing locale.
2. Add display names to `LOCALE_INFO` in `tools/build_manifest.py`.
3. Regenerate the manifest and commit.
4. In the client, add the locale id to `i18n/manifest.json` if that copy is
   kept in the app bundle — or simply let the next update pull it in.

## File notes

- `meta.json` lists the dictionary files, their load order (later files
  override earlier ones) and the whitelist of strings that are allowed to
  stay English.
- `pob-ui.json` holds strings Path of Building itself writes (calcs tab row
  labels, tips text). The game data dictionaries cover game text only, so
  these have to be maintained by hand.

## Update mechanism

The client requests `manifest.json`, compares each file's SHA1 with what it
has on disk, and downloads only the files that differ. Files are written to
`i18n/<locale>/` in the application directory. There is no signature — the
client trusts the host it is configured to talk to, so point it at a repo you
control.
