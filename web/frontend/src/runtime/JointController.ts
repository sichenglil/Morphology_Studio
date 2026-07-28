import type {RobotRuntimeIndex,JointRuntime} from './RobotRuntimeIndex';import type {RenderScheduler} from './RenderScheduler';import {performanceMetrics} from './PerformanceMetrics'
export class JointController {
  constructor(private runtime:RobotRuntimeIndex,private scheduler:RenderScheduler){}
  setJoint(id:string,value:number){const start=performance.now(),joint=this.runtime.jointsById.get(id);if(!joint)throw new Error(`Unknown joint: ${id}`);const next=this.clamp(joint,value);this.apply(joint,next);performanceMetrics.recordFk(performance.now()-start);performanceMetrics.pending(1);this.scheduler.invalidate();return next}
  setMany(values:Record<string,number>){for(const [id,value] of Object.entries(values))this.setJoint(id,value)}
  reset(){for(const joint of this.runtime.jointsById.values())if(joint.type!=='fixed')this.apply(joint,0);this.scheduler.invalidate()}
  private clamp(joint:JointRuntime,value:number){if(!Number.isFinite(value))throw new Error('Joint value must be finite');if(joint.type==='fixed')throw new Error('Fixed joints cannot move');if(!['revolute','continuous','prismatic'].includes(joint.type))throw new Error(`${joint.type} joints are not supported for live preview`);return Math.min(joint.upper??Infinity,Math.max(joint.lower??-Infinity,value))}
  private apply(joint:JointRuntime,value:number){joint.currentValue=value;joint.motionObject.position.set(0,0,0);joint.motionObject.quaternion.identity();if(joint.type==='prismatic')joint.motionObject.position.copy(joint.axis).multiplyScalar(value);else joint.motionObject.quaternion.setFromAxisAngle(joint.axis,value);joint.motionObject.updateMatrix();joint.motionObject.updateWorldMatrix(false,true)}
}
