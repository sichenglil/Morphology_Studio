import morphology_toolkit.paths as paths


def test_source_resource_root_is_independent_of_cwd(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert (paths.resource_root() / "config" / "robot_models.json").is_file()


def test_pyinstaller_bundle_path(monkeypatch, tmp_path):
    monkeypatch.setattr(paths.sys, "frozen", True, raising=False)
    monkeypatch.setattr(paths.sys, "executable", str(tmp_path / "MorphologyStudio.exe"))
    monkeypatch.setattr(paths.sys, "_MEIPASS", str(tmp_path / "_internal"), raising=False)
    assert paths.bundled_root() == (tmp_path / "_internal").resolve()


def test_windows_writable_paths_use_appdata_and_localappdata(monkeypatch, tmp_path):
    monkeypatch.setattr(paths.sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path / "roaming"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert paths.get_user_data_dir() == tmp_path / "roaming" / "MorphologyStudio"
    assert paths.get_cache_dir() == tmp_path / "MorphologyStudio" / "Cache"
    assert paths.get_log_dir() == tmp_path / "roaming" / "MorphologyStudio" / "logs"


def test_linux_writable_paths_follow_xdg(monkeypatch, tmp_path):
    monkeypatch.setattr(paths.sys, "platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    assert paths.get_user_data_dir() == tmp_path / "data" / "MorphologyStudio"
    assert paths.get_cache_dir() == tmp_path / "cache" / "MorphologyStudio"


def test_macos_writable_paths_use_library(monkeypatch, tmp_path):
    monkeypatch.setattr(paths.sys, "platform", "darwin")
    monkeypatch.setattr(paths.Path, "home", lambda: tmp_path)
    assert (
        paths.get_user_data_dir()
        == tmp_path / "Library" / "Application Support" / "MorphologyStudio"
    )
    assert paths.get_cache_dir() == tmp_path / "Library" / "Caches" / "MorphologyStudio"
