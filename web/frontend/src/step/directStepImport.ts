export interface StepSolid {
  name: string
  positions: Float32Array
  indices: Uint32Array
}

let nextRequestId = 1
let worker: Worker | undefined
const pending = new Map<number, { resolve:(value:StepSolid[])=>void; reject:(reason:Error)=>void }>()

function stepWorker() {
  if (worker) return worker
  worker = new Worker(new URL('./StepWorker.ts', import.meta.url), { type: 'module' })
  worker.onmessage = (event) => {
    const request = pending.get(event.data.id)
    if (!request) return
    pending.delete(event.data.id)
    if (event.data.error) request.reject(new Error(event.data.error))
    else request.resolve((event.data.solids ?? []) as StepSolid[])
  }
  worker.onerror = (event) => {
    const error = new Error(event.message || 'STEP 解析 Worker 失败')
    for (const request of pending.values()) request.reject(error)
    pending.clear()
    worker?.terminate()
    worker = undefined
  }
  return worker
}

export function prewarmStepEngine(): Promise<void> {
  const id = nextRequestId++
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve: () => resolve(), reject })
    stepWorker().postMessage({ id, action: 'init' })
  })
}

function parseBuffer(buffer: ArrayBuffer): Promise<StepSolid[]> {
  const id = nextRequestId++
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject })
    stepWorker().postMessage({ id, action: 'parse', buffer }, [buffer])
  })
}

export function parseStep(file: File): Promise<StepSolid[]> {
  return file.arrayBuffer().then(parseBuffer)
}

export async function parseStepPath(path: string): Promise<StepSolid[]> {
  const response = await fetch(`/api/models/step-source?path=${encodeURIComponent(path)}`)
  if (!response.ok) throw new Error(await response.text())
  return parseBuffer(await response.arrayBuffer())
}

function normal(a: number[], b: number[], c: number[]) {
  const ab = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]
  const ac = [c[0] - a[0], c[1] - a[1], c[2] - a[2]]
  const value = [
    ab[1] * ac[2] - ab[2] * ac[1],
    ab[2] * ac[0] - ab[0] * ac[2],
    ab[0] * ac[1] - ab[1] * ac[0],
  ]
  const length = Math.hypot(...value) || 1
  return value.map((item) => item / length)
}

export function binaryStl(solid: StepSolid): Uint8Array {
  const triangleCount = Math.floor(solid.indices.length / 3)
  const bytes = new Uint8Array(84 + triangleCount * 50)
  const view = new DataView(bytes.buffer)
  new TextEncoder().encodeInto('Morphology Studio OpenCascade STEP import', bytes.subarray(0, 80))
  view.setUint32(80, triangleCount, true)
  let offset = 84
  for (let triangle = 0; triangle < triangleCount; triangle += 1) {
    const points = [0, 1, 2].map((corner) => {
      const vertex = solid.indices[triangle * 3 + corner] * 3
      return [solid.positions[vertex], solid.positions[vertex + 1], solid.positions[vertex + 2]]
    })
    const values = [...normal(points[0], points[1], points[2]), ...points.flat()]
    for (const value of values) {
      view.setFloat32(offset, value, true)
      offset += 4
    }
    view.setUint16(offset, 0, true)
    offset += 2
  }
  return bytes
}

export function toBase64(bytes: Uint8Array): string {
  let result = ''
  const block = 0x8000
  for (let offset = 0; offset < bytes.length; offset += block) {
    result += String.fromCharCode(...bytes.subarray(offset, offset + block))
  }
  return btoa(result)
}
