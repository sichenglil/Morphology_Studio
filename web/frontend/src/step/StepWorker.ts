/*
 * STEP tessellation adapted from Democratizing-Dexterous/step2urdf
 * commit 5c67a6768ce6767edf31aaa9e0737561363c315e (MIT).
 * This reduced worker keeps only offline OpenCascade loading and solid meshing.
 */
/* eslint-disable @typescript-eslint/no-explicit-any -- OpenCascade.js beta has no TypeScript API declarations. */

type SolidMesh = { name: string; positions: Float32Array; indices: Uint32Array }
type WorkerRequest = { id: number; action: 'init' | 'parse'; buffer?: ArrayBuffer }

let oc: any

function dispose(objects: any[]) {
  for (const object of objects.reverse()) {
    try { object?.delete?.() } catch { /* OpenCascade cleanup is best-effort. */ }
  }
}

async function openCascade() {
  if (!oc) {
    const initialize = (await import('opencascade.js')).default
    oc = await initialize()
  }
  return oc
}

function meshShape(shape: any, index: number): SolidMesh | null {
  const positions: number[] = []
  const indices: number[] = []
  let vertexOffset = 0
  const explorer = new oc.TopExp_Explorer_2(
    shape,
    oc.TopAbs_ShapeEnum.TopAbs_FACE,
    oc.TopAbs_ShapeEnum.TopAbs_SHAPE,
  )
  try {
    for (; explorer.More(); explorer.Next()) {
      const temporary: any[] = []
      try {
        const face = oc.TopoDS.Face_1(explorer.Current())
        const location = new oc.TopLoc_Location_1()
        temporary.push(location)
        const handle = oc.BRep_Tool.Triangulation(face, location, 0)
        if (handle.IsNull()) continue
        const triangulation = handle.get()
        const transform = location.Transformation()
        const nodeCount = triangulation.NbNodes()
        for (let nodeIndex = 1; nodeIndex <= nodeCount; nodeIndex += 1) {
          const point = triangulation.Node(nodeIndex).Transformed(transform)
          positions.push(point.X(), point.Y(), point.Z())
        }
        const reversed = face.Orientation_1() === oc.TopAbs_Orientation.TopAbs_REVERSED
        for (let triangleIndex = 1; triangleIndex <= triangulation.NbTriangles(); triangleIndex += 1) {
          const triangle = triangulation.Triangle(triangleIndex)
          let first = triangle.Value(1) - 1 + vertexOffset
          let second = triangle.Value(2) - 1 + vertexOffset
          const third = triangle.Value(3) - 1 + vertexOffset
          if (reversed) [first, second] = [second, first]
          indices.push(first, second, third)
        }
        vertexOffset += nodeCount
      } finally {
        dispose(temporary)
      }
    }
  } finally {
    explorer.delete()
  }
  if (!positions.length || !indices.length) return null
  return {
    name: `link_${index}`,
    positions: new Float32Array(positions),
    indices: new Uint32Array(indices),
  }
}

async function parseStep(buffer: ArrayBuffer): Promise<SolidMesh[]> {
  await openCascade()
  const temporary: any[] = []
  const filename = `model_${Date.now()}.step`
  try {
    oc.FS.createDataFile('/', filename, new Uint8Array(buffer), true, true, true)
    const reader = new oc.STEPControl_Reader_1()
    temporary.push(reader)
    const status = reader.ReadFile(filename)
    if (status !== oc.IFSelect_ReturnStatus.IFSelect_RetDone) {
      throw new Error('OpenCascade 无法读取该 STEP 文件')
    }
    const progress = new oc.Message_ProgressRange_1()
    temporary.push(progress)
    reader.TransferRoots(progress)
    const root = reader.OneShape()
    temporary.push(root)
    const mesher = new oc.BRepMesh_IncrementalMesh_2(root, 0.1, false, 0.5, false)
    temporary.push(mesher)

    const solids: SolidMesh[] = []
    const explorer = new oc.TopExp_Explorer_2(
      root,
      oc.TopAbs_ShapeEnum.TopAbs_SOLID,
      oc.TopAbs_ShapeEnum.TopAbs_SHAPE,
    )
    try {
      for (; explorer.More(); explorer.Next()) {
        const mesh = meshShape(explorer.Current(), solids.length)
        if (mesh) solids.push(mesh)
      }
    } finally {
      explorer.delete()
    }
    if (!solids.length) {
      const mesh = meshShape(root, 0)
      if (mesh) solids.push(mesh)
    }
    if (!solids.length) throw new Error('STEP 文件中没有可三角化的实体')
    return solids
  } finally {
    try { oc?.FS.unlink(`/${filename}`) } catch { /* Ignore missing virtual file. */ }
    dispose(temporary)
  }
}

self.onmessage = async (event: MessageEvent<WorkerRequest>) => {
  try {
    if (event.data.action === 'init') {
      await openCascade()
      self.postMessage({ id: event.data.id, ready: true })
      return
    }
    if (!event.data.buffer) throw new Error('STEP 请求缺少文件数据')
    const solids = await parseStep(event.data.buffer)
    const transfer = solids.flatMap((solid) => [solid.positions.buffer, solid.indices.buffer])
    self.postMessage({ id: event.data.id, solids }, { transfer })
  } catch (error) {
    self.postMessage({
      id: event.data.id,
      error: error instanceof Error ? error.message : String(error),
    })
  }
}
