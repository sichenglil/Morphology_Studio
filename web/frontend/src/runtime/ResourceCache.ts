import * as THREE from 'three';import {STLLoader} from 'three/examples/jsm/loaders/STLLoader.js';import {ColladaLoader} from 'three/examples/jsm/loaders/ColladaLoader.js';import {performanceMetrics} from './PerformanceMetrics'
interface Entry{source:Promise<THREE.Object3D>;refs:number}
export class ResourceCache {private entries=new Map<string,Entry>();private defaultMaterial=new THREE.MeshStandardMaterial({color:0x8ca9c7,roughness:.58,metalness:.12})
 async acquire(url:string){let entry=this.entries.get(url);if(!entry){performanceMetrics.increment('meshLoads');entry={source:this.load(url),refs:0};this.entries.set(url,entry)}entry.refs++;return(await entry.source).clone(true)}
 release(url:string){const entry=this.entries.get(url);if(!entry||--entry.refs>0)return;this.entries.delete(url);void entry.source.then(source=>source.traverse(o=>{const mesh=o as THREE.Mesh;if(mesh.geometry)mesh.geometry.dispose()}))}
 dispose(){for(const entry of this.entries.values())void entry.source.then(source=>source.traverse(o=>{const m=o as THREE.Mesh;if(m.geometry)m.geometry.dispose()}));this.entries.clear();this.defaultMaterial.dispose()}
 private async load(url:string){if(url.toLowerCase().includes('.dae'))return(await new ColladaLoader().loadAsync(url)).scene;const geometry=await new STLLoader().loadAsync(url);geometry.computeVertexNormals();return new THREE.Mesh(geometry,this.defaultMaterial)}
}
