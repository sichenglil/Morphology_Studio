import * as THREE from 'three'
export type SupportedJointType='fixed'|'revolute'|'continuous'|'prismatic'
export interface JointRuntime {id:string;type:string;originObject:THREE.Object3D;motionObject:THREE.Object3D;axis:THREE.Vector3;lower?:number;upper?:number;currentValue:number;childLinkObject:THREE.Object3D}
export interface RobotRuntimeIndex {modelId:string;rootObject:THREE.Object3D;linksById:Map<string,THREE.Object3D>;jointsById:Map<string,JointRuntime>;visualsById:Map<string,THREE.Object3D>;collisionsById:Map<string,THREE.Object3D>}
