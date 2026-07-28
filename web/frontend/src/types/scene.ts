export interface Transform { xyz: number[]; rpy: number[] }
export interface VisualGeometry { kind: string; size: number[]; scale: number[]; resource: string | null; origin: Transform; material: string | null }
export interface LinkNode { id: string; name: string; parentJoint: string | null; visuals: VisualGeometry[]; collisions: number; inertial: unknown }
export interface JointNode { id: string; name: string; type: string; parent: string; child: string; origin: Transform; axis: number[]; limit: Record<string, number>; value: number }
export interface SceneManifest { robotId: string | null; displayName?: string; rootLinks: string[]; links: LinkNode[]; joints: JointNode[]; resources: string[]; sourceFormat?: string }
export interface ValidationResult { errors: number; warnings: number; exportReady: boolean; diagnostics: Array<{severity: string; code: string; message: string; subject?: string}> }
