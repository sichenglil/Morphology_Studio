from pathlib import Path

from morphology_toolkit.core.model import ProcessingMode
from morphology_toolkit.resources import PackageResolver, load_package_map


def make_package(path: Path, name: str):
    path.mkdir(parents=True)
    (path / "package.xml").write_text(f"<package><name>{name}</name></package>", encoding="utf-8")


def test_explicit_map_and_trace(tmp_path):
    package = tmp_path / "pkg"; make_package(package, "demo")
    resolver = PackageResolver({"demo": package})
    assert resolver.resolve("demo") == package.resolve()
    assert resolver.explain("demo").candidates[0].source == "explicit_map"


def test_root_discovery_and_missing_trace(tmp_path):
    package = tmp_path / "root" / "pkg"; make_package(package, "demo")
    resolver = PackageResolver(roots=[tmp_path / "root"])
    assert resolver.resolve("demo") == package.resolve()
    assert resolver.resolve("missing") is None
    assert "not found" in resolver.explain("missing").error


def test_duplicate_package_is_ambiguous(tmp_path):
    make_package(tmp_path / "a" / "pkg", "duplicate")
    make_package(tmp_path / "b" / "pkg", "duplicate")
    resolver = PackageResolver(roots=[tmp_path], mode=ProcessingMode.ASSISTED)
    assert resolver.resolve("duplicate") is None
    assert "Ambiguous" in resolver.explain("duplicate").error


def test_relative_package_map():
    mapping = load_package_map(Path("configs/package_maps/local_models.yaml"), Path.cwd())
    assert mapping["ur_description"] == (Path.cwd() / "models/ur_description").resolve()
