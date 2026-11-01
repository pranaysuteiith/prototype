'use strict';
const $=id=>document.getElementById(id);let instance=null,starting=false,muted=false,ready=false;const root='Doro Painted Cafe - Imported';
function send(method,value){if(instance)instance.SendMessage(root,method,String(value));}
function notify(text){$('toast').textContent=text;$('toast').classList.add('show');setTimeout(()=>$('toast').classList.remove('show'),2200);}
function soundUI(){ $('mute').setAttribute('aria-pressed',String(muted));$('mute').querySelector('span').textContent=muted?'Sound off':'Sound on';send('SetMuted',muted?'1':'0'); }
$('mute').addEventListener('click',()=>{muted=!muted;soundUI();});
$('volume').addEventListener('input',()=>send('SetVolume',$('volume').value));$('blur').addEventListener('change',()=>send('SetBlur',$('blur').checked?'1':'0'));
$('fullscreen').addEventListener('click',async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.querySelector('.game').requestFullscreen();$('unity-canvas').focus();}catch{notify('Fullscreen is unavailable in this browser.');}});
$('share').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href.split('#')[0]);notify('Link copied — share a little calm.');}catch{prompt('Copy this link:',location.href);}});
function fail(message){$('loading').hidden=true;$('welcome').hidden=true;$('error').hidden=false;$('error-text').textContent=message;$('hint').textContent='Please try again';}
window.addEventListener('unhandledrejection',event=>{if(starting && !ready)fail('The café could not load. Please use a current desktop browser with WebGL 2 enabled and try again.');});
$('unity-canvas').addEventListener('contextmenu',e=>e.preventDefault());
window.addEventListener('keydown',e=>{if(document.activeElement===$('unity-canvas')&&['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].includes(e.key))e.preventDefault();});
$('enter').addEventListener('click',async()=>{
 if(starting)return;starting=true;$('welcome').hidden=true;$('loading').hidden=false;
 try{
  const response=await fetch('build-config.json',{cache:'no-store'});if(!response.ok)throw Error('Build configuration unavailable.');const config=await response.json();
  let dataUrl=config.dataUrl;
  if(config.dataParts){
   let loaded=0;
   const parts=await Promise.all(config.dataParts.map(async path=>{const r=await fetch(path);if(!r.ok)throw Error('Scene download failed');const buffer=await r.arrayBuffer();loaded+=buffer.byteLength;$('progress').value=.55*loaded/config.dataBytes;$('load-text').textContent=`Opening the neighbourhood · ${Math.round(100*loaded/config.dataBytes)}%`;return buffer;}));
   dataUrl=URL.createObjectURL(new Blob(parts,{type:'application/octet-stream'}));
  }
  const loader=document.createElement('script');loader.src=config.loaderUrl;await new Promise((resolve,reject)=>{loader.onload=resolve;loader.onerror=reject;document.body.appendChild(loader);});
  const canvas=$('unity-canvas');
  instance=await createUnityInstance(canvas,{dataUrl:dataUrl,frameworkUrl:config.frameworkUrl,codeUrl:config.codeUrl,streamingAssetsUrl:'StreamingAssets',companyName:'Doro',productName:'Doro Café',productVersion:'2.0',matchWebGLToCanvasSize:true,devicePixelRatio:Math.min(window.devicePixelRatio||1,1.5)},p=>{$('progress').value=config.dataParts ? 0.55 + 0.45*p : p;$('load-text').textContent=p<.9?`Bringing the neighbourhood to life · ${Math.round(p*100)}%`:'Pouring the coffee…';});
  if(config.dataParts)URL.revokeObjectURL(dataUrl);
  ready=true;$('loading').hidden=true;canvas.style.visibility='visible';canvas.focus();$('hint').textContent='Arrow keys to walk · M to mute · B for soft focus';
  send('SetVolume',$('volume').value);send('SetMuted',muted?'1':'0');send('SetBlur',$('blur').checked?'1':'0');
  // Browser audio can require a gesture after Unity finishes loading.
  document.querySelector('.game').addEventListener('pointerdown',()=>{try{if(typeof WEBAudio!=='undefined'&&WEBAudio.audioContext)WEBAudio.audioContext.resume();}catch{}}, {passive:true});
 }catch(error){console.error(error);fail('We couldn’t open the café. Check your connection, allow WebGL in a current desktop browser, then try again.');}
});
document.addEventListener('keydown',e=>{if(ready&&document.activeElement===$('unity-canvas')){if(e.key.toLowerCase()==='m'){muted=!muted;/* Unity handles the same key; update only the page. */$('mute').setAttribute('aria-pressed',String(muted));$('mute').querySelector('span').textContent=muted?'Sound off':'Sound on';}if(e.key.toLowerCase()==='b')$('blur').checked=!$('blur').checked;}});

document.addEventListener('visibilitychange',()=>send('SetMuted',document.hidden||muted?'1':'0'));
