"""Generated-file download endpoint and PPT service safety tests."""

from app.services.ppt_service import ppt_service, slugify


def test_slugify_strips_traversal_and_separators():
    assert slugify("../../etc/passwd") == "etc_passwd"
    assert slugify("My Plant!!") == "my_plant"
    assert slugify("///") == "plant"
    assert ".." not in slugify("a/../b")


def test_safe_path_rejects_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(ppt_service, "output_dir", str(tmp_path))
    assert ppt_service.safe_path("../../../etc/passwd") is None
    assert ppt_service.safe_path("..%2F..%2F.env") is None
    assert ppt_service.safe_path("a/b.pptx") is None
    assert ppt_service.safe_path("evil.pptx.exe") is None
    assert ppt_service.safe_path("nope.pptx") is None  # does not exist


async def test_download_generated_file(client, sample_guide):
    result = await ppt_service.generate(sample_guide, "Rose Plant")
    # Filename is slug + unique suffix — no spaces or separators
    name = result["file_name"]
    assert name.startswith("rose_plant_care_guide_")
    assert "/" not in name and "\\" not in name

    r = await client.get(f"/api/v1/files/{name}")
    assert r.status_code == 200
    assert r.content[:2] == b"PK"
    assert "attachment" in r.headers["content-disposition"]
    assert r.headers["x-content-type-options"] == "nosniff"


async def test_download_unknown_file_404(client):
    r = await client.get("/api/v1/files/does_not_exist.pptx")
    assert r.status_code == 404


async def test_download_traversal_404(client):
    for bad in ("..%2Fsecret.pptx", "a/../b.pptx", ".env", "x.pptx%00.jpg"):
        r = await client.get(f"/api/v1/files/{bad}")
        assert r.status_code == 404


def test_cleanup_removes_expired(tmp_path, monkeypatch):
    import os
    import time

    monkeypatch.setattr(ppt_service, "output_dir", str(tmp_path))
    old = tmp_path / "old_guide.pptx"
    old.write_bytes(b"PK")
    os.utime(old, (time.time() - 7200, time.time() - 7200))
    fresh = tmp_path / "fresh_guide.pptx"
    fresh.write_bytes(b"PK")

    removed = ppt_service.cleanup_expired()
    assert removed == 1
    assert not old.exists()
    assert fresh.exists()
