from __future__ import annotations

import logging
import os
import platform
import socket
import sys
import threading
import time
import traceback
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from morphology_toolkit import __version__
from morphology_toolkit.logging_config import configure_logging
from morphology_toolkit.paths import bundled_root, get_cache_dir, resource_root

WEBVIEW2_CLIENT_ID = "{F1E7E1A1-2D57-49A6-9F1C-1F7B4D5F7D5A}"


def webview2_runtime_available() -> bool:
    if sys.platform != "win32":
        return True
    try:
        import winreg

        roots = (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE)
        keys = (
            rf"SOFTWARE\Microsoft\EdgeUpdate\Clients\{WEBVIEW2_CLIENT_ID}",
            rf"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{WEBVIEW2_CLIENT_ID}",
        )
        for root in roots:
            for key in keys:
                try:
                    with winreg.OpenKey(root, key) as handle:
                        if winreg.QueryValueEx(handle, "pv")[0]:
                            return True
                except OSError:
                    continue
    except ImportError:
        return False
    candidates = (
        os.environ.get("PROGRAMFILES(X86)"),
        os.environ.get("PROGRAMFILES"),
        os.environ.get("LOCALAPPDATA"),
    )
    return any(
        root and os.path.isdir(os.path.join(root, "Microsoft", "EdgeWebView", "Application"))
        for root in candidates
    )


def native_webview_backend() -> str:
    """Select the platform-native pywebview renderer."""
    if sys.platform == "win32":
        return "edgechromium"
    if sys.platform == "darwin":
        return "cocoa"
    return "gtk"


def available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_until_healthy(url: str, timeout: float = 15.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urlopen(f"{url}/api/health", timeout=0.5) as response:  # noqa: S310
                if response.status == 200:
                    return True
        except (OSError, URLError):
            time.sleep(0.1)
    return False


def create_server(port: int):
    import uvicorn

    from morphology_toolkit.webapp import create_app

    config = uvicorn.Config(
        app=create_app(),
        host="127.0.0.1",
        port=port,
        log_config=None,
        access_log=False,
        use_colors=False,
    )
    return uvicorn.Server(config)


def frontend_directory():
    packaged = bundled_root() / "morphology_toolkit" / "static" / "frontend"
    if packaged.is_dir():
        return packaged
    return Path(__file__).resolve().parent / "static" / "frontend"


def verify_installation() -> int:
    """Exercise packaged resources, writable storage, and API creation without opening a GUI."""
    frontend = frontend_directory()
    required = [frontend / "index.html"]
    required.extend(
        [
            next((frontend / "assets").glob("opencascade.full-*.wasm"), frontend / "missing.wasm"),
            next((frontend / "assets").glob("StepWorker-*.js"), frontend / "missing-worker.js"),
            resource_root() / "config" / "robot_models.json",
        ]
    )
    missing = [str(path) for path in required if not path.is_file() or path.stat().st_size == 0]
    if missing:
        raise RuntimeError(f"Packaged resources are missing or empty: {missing}")
    cache = get_cache_dir()
    cache.mkdir(parents=True, exist_ok=True)
    probe = cache / "installation-probe.tmp"
    probe.write_text("ok", encoding="utf-8")
    probe.unlink()
    server = create_server(available_port())
    route_paths = {route.path for route in server.config.app.routes}
    if not {"/", "/api/health", "/api/models/import-step", "/api/export"} <= route_paths:
        raise RuntimeError("Packaged API routes are incomplete")
    print("INSTALLATION_OK", platform.system(), platform.machine())
    return 0


def show_error(message: str) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Morphology Studio", message)
        root.destroy()
    except Exception:
        logging.getLogger(__name__).exception("Unable to show startup error dialog")


def _run(browser_fallback: bool = False) -> int:
    started = time.perf_counter()
    log_path = configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Morphology Studio %s", __version__)
    logger.info("Frozen=%s executable=%s", getattr(sys, "frozen", False), sys.executable)
    logger.info("Platform=%s machine=%s", platform.platform(), platform.machine())
    logger.info("MEIPASS=%s", getattr(sys, "_MEIPASS", None))
    logger.info("Resource root=%s", resource_root())
    frontend = frontend_directory() / "index.html"
    logger.info("Frontend entry=%s", frontend)
    frontend_assets = frontend.parent / "assets"
    wasm = next(frontend_assets.glob("opencascade.full-*.wasm"), None)
    worker = next(frontend_assets.glob("StepWorker-*.js"), None)
    logger.info("OpenCascade WASM=%s", wasm)
    logger.info("OpenCascade Worker=%s", worker)
    port = int(os.environ.get("MORPHOLOGY_PORT", "0")) or available_port()
    url = f"http://127.0.0.1:{port}"
    server = create_server(port)
    thread = threading.Thread(target=server.run, name="morphology-api", daemon=True)
    thread.start()
    if not wait_until_healthy(url):
        server.should_exit = True
        raise RuntimeError(f"Desktop API did not become healthy in 15 seconds. Log: {log_path}")
    logger.info("Desktop API ready at %s", url)
    logger.info("STARTUP backend_ready_seconds=%.3f", time.perf_counter() - started)

    try:
        if browser_fallback:
            import webbrowser

            webbrowser.open(url)
            thread.join()
        else:
            runtime_available = webview2_runtime_available()
            logger.info("WebView2 runtime available=%s", runtime_available)
            if sys.platform == "win32" and not runtime_available:
                raise RuntimeError(
                    "未检测到 Microsoft Edge WebView2 Runtime。请从微软官方网站安装后重试。"
                )
            try:
                import webview
            except ImportError as exc:
                raise RuntimeError(
                    "pywebview is required for the native window. "
                    "Install morphology-toolkit[desktop] or use --browser. "
                    f"Log: {log_path}"
                ) from exc
            webview.create_window(
                "Morphology Studio",
                url,
                width=1440,
                height=900,
                min_size=(1100, 700),
                resizable=True,
            )
            logger.info("STARTUP window_created_seconds=%.3f", time.perf_counter() - started)
            backend = native_webview_backend()
            logger.info("Native webview backend=%s", backend)
            webview.start(gui=backend)
    finally:
        server.should_exit = True
        thread.join(timeout=5)
    return 0


def main(browser_fallback: bool = False) -> int:
    try:
        if os.environ.get("MORPHOLOGY_VERIFY_INSTALLATION") == "1":
            return verify_installation()
        return _run(browser_fallback)
    except BaseException as exc:
        log_path = configure_logging()
        logging.getLogger(__name__).critical("Desktop startup failed", exc_info=True)
        show_error(f"Morphology Studio failed to start.\n\n{exc}\n\nLog: {log_path}")
        if sys.stdout is not None:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
