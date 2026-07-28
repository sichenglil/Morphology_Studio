export interface MetricsSnapshot {fps:number;frameMs:number;fkMs:number;renderMs:number;drawCalls:number;triangles:number;pendingJointUpdates:number;backendCommits:number;sceneRebuilds:number;meshLoads:number;workspaceSaves:number}
export class PerformanceMetrics {
  private frames:number[]=[]; private state:MetricsSnapshot={fps:0,frameMs:0,fkMs:0,renderMs:0,drawCalls:0,triangles:0,pendingJointUpdates:0,backendCommits:0,sceneRebuilds:0,meshLoads:0,workspaceSaves:0}
  recordFrame(ms:number){if(ms<=0||ms>100)return;this.frames.push(ms);if(this.frames.length>120)this.frames.shift();this.state.frameMs=this.average(this.frames);this.state.fps=this.state.frameMs?1000/this.state.frameMs:0}
  recordFk(ms:number){this.state.fkMs=ms} recordRender(ms:number,calls:number,triangles:number){this.state.renderMs=ms;this.state.drawCalls=calls;this.state.triangles=triangles}
  increment(key:'backendCommits'|'sceneRebuilds'|'meshLoads'|'workspaceSaves',by=1){this.state[key]+=by}
  pending(value:number){this.state.pendingJointUpdates=value}
  snapshot():MetricsSnapshot{return {...this.state}}
  reset(){this.frames=[];Object.keys(this.state).forEach(key=>(this.state as unknown as Record<string,number>)[key]=0)}
  private average(values:number[]){return values.length?values.reduce((a,b)=>a+b,0)/values.length:0}
}
export const performanceMetrics=new PerformanceMetrics()
