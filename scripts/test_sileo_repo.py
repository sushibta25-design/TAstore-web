#!/usr/bin/env python3
"""Self-test the actual Sileo APT verifier with a synthetic package in a temp dir."""
import gzip
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile

source = Path(__file__).resolve().parent / "verify_sileo_repo.py"
with tempfile.TemporaryDirectory(prefix="tastore-apt-test-") as temp:
    root = Path(temp)
    (root / "scripts").mkdir()
    shutil.copy2(source, root / "scripts/verify_sileo_repo.py")
    build = root / "fixture"
    (build / "DEBIAN").mkdir(parents=True)
    (build / "usr/share/tastore").mkdir(parents=True)
    (build / "DEBIAN/control").write_text(
        "Package: com.sushibta.localtest\nVersion: 0.0.1\nArchitecture: iphoneos-arm64e\n"
        "Maintainer: TAstore\nDescription: Local APT fixture only\nDepends: firmware (>= 15.0)\n"
    )
    (build / "usr/share/tastore/marker").write_text("LOCAL TEST - NEVER PUBLISH")
    repo = root / "repo"
    (repo / "pool").mkdir(parents=True)
    deb = repo / "pool/com.sushibta.localtest_0.0.1_iphoneos-arm64e.deb"
    subprocess.run(["dpkg-deb", "--build", str(build), str(deb)], check=True, capture_output=True)
    scan = subprocess.run(["dpkg-scanpackages", "pool", "/dev/null"],
                          cwd=repo, check=True, capture_output=True)
    (repo / "Packages").write_bytes(scan.stdout)
    (repo / "Packages.gz").write_bytes(gzip.compress(scan.stdout, mtime=0))
    release = "Origin: TAstore Local Test\nSuite: test\nSHA256:\n"
    for n in ("Packages", "Packages.gz"):
        b = (repo / n).read_bytes()
        release += f" {hashlib.sha256(b).hexdigest()} {len(b)} {n}\n"
    (repo / "Release").write_text(release)
    cmd = ["python3", str(root / "scripts/verify_sileo_repo.py")]
    good = subprocess.run(cmd, capture_output=True, text=True)
    assert good.returncode == 0, good.stdout + good.stderr
    deb.write_bytes(deb.read_bytes() + b"CORRUPTED")
    bad = subprocess.run(cmd, capture_output=True, text=True)
    assert bad.returncode != 0 and "SHA256 mismatch" in bad.stdout, bad.stdout + bad.stderr
    print("PASS: actual APT verifier accepts valid synthetic repository")
    print("PASS: actual APT verifier rejects tampered package")
    print("No test packages were uploaded; temporary directory removed.")
