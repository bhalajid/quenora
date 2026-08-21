// Replicates the EXACT projection + pick() logic from index.html so we can
// test sphere hit-testing headlessly, with no browser.
const RAW=[[12.0,161.71,3.0],[21.64,161.34,3.95],[33.39,159.88,5.2],[47.73,156.52,6.84],
           [65.05,149.97,9.0],[85.34,138.1,11.84],[107.49,117.76,15.59],
           [127.81,84.89,20.52],[151.71,36.0,27.0]];
const SX=0.115, CXO=82, CYO=100, FOV=46;

function build(){
  return RAW.map((c,i)=>({
    i,
    x:(c[0]-CXO)*SX*1.35,
    y:-(c[1]-CYO)*SX*1.35,
    z:0,
    r:c[2]*SX
  }));
}

// mirrors frameCamera()
function camFor(W){
  if(W<700)  return {pos:[0,-1,52], gy:-2, gs:0.92};
  if(W<1000) return {pos:[0,0,44],  gy:-1, gs:0.96};
  return {pos:[0,1.5,34], gy:0, gs:1};
}

// mirrors project(): perspective camera looking down -Z, no lookAt
function project(sp,W,H,cam){
  const gs=cam.gs;
  const wx=sp.x*gs, wy=sp.y*gs+cam.gy, wz=sp.z*gs;
  const [cx,cy,cz]=cam.pos;
  const d=cz-wz;                       // depth in front of camera
  if(d<=0) return null;
  const aspect=W/H;
  const t=Math.tan(FOV*Math.PI/180/2);
  const ndcX=(wx-cx)/(t*aspect*d);
  const ndcY=(wy-cy)/(t*d);
  const x=(ndcX*0.5+0.5)*W, y=(-ndcY*0.5+0.5)*H;
  // drawn radius in px
  const rpx=(sp.r*gs)/(t*aspect*d)*0.5*W;
  return {x,y,r:rpx};
}

function pick(px,py,spheres,W,H,cam,floor){
  let best=-1,bestD=Infinity;
  for(const sp of spheres){
    const p=project(sp,W,H,cam); if(!p) continue;
    const d=Math.hypot(px-p.x,py-p.y);
    const hit=Math.max(p.r,floor);
    if(d<=hit && d<bestD){bestD=d;best=sp.i;}
  }
  return best;
}

const VIEWPORTS=[[1920,1080],[1440,900],[1280,800],[900,700],[420,860]];
let fails=0;

for(const [W,H] of VIEWPORTS){
  const cam=camFor(W), sph=build();
  console.log(`\n=== ${W}x${H} ===`);
  console.log('  #   screenX   screenY   drawn_r   in-viewport?  self-pick?');
  for(const sp of sph){
    const p=project(sp,W,H,cam);
    if(!p){ console.log(`  ${sp.i+1}   OFF-CAMERA`); fails++; continue; }
    const vis = p.x>=0 && p.x<=W && p.y>=0 && p.y<=H;
    const got = pick(p.x,p.y,sph,W,H,cam,14);
    const ok  = got===sp.i;
    if(vis && !ok) fails++;
    console.log(`  ${sp.i+1}  ${p.x.toFixed(0).padStart(7)}  ${p.y.toFixed(0).padStart(7)}  ${p.r.toFixed(1).padStart(7)}   ${(vis?'yes':'NO ').padStart(10)}   ${ok?'ok':'MISMATCH->'+(got+1)}`);
  }
}
console.log(`\nfailures: ${fails}`);
