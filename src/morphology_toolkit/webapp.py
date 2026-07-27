from __future__ import annotations

from pathlib import Path


def create_app():
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import HTMLResponse
    except ImportError as exc:
        raise RuntimeError("Web UI requires 'pip install morphology-toolkit[web]'") from exc
    from morphology_toolkit.importers import DirectoryImporter, UrdfImporter, detect_format
    app = FastAPI(title="Morphology Toolkit")
    @app.get("/", response_class=HTMLResponse)
    def home():
        return """<!doctype html><html><head><meta charset='utf-8'><title>Morphology Toolkit</title><style>body{font:16px system-ui;background:#10151d;color:#e7edf5;max-width:1100px;margin:auto;padding:3rem}input,button{padding:.7rem;margin:.3rem;background:#1d2733;color:white;border:1px solid #506070;border-radius:6px}pre{background:#18212b;padding:1rem;overflow:auto}.grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem}</style></head><body><h1>Morphology Toolkit</h1><p>通用模型扫描与结构预览（源文件只读）</p><input id=p size=80 placeholder='URDF 或模型目录路径'><button onclick='scan()'>分析</button><div class=grid><section><h2>候选与结构</h2><pre id=o>等待输入…</pre></section><section><h2>三维预览</h2><p>基础版本提供结构数据 API；完整 Three.js 编辑器将在后续增量中接入。</p></section></div><script>async function scan(){let r=await fetch('/api/analyze?path='+encodeURIComponent(p.value));o.textContent=JSON.stringify(await r.json(),null,2)}</script></body></html>"""
    @app.get("/api/analyze")
    def analyze(path: str):
        target = Path(path)
        if not target.exists(): raise HTTPException(404, "Path not found")
        fmt = detect_format(target)
        if target.is_dir():
            data = DirectoryImporter().analyze(target)
            return {"format": fmt, "entries": [{"path": str(item.path), "format": item.detected_format, "score": item.score, "confidence": item.confidence} for item in data.entry_candidates]}
        if fmt == "urdf":
            model = UrdfImporter().execute(target)
            return {"format": fmt, "robot_id": model.robot_id, "links": list(model.links), "joints": [vars(joint) for joint in model.joints.values()], "roots": model.root_links}
        return {"format": fmt, "message": "Use CLI for parameterized import"}
    return app


def run(port: int = 8000):
    try: import uvicorn
    except ImportError as exc: raise RuntimeError("Web UI requires 'pip install morphology-toolkit[web]'") from exc
    uvicorn.run(create_app(), host="127.0.0.1", port=port)

