#!/usr/bin/env python3
"""Read-only checks for a prepared TAstore APT repo. Never uploads or changes files."""
import gzip
import hashlib
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1] / "repo"
errors = []
def fail(s): errors.append(s)
files = [root / name for name in ("Packages", "Packages.gz", "Release")]
for p in files:
    if not p.is_file(): fail(f"Missing {p.relative_to(root.parent)}")
if errors:
    print("\n".join("FAIL: " + s for s in errors))
    sys.exit(1)
raw = files[0].read_bytes()
try:
    unpacked = gzip.decompress(files[1].read_bytes())
    if unpacked != raw: fail("Packages.gz does not match Packages")
except Exception as exc:
    fail(f"Invalid Packages.gz: {exc}")
paragraphs = [p for p in raw.decode("utf-8", "strict").split("\n\n") if p.strip()]
if not paragraphs: fail("Packages is empty; do not activate Sileo source")
identity = set()
for num, para in enumerate(paragraphs, 1):
    props = {}
    for line in para.splitlines():
        if line.startswith((" ", "\t")):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            props[k] = v.strip()
    required = ("Package", "Version", "Architecture", "Filename", "Size", "SHA256", "Depends")
    for k in required:
        if not props.get(k): fail(f"Package #{num}: missing {k}")
    if any(k not in props for k in required): continue
    key = tuple(props[k] for k in ("Package", "Version", "Architecture"))
    if key in identity: fail(f"Duplicate package/version/architecture: {key}")
    identity.add(key)
    name = props["Filename"]
    if name.startswith("/") or ".." in Path(name).parts or not name.startswith("pool/"):
        fail(f"Unsafe Filename: {name}"); continue
    target = (root / name).resolve()
    if root.resolve() not in target.parents or not target.is_file():
        fail(f"Missing DEB: {name}"); continue
    content = target.read_bytes()
    if not target.is_symlink() and len(content) != int(props["Size"]):
        fail(f"Size mismatch: {name}")
    if hashlib.sha256(content).hexdigest().lower() != props["SHA256"].lower():
        fail(f"SHA256 mismatch: {name}")
    p = props["Package"]
    deps = props["Depends"]
    if p == "com.sushibta.multita.rh15" and not ("firmware (>= 15.0)" in deps and "firmware (<< 16.0)" in deps):
        fail(f"RH15 firmware bounds missing: {name}")
    if p == "com.sushibta.multita.rh16" and not ("firmware (>= 16.0)" in deps and "firmware (<< 17.0)" in deps):
        fail(f"RH16 firmware bounds missing: {name}")
    if p in ("com.sushibta.multita.rh15", "com.sushibta.multita.rh16") and props["Architecture"] != "iphoneos-arm64e":
        fail(f"RootHide architecture mismatch: {name}")
release = files[2].read_text(encoding="utf-8")
for filename, data in (("Packages", raw), ("Packages.gz", files[1].read_bytes())):
    hash_ = hashlib.sha256(data).hexdigest()
    if hash_ not in release: fail(f"Release does not include SHA256 for {filename}")
if errors:
    print("\n".join("FAIL: " + s for s in errors))
    sys.exit(1)
print(f"PASS: {len(paragraphs)} package record(s), package files, SHA256 and Release indexes consistent")
print("NOTE: Static checks only. Does not prove DEB metadata, signature, jailbreak compatibility, or Sileo runtime.")
