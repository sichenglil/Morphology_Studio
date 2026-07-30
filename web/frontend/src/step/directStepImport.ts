export interface StepSolid {
  name: string
  positions: Float32Array
  indices: Uint32Array
}

let nextRequestId = 1

export function parseStep(file: File): Promise<StepSolid[]> {
  return file.arrayBuffer().then((buffer) => new Promise((resolve, reject) => {
    const worker = new Worker(new URL('./StepWorker.ts', import.meta.url), { type: 'module' })
    const id = nextRequestId++
    worker.onmessage = (event) => {
      if (event.data.id !== id) return
      worker.terminate()
      if (event.data.error) reject(new Error(event.data.error))
      else resolve(event.data.solids as StepSolid[])
    }
    worker.onerror = (event) => {
      worker.terminate()
      reject(new Error(event.message || 'STEP 解析 Worker 失败'))
    }
    worker.postMessage({ id, buffer }, [buffer])
  }))
}

export async function parseStepPath(path: string): Promise<StepSolid[]> {
  const response = await fetch(`/api/models/step-source?path=${encodeURIComponent(path)}`)
  if (!response.ok) throw new Error(await response.text())
  const buffer = await response.arrayBuffer()
  return new Promise((resolve, reject) => {
    const worker = new Worker(new URL('./StepWorker.ts', import.meta.url), { type: 'module' })
    const id = nextRequestId++
    worker.onmessage = (event) => {
      if (event.data.id !== id) return
      worker.terminate()
      if (event.data.error) reject(new Error(event.data.error))
      else resolve(event.data.solids as StepSolid[])
    }
    worker.onerror = (event) => {
      worker.terminate()
      reject(new Error(event.message || 'STEP 解析 Worker 失败'))
    }
    worker.postMessage({ id, buffer }, [buffer])
  })
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
