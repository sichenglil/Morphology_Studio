export type FrameRequest=(callback:FrameRequestCallback)=>number
export class RenderScheduler {
  private pending=false;private disposed=false;private continuous=new Set<string>();private last=0
  constructor(private render:(time:number)=>void,private raf:FrameRequest=callback=>window.requestAnimationFrame(callback),private cancel:(id:number)=>void=id=>window.cancelAnimationFrame(id)){void this.cancel}
  invalidate(){if(this.pending||this.disposed)return;this.pending=true;this.raf(time=>{this.pending=false;if(this.disposed)return;this.render(time);if(this.continuous.size)this.invalidate()})}
  startContinuous(reason:string){this.continuous.add(reason);this.invalidate()}
  stopContinuous(reason:string){this.continuous.delete(reason)}
  isContinuous(){return this.continuous.size>0}
  dispose(){this.disposed=true;this.continuous.clear();this.last=0}
}
