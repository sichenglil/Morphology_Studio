import morphology_toolkit.paths as paths


def test_source_resource_root_is_independent_of_cwd(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert (paths.resource_root() / "config" / "robot_models.json").is_file()


def test_pyinstaller_bundle_path(monkeypatch, tmp_path):
    monkeypatch.setattr(paths.sys, "frozen", True, raising=False)
    monkeypatch.setattr(paths.sys, "executable", str(tmp_path / "MorphologyStudio.exe"))
    monkeypatch.setattr(paths.sys, "_MEIPASS", str(tmp_path / "_internal"), raising=False)
    assert paths.bundled_root() == (tmp_path / "_internal").resolve()
