// Runs the REAL Three.js math (same version as the page) to test sphere
// hit-testing, including group rotation and matrixWorld — the parts the
// pure-math test could not cover.
const THREE=require('three');

const RAW=[[12.0,161.71,3.0],[21.64,161.34,3.95],[33.39,159.88,5.2],[47.73,156.52,6.84],
           [65.05,149.97,9.0],[85.34,138.1,11.84],[107.49,117.76,15.59],
           [127.81,84.89,20.52],[151.71,36.0,27.0]];
const SX=0.115, CXO=82, CYO=100;

function scene(W,H,rotY){
  const cam=new THREE.PerspectiveCamera(46,W/H,0.1,220);
  const group=new THREE.Group();
  const spheres=[];
  RAW.forEach((c,i)=>{
    const x=(c[0]-CXO)*SX*1.35, y=-(c[1]-CYO)*SX*1.35, r=c[2]*SX;
    const shell=new THREE.Object3D(); shell.position.set(x,y,0);
    group.add(shell);
    spheres.push({shell,r,base:new THREE.Vector3(x,y,0),i,hs:1});
  });
  if(W<700){cam.position.set(0,-1,52);group.position.set(0,-2,0);group.scale.setScalar(.92);}
  else if(W<1000){cam.position.set(0,0,44);group.position.set(0,-1,0);group.scale.setScalar(.96);}
  else{cam.position.set(0,1.5,34);group.position.set(0,0,0);group.scale.setScalar(1);}
  cam.updateProjectionMatrix();
  cam.updateMatrixWorld(true);          // <-- required for .project()
  group.rotation.y=rotY;
  group.updateMatrixWorld(true);
  return {cam,group,spheres};
}

// EXACT copy of the page's project()
function project(sp,cam,group,W,H){
  const c=sp.shell.position.clone(); c.applyMatrix4(group.matrixWorld);
  const v=c.clone().project(cam);
  if(v.z>1) return null;
  const x=(v.x*.5+.5)*W, y=(-v.y*.5+.5)*H;
  const edge=c.clone(); edge.x+=sp.r*(sp.hs||1);
  const ev=edge.project(cam);
  const r=Math.abs((ev.x*.5+.5)*W - x);
  return {x,y,r};
}
function pick(px,py,spheres,cam,group,W,H,floor){
  let best=-1,bestD=Infinity;
  for(let i=0;i<spheres.length;i++){
    const p=project(spheres[i],cam,group,W,H); if(!p)continue;
    const d=Math.hypot(px-p.x,py-p.y);
    const hit=Math.max(p.r,floor);
    if(d<=hit&&d<bestD){bestD=d;best=i;}
  }
  return best;
}

const VIEWS=[[1920,1080],[1600,1000],[1440,900],[1280,800]];
const ROTS=[0,0.2,-0.2,0.42,-0.42];   // full mouse-parallax range
let bad=0,total=0;
console.log('Testing every sphere at every viewport x rotation combination');
console.log('(hovering a sphere\'s own centre must select that sphere)\n');
for(const [W,H] of VIEWS){
  for(const rot of ROTS){
    const {cam,group,spheres}=scene(W,H,rot);
    const miss=[];
    for(const sp of spheres){
      const p=project(sp,cam,group,W,H); if(!p)continue;
      total++;
      const got=pick(p.x,p.y,spheres,cam,group,W,H,14);
      if(got!==sp.i){miss.push(`s${sp.i+1}->s${got+1}`);bad++;}
    }
    console.log(`  ${W}x${H} rotY=${rot.toFixed(2)}  ${miss.length?'MISS: '+miss.join(' '):'all 9 ok'}`);
  }
}
console.log(`\n${total-bad}/${total} correct, ${bad} mis-picks`);

// how big is each sphere's clickable area, really?
console.log('\nDrawn radius per sphere @1440x900 (hit floor = 14px):');
const {cam,group,spheres}=scene(1440,900,0);
spheres.forEach(sp=>{
  const p=project(sp,cam,group,1440,900);
  console.log(`  sphere ${sp.i+1}: drawn r=${p.r.toFixed(1)}px  hit=${Math.max(p.r,14).toFixed(1)}px  at (${p.x.toFixed(0)},${p.y.toFixed(0)})`);
});

// ---- how hard is each sphere to actually HIT? ----
console.log('\n--- hit-target analysis @1440x900 ---');
console.log('Fitts\'s law: targets under ~24px diameter are fiddly for a moving pointer.');
const S=scene(1440,900,0);
S.spheres.forEach(sp=>{
  const p=project(sp,S.cam,S.group,1440,900);
  const dia=Math.max(p.r,14)*2;
  console.log(`  sphere ${sp.i+1}: target diameter ${dia.toFixed(0)}px  ${dia<28?'<-- FIDDLY':''}`);
});

// ---- would a bigger floor cause wrong picks? ----
console.log('\n--- does raising the hit floor break neighbour selection? ---');
for(const floor of [14,20,26,32,40]){
  let bad=0,tot=0;
  for(const [W,H] of VIEWS){
    for(const rot of ROTS){
      const s=scene(W,H,rot);
      for(const sp of s.spheres){
        const p=project(sp,s.cam,s.group,W,H); if(!p)continue;
        tot++;
        if(pick(p.x,p.y,s.spheres,s.cam,s.group,W,H,floor)!==sp.i) bad++;
      }
    }
  }
  console.log(`  floor=${String(floor).padStart(2)}px  ->  ${tot-bad}/${tot} correct  ${bad?'('+bad+' wrong)':'OK'}`);
}
