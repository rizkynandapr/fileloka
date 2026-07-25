(function(){
'use strict';
/* ================= core utils ================= */
const $=(s,r=document)=>r.querySelector(s);
const $$=(s,r=document)=>Array.from(r.querySelectorAll(s));
const on=(el,ev,fn,o)=>el.addEventListener(ev,fn,o);
const DEFAULT_TITLE=document.title;

function h(html){const t=document.createElement('template');t.innerHTML=html.trim();return t.content.firstElementChild;}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function fmtBytes(n){
  if(!isFinite(n))return '—';
  const u=['B','KB','MB','GB'];let i=0;
  while(n>=1024&&i<u.length-1){n/=1024;i++;}
  return (n<10&&i>0?n.toFixed(1):Math.round(n))+' '+u[i];
}
function baseName(name){return name.replace(/\.[^.]+$/,'');}
async function readBytes(file){return new Uint8Array(await file.arrayBuffer());}
function downloadBlob(blob,name){
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);a.download=name;
  document.body.appendChild(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(a.href),5000);
}
function toast(msg,isErr){
  const t=h('<div class="toast'+(isErr?' err':'')+'"></div>');
  t.textContent=msg;$('#toasts').appendChild(t);
  setTimeout(()=>t.remove(),3600);
}
function setBusy(btn,busy,busyText){
  if(busy){btn.dataset.label=btn.innerHTML;btn.textContent=busyText||'Working…';btn.disabled=true;}
  else{if(btn.dataset.label)btn.innerHTML=btn.dataset.label;btn.disabled=false;}
}
const isPdf=f=>f.type==='application/pdf'||/\.pdf$/i.test(f.name);
const isImg=f=>/^image\/(png|jpe?g|webp)$/.test(f.type)||/\.(png|jpe?g|webp)$/i.test(f.name);

/* ================= shared icons ================= */
const I={
  dl:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12m0 0 4-4m-4 4-4-4M4 19h16"/></svg>',
  up:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 16V4m0 0 4 4m-4-4-4 4"/><path d="M3 15v3a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-3"/></svg>',
  ok:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>',
  shield:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l7 3v5c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/><path d="m9.5 11.5 2 2 3.5-3.5"/></svg>',
  updown:{u:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 14 6-6 6 6"/></svg>',
          d:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 10 6 6 6-6"/></svg>',
          x:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 6l12 12M18 6 6 18"/></svg>'},
  copy:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
  refresh:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 8A9 9 0 0 0 5 6.5L3.5 8M3.5 16a9 9 0 0 0 15.5 1.5l1.5-1.5"/><path d="M3.5 3.5V8H8M20.5 20.5V16H16"/></svg>'
};

/* ================= lazy CDN libraries ================= */
const CDN={
  pdfLib:{src:'lib/pdf-lib.min.js',ok:()=>window.PDFLib},
  pdfjs:{src:'lib/pdf.min.js',ok:()=>window.pdfjsLib,
         after(){window.pdfjsLib.GlobalWorkerOptions.workerSrc='lib/pdf.worker.min.js';}},
  jszip:{src:'lib/jszip.min.js',ok:()=>window.JSZip},
  qrcode:{src:'lib/qrcode.min.js',ok:()=>window.QRCode}
};
const libCache={};
function loadLib(name){
  if(libCache[name])return libCache[name];
  const c=CDN[name];
  libCache[name]=new Promise((res,rej)=>{
    if(c.ok()){c.after&&c.after();return res();}
    const s=document.createElement('script');s.src=c.src;
    s.onload=()=>{c.after&&c.after();res();};
    s.onerror=()=>{delete libCache[name];rej(new Error('A required library failed to load. Check your connection and try again.'));};
    document.head.appendChild(s);
  });
  return libCache[name];
}

/* ================= theme ================= */
const SUN='M12 8a4 4 0 1 0 .01 8A4 4 0 0 0 12 8zM12 3v1.5M12 19.5V21M3 12h1.5M19.5 12H21M5.3 5.3l1.1 1.1M17.6 17.6l1.1 1.1M18.7 5.3l-1.1 1.1M6.4 17.6l-1.1 1.1';
const MOON='M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z';
let theme=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
function applyTheme(){
  document.documentElement.dataset.theme=theme;
  $('#themeIcon').setAttribute('d',theme==='dark'?SUN:MOON);
}
on($('#themeBtn'),'click',()=>{theme=theme==='dark'?'light':'dark';applyTheme();});

/* ================= router ================= */
const homeView=$('#view-home'),toolView=$('#view-tool'),mount=$('#toolMount');
const TOOLS={};
let pendingFiles=null;   // files handed over from a global drop
let activeIntake=null;   // {match, fn} registered by the open tool
const homeActive=()=>homeView.classList.contains('is-active');

function route(){
  const m=location.hash.match(/^#\/([a-z-]+)$/);
  const id=m&&m[1];
  activeIntake=null;
  if(id&&TOOLS[id]){
    homeView.classList.remove('is-active');
    toolView.classList.add('is-active');
    mount.innerHTML='';
    document.title=TOOLS[id].name+' — ToolDock';
    let files=null;
    if(pendingFiles){files=pendingFiles.filter(TOOLS[id].match);pendingFiles=null;if(!files.length)files=null;}
    TOOLS[id].mount(mount,files);
    window.scrollTo({top:0,behavior:'instant'});
  }else{
    toolView.classList.remove('is-active');
    homeView.classList.add('is-active');
    mount.innerHTML='';
    document.title=DEFAULT_TITLE;
  }
}
on(window,'hashchange',route);
on($('#backBtn'),'click',()=>{location.hash='';});
on($('#brandHome'),'click',e=>{e.preventDefault();location.hash='';});
$$('a[data-nav="home"]').forEach(a=>on(a,'click',e=>{e.preventDefault();location.hash='';}));

/* ================= search + category tabs ================= */
const cards=$$('#toolGrid .card'),gridEmpty=$('#gridEmpty'),searchInput=$('#searchInput');
let activeCat='all';
function filterCards(){
  const q=searchInput.value.trim().toLowerCase();let vis=0;
  cards.forEach(c=>{
    const okCat=activeCat==='all'||c.dataset.cat===activeCat;
    const hay=(c.querySelector('h3').textContent+' '+c.querySelector('p').textContent+' '+(c.dataset.k||'')).toLowerCase();
    const show=okCat&&(!q||hay.includes(q));
    c.classList.toggle('hidden',!show);if(show)vis++;
  });
  gridEmpty.classList.toggle('show',!vis);
}
on(searchInput,'input',filterCards);
$$('.tab').forEach(t=>on(t,'click',()=>{
  $$('.tab').forEach(x=>x.setAttribute('aria-selected',x===t?'true':'false'));
  activeCat=t.dataset.cat;filterCards();
}));
on(document,'keydown',e=>{
  const typing=/^(input|textarea|select)$/i.test(document.activeElement.tagName);
  if(e.key==='/'&&homeActive()&&!typing){e.preventDefault();searchInput.focus();}
  if(e.key==='Escape'&&!homeActive()&&!typing){location.hash='';}
});

/* ================= global drag & drop ================= */
const overlay=$('#dropOverlay');
const hasFiles=e=>e.dataTransfer&&Array.from(e.dataTransfer.types).includes('Files');
let dragDepth=0;
on(window,'dragenter',e=>{
  if(!hasFiles(e))return;e.preventDefault();
  if(homeActive()){dragDepth++;overlay.classList.add('show');}
});
on(window,'dragover',e=>{if(hasFiles(e))e.preventDefault();});
on(window,'dragleave',e=>{
  if(!hasFiles(e))return;
  if(homeActive()){dragDepth=Math.max(0,dragDepth-1);if(!dragDepth)overlay.classList.remove('show');}
});
on(window,'drop',e=>{
  if(!hasFiles(e))return;e.preventDefault();
  dragDepth=0;overlay.classList.remove('show');
  const files=Array.from(e.dataTransfer.files);
  if(!files.length)return;
  if(!homeActive()&&activeIntake){
    const ok=files.filter(activeIntake.match);
    if(ok.length)activeIntake.fn(ok);
    else toast('This tool works with '+activeIntake.label+'.',true);
    return;
  }
  openChooser(files);
});

/* ================= drop chooser ================= */
const chooser=$('#chooser'),chList=$('#chList'),chSub=$('#chSub');
function openChooser(files){
  const pdfs=files.filter(isPdf),imgs=files.filter(isImg);
  if(!pdfs.length&&!imgs.length){toast('Drop PDF or image files (JPG, PNG, WebP).',true);return;}
  const total=files.reduce((s,f)=>s+f.size,0);
  const parts=[];
  if(pdfs.length)parts.push(pdfs.length+' PDF'+(pdfs.length>1?'s':''));
  if(imgs.length)parts.push(imgs.length+' image'+(imgs.length>1?'s':''));
  chSub.textContent=parts.join(' + ')+' · '+fmtBytes(total)+' — pick a tool:';
  const opts=[];
  if(pdfs.length>1)opts.push('merge-pdf');
  if(pdfs.length)opts.push('compress-pdf','split-pdf','pdf-to-jpg');
  if(imgs.length)opts.push('compress-image','jpg-to-pdf','resize-image','convert-image');
  chList.innerHTML='';
  opts.forEach(id=>{
    const b=h('<button type="button"><span style="flex:1">'+esc(TOOLS[id].name)+'</span>'+
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h13m-5-5 5 5-5 5"/></svg></button>');
    on(b,'click',()=>{
      pendingFiles=files;chooser.classList.remove('show');
      if(location.hash==='#/'+id)route();else location.hash='#/'+id;
    });
    chList.appendChild(b);
  });
  chooser.classList.add('show');
}
on($('#chCancel'),'click',()=>chooser.classList.remove('show'));
on(chooser,'click',e=>{if(e.target===chooser)chooser.classList.remove('show');});

/* ================= shared tool UI ================= */
function toolShell(t,bodyHtml){
  return h('<div>'+
    '<div class="tool-head rise"><span class="ic">'+t.icon+'</span><div><h2>'+esc(t.name)+'</h2><p>'+esc(t.desc)+'</p></div></div>'+
    '<div class="tool-body rise" style="animation-delay:.05s">'+bodyHtml+'</div>'+
    '<p class="local-note">'+I.shield+'Runs 100% on your device — this file is never uploaded.</p>'+
  '</div>');
}
function dzHtml(strong,small){
  return '<div class="dz" tabindex="0" role="button" aria-label="'+esc(strong)+'">'+
    '<span class="dz-ic">'+I.up+'</span><strong>'+esc(strong)+'</strong><small>'+esc(small)+'</small>'+
    '<input type="file"></div>';
}
function wireDz(dzEl,{accept,multiple,onFiles,match,label}){
  const inp=dzEl.querySelector('input');
  if(accept)inp.accept=accept;
  inp.multiple=!!multiple;
  on(dzEl,'click',()=>inp.click());
  on(dzEl,'keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();inp.click();}});
  on(inp,'change',()=>{
    const fs=Array.from(inp.files).filter(match||(()=>true));
    if(fs.length)onFiles(fs);else if(inp.files.length)toast('This tool works with '+label+'.',true);
    inp.value='';
  });
  ['dragenter','dragover'].forEach(ev=>on(dzEl,ev,e=>{e.preventDefault();e.stopPropagation();dzEl.classList.add('drag');}));
  ['dragleave','drop'].forEach(ev=>on(dzEl,ev,e=>{e.preventDefault();dzEl.classList.remove('drag');}));
  on(dzEl,'drop',e=>{
    e.stopPropagation();
    const fs=Array.from(e.dataTransfer.files).filter(match||(()=>true));
    if(fs.length)onFiles(fs);else toast('This tool works with '+label+'.',true);
  });
  activeIntake={match:match||(()=>true),fn:onFiles,label:label||'these files'};
}
function progHtml(){return '<div class="prog"><div class="bar"><i></i></div><p class="plabel"></p></div>';}
function makeProg(root){
  const el=$('.prog',root),bar=$('.bar i',el),lab=$('.plabel',el);
  return{
    show(t){el.classList.add('show');bar.style.width='0%';lab.textContent=t||'';},
    set(i,n,t){bar.style.width=Math.round(100*i/n)+'%';lab.textContent=t||i+' / '+n;},
    hide(){el.classList.remove('show');}
  };
}
function resultHtml(){return '<div class="result"><h4>'+I.ok+'<span>Done</span></h4><p class="rstats"></p><div class="ritems"></div><div class="actions" style="margin-top:6px"></div></div>';}
function showResult(root,{title,stats,items,note}){
  const el=$('.result',root);
  $('h4 span',el).textContent=title||'Done';
  $('.rstats',el).innerHTML=stats||'';
  const ritems=$('.ritems',el),acts=$('.actions',el);
  ritems.innerHTML='';acts.innerHTML='';
  if(items.length===1){
    const b=h('<button class="btn btn-primary">'+I.dl+'Download '+esc(items[0].name)+'</button>');
    on(b,'click',()=>downloadBlob(items[0].blob,items[0].name));
    acts.appendChild(b);
  }else{
    items.slice(0,30).forEach(it=>{
      const row=h('<div style="display:flex;gap:10px;align-items:center"><span class="fname" style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:.9rem;font-weight:600">'+esc(it.name)+'</span><span class="fmeta" style="font-family:var(--font-mono);font-size:.76rem;color:var(--muted)">'+fmtBytes(it.blob.size)+'</span></div>');
      const b=h('<button class="mini-btn" aria-label="Download '+esc(it.name)+'">'+I.dl.replace('stroke-width="2"','stroke-width="1.8"')+'</button>');
      on(b,'click',()=>downloadBlob(it.blob,it.name));
      row.appendChild(b);ritems.appendChild(row);
    });
    if(items.length>30)ritems.appendChild(h('<p class="note">…and '+(items.length-30)+' more (use “Download all”).</p>'));
    const zipBtn=h('<button class="btn btn-primary">'+I.dl+'Download all (.zip)</button>');
    on(zipBtn,'click',async()=>{
      try{
        setBusy(zipBtn,true,'Zipping…');
        await loadLib('jszip');
        const zip=new JSZip();
        for(const it of items)zip.file(it.name,it.blob);
        const blob=await zip.generateAsync({type:'blob',compression:'DEFLATE'});
        downloadBlob(blob,(items.zipName||'tooldock-files')+'.zip');
      }catch(err){toast(err.message,true);}finally{setBusy(zipBtn,false);}
    });
    acts.appendChild(zipBtn);
  }
  if(note)acts.insertAdjacentHTML('afterend','<p class="note">'+note+'</p>');
  el.classList.add('show');
  el.scrollIntoView({behavior:'smooth',block:'nearest'});
}
function optRange(id,label,min,max,step,val,unit){
  return '<div class="opt"><label for="'+id+'">'+label+'</label>'+
    '<div style="display:flex;align-items:center;gap:10px"><input type="range" id="'+id+'" min="'+min+'" max="'+max+'" step="'+step+'" value="'+val+'">'+
    '<span class="range-val" data-for="'+id+'">'+val+(unit||'')+'</span></div></div>';
}
function wireRange(root,id,fmt){
  const r=$('#'+id,root),v=$('.range-val[data-for="'+id+'"]',root);
  const upd=()=>v.textContent=fmt?fmt(r.value):r.value;
  on(r,'input',upd);upd();return r;
}

/* ================= PDF helpers ================= */
async function pdfDocFrom(bytes){
  await loadLib('pdfLib');
  try{return await PDFLib.PDFDocument.load(bytes);}
  catch(err){
    if(/encrypt/i.test(String(err)))throw new Error('That PDF is password-protected — not supported yet.');
    throw new Error('Could not read this PDF. The file may be damaged.');
  }
}
function parseRanges(str,n){
  const out=[],seen=new Set();
  const tokens=String(str).split(',').map(s=>s.trim()).filter(Boolean);
  if(!tokens.length)throw new Error('Enter page numbers, e.g. 1-3, 7');
  for(const t of tokens){
    const m=t.match(/^(\d+)(?:\s*-\s*(\d+))?$/);
    if(!m)throw new Error('“'+t+'” is not a valid page or range.');
    let a=parseInt(m[1],10),b=m[2]?parseInt(m[2],10):a;
    if(a>b){const x=a;a=b;b=x;}
    if(a<1||b>n)throw new Error('Pages must be between 1 and '+n+'.');
    for(let p=a;p<=b;p++){if(!seen.has(p)){seen.add(p);out.push(p-1);}}
  }
  return out;
}
async function eachPdfPage(bytes,{scale=1.5,onPage,prog}={}){
  await loadLib('pdfjs');
  const pdf=await pdfjsLib.getDocument({data:bytes.slice()}).promise;
  const n=pdf.numPages;
  for(let i=1;i<=n;i++){
    const page=await pdf.getPage(i);
    const v1=page.getViewport({scale:1});
    const vp=page.getViewport({scale});
    const c=document.createElement('canvas');
    c.width=Math.ceil(vp.width);c.height=Math.ceil(vp.height);
    await page.render({canvasContext:c.getContext('2d'),viewport:vp}).promise;
    await onPage({canvas:c,index:i,total:n,ptW:v1.width,ptH:v1.height});
    page.cleanup();c.width=0;c.height=0;
    if(prog)prog.set(i,n,'Page '+i+' of '+n);
  }
  pdf.destroy();
  return n;
}
function canvasToBlob(c,type,q){
  return new Promise((res,rej)=>c.toBlob(b=>b?res(b):rej(new Error('Your browser could not encode this image format.')),type,q));
}
function makeSortableList(listEl,state,{badge,onChange}={}){
  function render(){
    listEl.innerHTML='';
    state.forEach((it,i)=>{
      const li=h('<li><span class="fname" title="'+esc(it.file.name)+'">'+esc(it.file.name)+'</span>'+
        (badge?badge(it):'')+'<span class="fmeta">'+fmtBytes(it.file.size)+'</span><span class="fbtns"></span></li>');
      const btns=$('.fbtns',li);
      const up=h('<button class="mini-btn" aria-label="Move up">'+I.updown.u+'</button>');
      const dn=h('<button class="mini-btn" aria-label="Move down">'+I.updown.d+'</button>');
      const rm=h('<button class="mini-btn" aria-label="Remove">'+I.updown.x+'</button>');
      up.disabled=i===0;dn.disabled=i===state.length-1;
      on(up,'click',()=>{const t=state[i-1];state[i-1]=state[i];state[i]=t;render();if(onChange)onChange();});
      on(dn,'click',()=>{const t=state[i+1];state[i+1]=state[i];state[i]=t;render();if(onChange)onChange();});
      on(rm,'click',()=>{state.splice(i,1);render();if(onChange)onChange();});
      btns.append(up,dn,rm);
      listEl.appendChild(li);
    });
  }
  return{render};
}

/* ================= 1 · Merge PDF ================= */
TOOLS['merge-pdf']={
  name:'Merge PDF',desc:'Combine several PDFs into one file, in the order you choose.',match:isPdf,
  icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="13" y="4" width="8" height="16" rx="2"/><path d="M3 9h6m0 0L7 7m2 2-2 2M3 15h6m0 0-2-2m2 2-2 2"/></svg>',
  mount(root,pre){
    const el=toolShell(this,
      dzHtml('Choose PDF files','or drop them anywhere on this page — add as many as you like')+
      '<ul class="flist"></ul>'+
      '<div class="actions"><button class="btn btn-primary" id="mergeGo" disabled>Merge PDFs</button>'+
      '<button class="btn btn-ghost btn-sm" id="mergeClear" hidden>Clear list</button></div>'+
      progHtml()+resultHtml());
    root.appendChild(el);
    const state=[];
    const goBtn=$('#mergeGo',el),clearBtn=$('#mergeClear',el),prog=makeProg(el);
    const list=makeSortableList($('.flist',el),state,{
      badge:it=>it.err?'<span class="badge err">locked</span>':(it.pages!=null?'<span class="badge">'+it.pages+' pg</span>':'<span class="badge">…</span>'),
      onChange:sync
    });
    function sync(){
      const ok=state.filter(x=>!x.err);
      goBtn.disabled=ok.length<2;
      goBtn.textContent=ok.length>=2?'Merge '+ok.length+' PDFs':'Merge PDFs';
      clearBtn.hidden=!state.length;
    }
    async function addFiles(fs){
      for(const f of fs){
        const it={file:f,bytes:null,pages:null,err:null};
        state.push(it);list.render();sync();
        try{
          it.bytes=await readBytes(f);
          const d=await pdfDocFrom(it.bytes);
          it.pages=d.getPageCount();
        }catch(err){it.err=err.message;toast(f.name+': '+err.message,true);}
        list.render();sync();
      }
    }
    wireDz($('.dz',el),{accept:'.pdf,application/pdf',multiple:true,onFiles:addFiles,match:isPdf,label:'PDF files'});
    on(clearBtn,'click',()=>{state.length=0;list.render();sync();});
    on(goBtn,'click',async()=>{
      const ok=state.filter(x=>!x.err);
      if(ok.length<2)return;
      try{
        setBusy(goBtn,true,'Merging…');prog.show();
        await loadLib('pdfLib');
        const out=await PDFLib.PDFDocument.create();
        let done=0;
        for(const it of ok){
          const src=await pdfDocFrom(it.bytes);
          const pages=await out.copyPages(src,src.getPageIndices());
          pages.forEach(p=>out.addPage(p));
          prog.set(++done,ok.length,it.file.name);
        }
        const bytes=await out.save();
        const blob=new Blob([bytes],{type:'application/pdf'});
        showResult(el,{
          title:'Merged',
          stats:out.getPageCount()+' pages · '+fmtBytes(blob.size),
          items:[{blob,name:'merged.pdf'}]
        });
      }catch(err){toast(err.message,true);}
      finally{setBusy(goBtn,false);prog.hide();sync();}
    });
    if(pre)addFiles(pre);
  }
};

/* ================= 2 · Split PDF ================= */
TOOLS['split-pdf']={
  name:'Split PDF',desc:'Pull out just the pages you need, or save every page separately.',match:isPdf,
  icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="8" height="16" rx="2"/><path d="M15 9h6m0 0-2-2m2 2-2 2M15 15h6m0 0-2-2m2 2-2 2"/></svg>',
  mount(root,pre){
    const el=toolShell(this,
      dzHtml('Choose a PDF','or drop it anywhere on this page')+
      '<div id="splitPanel" hidden>'+
        '<ul class="flist" style="margin-top:16px"></ul>'+
        '<div class="opts"><div class="opt"><label>What to do</label><div class="radio-row">'+
          '<label class="radio-pill"><input type="radio" name="splitMode" value="extract" checked>Extract pages</label>'+
          '<label class="radio-pill"><input type="radio" name="splitMode" value="all">Every page as its own PDF</label>'+
        '</div></div>'+
        '<div class="opt" id="rangeOpt"><label for="rangeIn">Pages (e.g. 1-3, 7)</label><input type="text" id="rangeIn" placeholder="1-3, 7" inputmode="numeric" style="min-width:180px"></div></div>'+
        '<div class="actions"><button class="btn btn-primary" id="splitGo">Split PDF</button></div>'+
      '</div>'+progHtml()+resultHtml());
    root.appendChild(el);
    let cur=null; // {file, bytes, pages}
    const panel=$('#splitPanel',el),prog=makeProg(el);
    async function setFile(fs){
      const f=fs[0];
      try{
        const bytes=await readBytes(f);
        const d=await pdfDocFrom(bytes);
        cur={file:f,bytes,pages:d.getPageCount()};
        $('.flist',el).innerHTML='<li><span class="fname">'+esc(f.name)+'</span><span class="badge">'+cur.pages+' pages</span><span class="fmeta">'+fmtBytes(f.size)+'</span></li>';
        panel.hidden=false;
        $('#rangeIn',el).placeholder='1-'+cur.pages;
        $('.result',el).classList.remove('show');
      }catch(err){toast(err.message,true);}
    }
    wireDz($('.dz',el),{accept:'.pdf,application/pdf',multiple:false,onFiles:setFile,match:isPdf,label:'a PDF file'});
    const rangeOpt=$('#rangeOpt',el);
    $$('input[name="splitMode"]',el).forEach(r=>on(r,'change',()=>{rangeOpt.style.display=r.value==='extract'&&r.checked?'':'none';}));
    on($('#splitGo',el),'click',async()=>{
      if(!cur)return toast('Choose a PDF first.',true);
      const mode=$('input[name="splitMode"]:checked',el).value;
      const goBtn=$('#splitGo',el);
      try{
        setBusy(goBtn,true,'Splitting…');
        await loadLib('pdfLib');
        const src=await pdfDocFrom(cur.bytes);
        const base=baseName(cur.file.name);
        if(mode==='extract'){
          const idx=parseRanges($('#rangeIn',el).value,cur.pages);
          const out=await PDFLib.PDFDocument.create();
          const pages=await out.copyPages(src,idx);
          pages.forEach(p=>out.addPage(p));
          const blob=new Blob([await out.save()],{type:'application/pdf'});
          showResult(el,{title:'Pages extracted',stats:idx.length+' of '+cur.pages+' pages · '+fmtBytes(blob.size),
            items:[{blob,name:base+'-pages.pdf'}]});
        }else{
          prog.show();
          const items=[];
          for(let i=0;i<cur.pages;i++){
            const out=await PDFLib.PDFDocument.create();
            const[p]=await out.copyPages(src,[i]);
            out.addPage(p);
            items.push({blob:new Blob([await out.save()],{type:'application/pdf'}),name:base+'-page-'+(i+1)+'.pdf'});
            prog.set(i+1,cur.pages);
          }
          items.zipName=base+'-pages';
          showResult(el,{title:'Split into '+cur.pages+' files',stats:'One PDF per page',items});
        }
      }catch(err){toast(err.message,true);}
      finally{setBusy(goBtn,false);prog.hide();}
    });
    if(pre)setFile(pre);
  }
};

/* ================= 3 · Compress PDF ================= */
TOOLS['compress-pdf']={
  name:'Compress PDF',desc:'Shrink a PDF so it fits email and upload limits.',match:isPdf,
  icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M12 7v3m0 0-2-2m2 2 2-2M12 17v-3m0 0-2 2m2-2 2 2"/></svg>',
  mount(root,pre){
    const el=toolShell(this,
      dzHtml('Choose a PDF','or drop it anywhere on this page')+
      '<div id="cpPanel" hidden><ul class="flist" style="margin-top:16px"></ul>'+
        '<div class="opts"><div class="opt"><label>Method</label><div class="radio-row">'+
          '<label class="radio-pill"><input type="radio" name="cpMode" value="balanced" checked>Balanced — keeps text</label>'+
          '<label class="radio-pill"><input type="radio" name="cpMode" value="strong">Strong — smallest file</label>'+
        '</div></div>'+
        '<div id="cpStrongOpts" style="display:none;gap:14px 22px" class="opts">'+
          optRange('cpQ','Image quality',40,90,5,70,'%')+
          '<div class="opt"><label for="cpScale">Detail</label><select id="cpScale"><option value="1.3">Standard — screen</option><option value="1.8">High — print</option></select></div>'+
        '</div>'+
        '<p class="note" id="cpHint">Balanced re-packs the file and keeps text selectable. Strong redraws each page as a compressed image — much smaller, but text can no longer be selected or searched.</p>'+
        '<div class="actions"><button class="btn btn-primary" id="cpGo">Compress PDF</button></div>'+
      '</div>'+progHtml()+resultHtml());
    root.appendChild(el);
    let cur=null;
    const prog=makeProg(el);
    wireRange(el,'cpQ',v=>v+'%');
    async function setFile(fs){
      const f=fs[0];
      try{
        const bytes=await readBytes(f);
        const d=await pdfDocFrom(bytes);
        cur={file:f,bytes,pages:d.getPageCount()};
        $('.flist',el).innerHTML='<li><span class="fname">'+esc(f.name)+'</span><span class="badge">'+cur.pages+' pages</span><span class="fmeta">'+fmtBytes(f.size)+'</span></li>';
        $('#cpPanel',el).hidden=false;
        $('.result',el).classList.remove('show');
        if(cur.pages>60)toast('Heads up: '+cur.pages+' pages — Strong mode may take a while on this device.');
      }catch(err){toast(err.message,true);}
    }
    wireDz($('.dz',el),{accept:'.pdf,application/pdf',multiple:false,onFiles:setFile,match:isPdf,label:'a PDF file'});
    $$('input[name="cpMode"]',el).forEach(r=>on(r,'change',()=>{
      $('#cpStrongOpts',el).style.display=$('input[name="cpMode"]:checked',el).value==='strong'?'flex':'none';
    }));
    on($('#cpGo',el),'click',async()=>{
      if(!cur)return toast('Choose a PDF first.',true);
      const goBtn=$('#cpGo',el);
      const mode=$('input[name="cpMode"]:checked',el).value;
      try{
        setBusy(goBtn,true,'Compressing…');
        let outBytes,note='';
        if(mode==='balanced'){
          const d=await pdfDocFrom(cur.bytes);
          outBytes=await d.save({useObjectStreams:true});
          note='Text and links preserved. For a much smaller file, try Strong mode.';
        }else{
          prog.show('Preparing…');
          await loadLib('pdfLib');
          const q=(+$('#cpQ',el).value)/100;
          const scale=+$('#cpScale',el).value;
          const out=await PDFLib.PDFDocument.create();
          await eachPdfPage(cur.bytes,{scale,prog,onPage:async(pg)=>{
            const blob=await canvasToBlob(pg.canvas,'image/jpeg',q);
            const img=await out.embedJpg(new Uint8Array(await blob.arrayBuffer()));
            const p=out.addPage([pg.ptW,pg.ptH]);
            p.drawImage(img,{x:0,y:0,width:pg.ptW,height:pg.ptH});
          }});
          outBytes=await out.save();
          note='Strong mode redraws pages as images — text is no longer selectable. Switch to Balanced if you need selectable text.';
        }
        const blob=new Blob([outBytes],{type:'application/pdf'});
        const before=cur.file.size,after=blob.size;
        const pct=Math.round(100*(before-after)/before);
        const delta=after<before
          ?'<span class="saving">−'+pct+'%</span>'
          :'<span class="growing">+'+Math.abs(pct)+'% (already efficient)</span>';
        showResult(el,{title:'Compressed',
          stats:fmtBytes(before)+' → '+fmtBytes(after)+' · '+delta,
          items:[{blob,name:baseName(cur.file.name)+'-compressed.pdf'}],note});
      }catch(err){toast(err.message,true);}
      finally{setBusy(goBtn,false);prog.hide();}
    });
    if(pre)setFile(pre);
  }
};

/* ================= 4 · PDF to JPG ================= */
TOOLS['pdf-to-jpg']={
  name:'PDF to JPG',desc:'Turn each page of a PDF into a high-quality image.',match:isPdf,
  icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="3" width="16" height="18" rx="2"/><circle cx="9.5" cy="9.5" r="1.6"/><path d="m4 17 4.5-4.5 3 3L15 12l5 5"/></svg>',
  mount(root,pre){
    const el=toolShell(this,
      dzHtml('Choose a PDF','or drop it anywhere on this page')+
      '<div id="pjPanel" hidden><ul class="flist" style="margin-top:16px"></ul>'+
        '<div class="opts">'+optRange('pjQ','JPG quality',60,95,5,85,'%')+
        '<div class="opt"><label for="pjScale">Detail</label><select id="pjScale"><option value="1.5">Good — screen</option><option value="2" selected>Sharp — print</option><option value="3">Maximum</option></select></div></div>'+
        '<div class="actions"><button class="btn btn-primary" id="pjGo">Convert to JPG</button></div>'+
        '<div class="thumbs" id="pjThumbs"></div>'+
      '</div>'+progHtml()+resultHtml());
    root.appendChild(el);
    let cur=null;const prog=makeProg(el);
    wireRange(el,'pjQ',v=>v+'%');
    async function setFile(fs){
      const f=fs[0];
      try{
        const bytes=await readBytes(f);
        const d=await pdfDocFrom(bytes);
        cur={file:f,bytes,pages:d.getPageCount()};
        $('.flist',el).innerHTML='<li><span class="fname">'+esc(f.name)+'</span><span class="badge">'+cur.pages+' pages</span><span class="fmeta">'+fmtBytes(f.size)+'</span></li>';
        $('#pjPanel',el).hidden=false;
        $('#pjThumbs',el).innerHTML='';
        $('.result',el).classList.remove('show');
      }catch(err){toast(err.message,true);}
    }
    wireDz($('.dz',el),{accept:'.pdf,application/pdf',multiple:false,onFiles:setFile,match:isPdf,label:'a PDF file'});
    on($('#pjGo',el),'click',async()=>{
      if(!cur)return toast('Choose a PDF first.',true);
      const goBtn=$('#pjGo',el);
      try{
        setBusy(goBtn,true,'Converting…');prog.show('Preparing…');
        const q=(+$('#pjQ',el).value)/100;
        const scale=+$('#pjScale',el).value;
        const base=baseName(cur.file.name);
        const items=[],thumbs=$('#pjThumbs',el);
        thumbs.innerHTML='';
        await eachPdfPage(cur.bytes,{scale,prog,onPage:async(pg)=>{
          const blob=await canvasToBlob(pg.canvas,'image/jpeg',q);
          items.push({blob,name:base+'-page-'+pg.index+'.jpg'});
          if(pg.index<=8){
            const t=document.createElement('canvas');
            const r=110/pg.canvas.height;
            t.width=Math.max(1,Math.round(pg.canvas.width*r));t.height=110;
            t.getContext('2d').drawImage(pg.canvas,0,0,t.width,t.height);
            const img=new Image();img.src=t.toDataURL('image/jpeg',.6);img.alt='Page '+pg.index;
            thumbs.appendChild(img);
          }
        }});
        items.zipName=base+'-pages';
        showResult(el,{title:items.length+' image'+(items.length>1?'s':'')+' ready',
          stats:'Quality '+Math.round(q*100)+'% · total '+fmtBytes(items.reduce((s,i)=>s+i.blob.size,0)),items});
      }catch(err){toast(err.message,true);}
      finally{setBusy(goBtn,false);prog.hide();}
    });
    if(pre)setFile(pre);
  }
};

/* ================= 5 · Images to PDF ================= */
TOOLS['jpg-to-pdf']={
  name:'Images to PDF',desc:'Pack photos and scans into one tidy PDF document.',match:isImg,
  icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="11" height="11" rx="2"/><circle cx="6.8" cy="6.8" r="1.2"/><path d="m3 11.5 3-3 3 3"/><rect x="13" y="13" width="8" height="8" rx="1.5"/></svg>',
  mount(root,pre){
    const el=toolShell(this,
      dzHtml('Choose images','JPG, PNG or WebP — drop them anywhere on this page')+
      '<ul class="flist"></ul>'+
      '<div class="opts"><div class="opt"><label>Page size</label><div class="radio-row">'+
        '<label class="radio-pill"><input type="radio" name="ipSize" value="fit" checked>Match image</label>'+
        '<label class="radio-pill"><input type="radio" name="ipSize" value="a4p">A4 portrait</label>'+
        '<label class="radio-pill"><input type="radio" name="ipSize" value="a4l">A4 landscape</label>'+
      '</div></div>'+
      '<div class="opt"><label>&nbsp;</label><label class="check"><input type="checkbox" id="ipMargin">Add a small margin</label></div></div>'+
      '<div class="actions"><button class="btn btn-primary" id="ipGo" disabled>Make PDF</button></div>'+
      progHtml()+resultHtml());
    root.appendChild(el);
    const state=[],prog=makeProg(el);
    const goBtn=$('#ipGo',el);
    const list=makeSortableList($('.flist',el),state,{onChange:sync});
    function sync(){goBtn.disabled=!state.length;goBtn.textContent=state.length?'Make PDF from '+state.length+' image'+(state.length>1?'s':''):'Make PDF';}
    function addFiles(fs){fs.forEach(f=>state.push({file:f}));list.render();sync();}
    wireDz($('.dz',el),{accept:'image/png,image/jpeg,image/webp',multiple:true,onFiles:addFiles,match:isImg,label:'JPG, PNG or WebP images'});
    on(goBtn,'click',async()=>{
      if(!state.length)return;
      try{
        setBusy(goBtn,true,'Building…');prog.show();
        await loadLib('pdfLib');
        const out=await PDFLib.PDFDocument.create();
        const A4=[595.28,841.89];
        const mode=$('input[name="ipSize"]:checked',el).value;
        const margin=$('#ipMargin',el).checked?28:0;
        let i=0;
        for(const it of state){
          const f=it.file;
          let bytes,img;
          if(/webp/i.test(f.type)||/\.webp$/i.test(f.name)){
            const bmp=await loadImageEl(f);
            const c=document.createElement('canvas');c.width=bmp.naturalWidth;c.height=bmp.naturalHeight;
            c.getContext('2d').drawImage(bmp,0,0);
            bytes=new Uint8Array(await(await canvasToBlob(c,'image/png')).arrayBuffer());
            img=await out.embedPng(bytes);
          }else if(/png/i.test(f.type)||/\.png$/i.test(f.name)){
            img=await out.embedPng(await readBytes(f));
          }else{
            img=await out.embedJpg(await readBytes(f));
          }
          let pw,ph;
          if(mode==='fit'){pw=img.width+2*margin;ph=img.height+2*margin;}
          else{const a=mode==='a4p'?A4:[A4[1],A4[0]];pw=a[0];ph=a[1];}
          const page=out.addPage([pw,ph]);
          const availW=pw-2*margin,availH=ph-2*margin;
          const s=Math.min(availW/img.width,availH/img.height,mode==='fit'?1:Infinity);
          const w=img.width*s,ht=img.height*s;
          page.drawImage(img,{x:(pw-w)/2,y:(ph-ht)/2,width:w,height:ht});
          prog.set(++i,state.length,f.name);
        }
        const blob=new Blob([await out.save()],{type:'application/pdf'});
        const name=state.length===1?baseName(state[0].file.name)+'.pdf':'images.pdf';
        showResult(el,{title:'PDF ready',stats:state.length+' page'+(state.length>1?'s':'')+' · '+fmtBytes(blob.size),items:[{blob,name}]});
      }catch(err){toast(err.message,true);}
      finally{setBusy(goBtn,false);prog.hide();}
    });
    if(pre)addFiles(pre);
  }
};
function loadImageEl(file){
  return new Promise((res,rej)=>{
    const url=URL.createObjectURL(file);
    const img=new Image();
    img.onload=()=>{res(img);setTimeout(()=>URL.revokeObjectURL(url),2000);};
    img.onerror=()=>{URL.revokeObjectURL(url);rej(new Error('Could not read '+file.name+'. The image may be damaged.'));};
    img.src=url;
  });
}

/* ================= 6 · Compress image ================= */
const WEBP_OK=document.createElement('canvas').toDataURL('image/webp').indexOf('data:image/webp')===0;
async function drawToCanvas(file,{w,h,bg}){
  const img=await loadImageEl(file);
  const cw=w||img.naturalWidth,ch=h||img.naturalHeight;
  const c=document.createElement('canvas');c.width=cw;c.height=ch;
  const ctx=c.getContext('2d');
  if(bg){ctx.fillStyle=bg;ctx.fillRect(0,0,cw,ch);}
  ctx.imageSmoothingQuality='high';
  ctx.drawImage(img,0,0,cw,ch);
  return c;
}
TOOLS['compress-image']={
  name:'Compress image',desc:'Cut file size hard while keeping your photos sharp.',match:isImg,
  icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 12h4M9.4 10.4 11 12l-1.6 1.6M17 12h-4M14.6 10.4 13 12l1.6 1.6"/></svg>',
  mount(root,pre){
    const el=toolShell(this,
      dzHtml('Choose images','JPG, PNG or WebP — several at once is fine')+
      '<ul class="flist"></ul>'+
      '<div class="opts">'+optRange('ciQ','Quality',30,95,5,75,'%')+
      '<div class="opt"><label for="ciFmt">Save as</label><select id="ciFmt">'+
        '<option value="image/jpeg">JPG — smallest for photos</option>'+
        (WEBP_OK?'<option value="image/webp">WebP — modern, small</option>':'')+
        '<option value="keep">Keep original format</option></select></div>'+
      '<div class="opt"><label for="ciMaxW">Max width (px, optional)</label><input type="number" id="ciMaxW" min="16" step="1" placeholder="e.g. 1920" style="width:150px"></div></div>'+
      '<p class="note">JPG and WebP output also strips hidden metadata (EXIF: location, camera, date) — a small privacy win. PNG stays lossless, so use “Max width” or switch format to shrink it.</p>'+
      '<div class="actions"><button class="btn btn-primary" id="ciGo" disabled>Compress</button></div>'+
      progHtml()+resultHtml());
    root.appendChild(el);
    const state=[],prog=makeProg(el),goBtn=$('#ciGo',el);
    wireRange(el,'ciQ',v=>v+'%');
    const list=makeSortableList($('.flist',el),state,{onChange:sync});
    function sync(){goBtn.disabled=!state.length;goBtn.textContent=state.length?'Compress '+state.length+' image'+(state.length>1?'s':''):'Compress';}
    function addFiles(fs){fs.forEach(f=>state.push({file:f}));list.render();sync();}
    wireDz($('.dz',el),{accept:'image/png,image/jpeg,image/webp',multiple:true,onFiles:addFiles,match:isImg,label:'JPG, PNG or WebP images'});
    on(goBtn,'click',async()=>{
      if(!state.length)return;
      try{
        setBusy(goBtn,true,'Compressing…');prog.show();
        const q=(+$('#ciQ',el).value)/100;
        const fmtSel=$('#ciFmt',el).value;
        const maxW=parseInt($('#ciMaxW',el).value,10)||null;
        const items=[];let before=0,after=0,i=0;
        for(const it of state){
          const f=it.file;
          const img=await loadImageEl(f);
          let w=img.naturalWidth,h=img.naturalHeight;
          if(maxW&&w>maxW){h=Math.round(h*maxW/w);w=maxW;}
          const orig=/png/i.test(f.type)?'image/png':(/webp/i.test(f.type)?'image/webp':'image/jpeg');
          const type=fmtSel==='keep'?orig:fmtSel;
          const bg=type==='image/jpeg'?'#ffffff':null;
          const c=document.createElement('canvas');c.width=w;c.height=h;
          const ctx=c.getContext('2d');
          if(bg){ctx.fillStyle=bg;ctx.fillRect(0,0,w,h);}
          ctx.imageSmoothingQuality='high';ctx.drawImage(img,0,0,w,h);
          const blob=await canvasToBlob(c,type,type==='image/png'?undefined:q);
          c.width=0;c.height=0;
          const ext=type==='image/png'?'png':(type==='image/webp'?'webp':'jpg');
          items.push({blob,name:baseName(f.name)+'-compressed.'+ext,orig:f.size});
          before+=f.size;after+=blob.size;
          prog.set(++i,state.length,f.name);
        }
        items.zipName='compressed-images';
        const pct=Math.round(100*(before-after)/before);
        showResult(el,{title:'Compressed',
          stats:fmtBytes(before)+' → '+fmtBytes(after)+' · '+(after<before?'<span class="saving">−'+pct+'%</span>':'<span class="growing">no smaller — try JPG or a max width</span>'),
          items});
      }catch(err){toast(err.message,true);}
      finally{setBusy(goBtn,false);prog.hide();}
    });
    if(pre)addFiles(pre);
  }
};

/* ================= 7 · Resize image ================= */
TOOLS['resize-image']={
  name:'Resize image',desc:'Scale pictures to exact pixels or a percentage.',match:isImg,
  icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="7" width="10" height="10" rx="1.5"/><path d="M3 3h4M3 3v4m0-4 4 4M21 21h-4m4 0v-4m0 4-4-4"/></svg>',
  mount(root,pre){
    const el=toolShell(this,
      dzHtml('Choose images','JPG, PNG or WebP — several at once is fine')+
      '<ul class="flist"></ul>'+
      '<div class="opts"><div class="opt"><label>Resize by</label><div class="radio-row">'+
        '<label class="radio-pill"><input type="radio" name="rzMode" value="px" checked>Pixels</label>'+
        '<label class="radio-pill"><input type="radio" name="rzMode" value="pct">Percent</label></div></div>'+
      '<div class="opt" id="rzWOpt"><label for="rzW">Width (px)</label><input type="number" id="rzW" min="1" placeholder="e.g. 1200" style="width:130px"></div>'+
      '<div class="opt" id="rzHOpt"><label for="rzH">Height (px)</label><input type="number" id="rzH" min="1" placeholder="auto" style="width:130px"></div>'+
      '<div class="opt" id="rzPOpt" style="display:none"><label for="rzP">Scale (%)</label><input type="number" id="rzP" min="1" max="500" value="50" style="width:110px"></div>'+
      '<div class="opt" id="rzKOpt"><label>&nbsp;</label><label class="check"><input type="checkbox" id="rzKeep" checked>Keep proportions</label></div></div>'+
      '<div class="actions"><button class="btn btn-primary" id="rzGo" disabled>Resize</button></div>'+
      progHtml()+resultHtml());
    root.appendChild(el);
    const state=[],prog=makeProg(el),goBtn=$('#rzGo',el);
    const list=makeSortableList($('.flist',el),state,{onChange:sync});
    function sync(){goBtn.disabled=!state.length;goBtn.textContent=state.length?'Resize '+state.length+' image'+(state.length>1?'s':''):'Resize';}
    function addFiles(fs){fs.forEach(f=>state.push({file:f}));list.render();sync();}
    wireDz($('.dz',el),{accept:'image/png,image/jpeg,image/webp',multiple:true,onFiles:addFiles,match:isImg,label:'JPG, PNG or WebP images'});
    $$('input[name="rzMode"]',el).forEach(r=>on(r,'change',()=>{
      const px=$('input[name="rzMode"]:checked',el).value==='px';
      $('#rzWOpt',el).style.display=px?'':'none';
      $('#rzHOpt',el).style.display=px?'':'none';
      $('#rzKOpt',el).style.display=px?'':'none';
      $('#rzPOpt',el).style.display=px?'none':'';
    }));
    on(goBtn,'click',async()=>{
      if(!state.length)return;
      const px=$('input[name="rzMode"]:checked',el).value==='px';
      const W=parseInt($('#rzW',el).value,10)||null;
      const H=parseInt($('#rzH',el).value,10)||null;
      const P=(parseFloat($('#rzP',el).value)||0)/100;
      const keep=$('#rzKeep',el).checked;
      if(px&&!W&&!H)return toast('Enter a width or a height.',true);
      if(!px&&(!P||P<=0))return toast('Enter a percentage above 0.',true);
      try{
        setBusy(goBtn,true,'Resizing…');prog.show();
        const items=[];let i=0;
        for(const it of state){
          const f=it.file;
          const img=await loadImageEl(f);
          let w=img.naturalWidth,h=img.naturalHeight;
          if(!px){w=Math.max(1,Math.round(w*P));h=Math.max(1,Math.round(h*P));}
          else if(W&&H){
            if(keep){const s=Math.min(W/w,H/h);w=Math.max(1,Math.round(w*s));h=Math.max(1,Math.round(h*s));}
            else{w=W;h=H;}
          }
          else if(W){h=Math.max(1,Math.round(h*W/img.naturalWidth));w=W;}
          else{w=Math.max(1,Math.round(w*H/img.naturalHeight));h=H;}
          const orig=/png/i.test(f.type)?'image/png':(/webp/i.test(f.type)&&WEBP_OK?'image/webp':'image/jpeg');
          const bg=orig==='image/jpeg'?'#ffffff':null;
          const c=document.createElement('canvas');c.width=w;c.height=h;
          const ctx=c.getContext('2d');
          if(bg){ctx.fillStyle=bg;ctx.fillRect(0,0,w,h);}
          ctx.imageSmoothingQuality='high';ctx.drawImage(img,0,0,w,h);
          const blob=await canvasToBlob(c,orig,orig==='image/png'?undefined:.92);
          c.width=0;c.height=0;
          const ext=orig==='image/png'?'png':(orig==='image/webp'?'webp':'jpg');
          items.push({blob,name:baseName(f.name)+'-'+w+'x'+h+'.'+ext});
          prog.set(++i,state.length,f.name);
        }
        items.zipName='resized-images';
        showResult(el,{title:'Resized',stats:items.length+' image'+(items.length>1?'s':'')+' · total '+fmtBytes(items.reduce((s,x)=>s+x.blob.size,0)),items});
      }catch(err){toast(err.message,true);}
      finally{setBusy(goBtn,false);prog.hide();}
    });
    if(pre)addFiles(pre);
  }
};

/* ================= 8 · Convert image ================= */
TOOLS['convert-image']={
  name:'Convert image',desc:'Switch between JPG, PNG and WebP in one click.',match:isImg,
  icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 8A9 9 0 0 0 5 6.5L3.5 8M3.5 16a9 9 0 0 0 15.5 1.5l1.5-1.5"/><path d="M3.5 3.5V8H8M20.5 20.5V16H16"/></svg>',
  mount(root,pre){
    const el=toolShell(this,
      dzHtml('Choose images','JPG, PNG or WebP — several at once is fine')+
      '<ul class="flist"></ul>'+
      '<div class="opts"><div class="opt"><label for="cvFmt">Convert to</label><select id="cvFmt">'+
        '<option value="image/jpeg">JPG</option><option value="image/png">PNG</option>'+
        (WEBP_OK?'<option value="image/webp">WebP</option>':'')+'</select></div>'+
      optRange('cvQ','Quality',30,95,5,85,'%')+'</div>'+
      (WEBP_OK?'':'<p class="note warn">Your browser can\u2019t save WebP, so that option is hidden. JPG and PNG work everywhere.</p>')+
      '<p class="note">Converting to JPG places transparent areas on a white background. Quality applies to JPG and WebP; PNG is always lossless.</p>'+
      '<div class="actions"><button class="btn btn-primary" id="cvGo" disabled>Convert</button></div>'+
      progHtml()+resultHtml());
    root.appendChild(el);
    const state=[],prog=makeProg(el),goBtn=$('#cvGo',el);
    wireRange(el,'cvQ',v=>v+'%');
    const list=makeSortableList($('.flist',el),state,{onChange:sync});
    function sync(){goBtn.disabled=!state.length;goBtn.textContent=state.length?'Convert '+state.length+' image'+(state.length>1?'s':''):'Convert';}
    function addFiles(fs){fs.forEach(f=>state.push({file:f}));list.render();sync();}
    wireDz($('.dz',el),{accept:'image/png,image/jpeg,image/webp',multiple:true,onFiles:addFiles,match:isImg,label:'JPG, PNG or WebP images'});
    on(goBtn,'click',async()=>{
      if(!state.length)return;
      try{
        setBusy(goBtn,true,'Converting…');prog.show();
        const type=$('#cvFmt',el).value;
        const q=(+$('#cvQ',el).value)/100;
        const bg=type==='image/jpeg'?'#ffffff':null;
        const ext=type==='image/png'?'png':(type==='image/webp'?'webp':'jpg');
        const items=[];let i=0;
        for(const it of state){
          const c=await drawToCanvas(it.file,{bg});
          const blob=await canvasToBlob(c,type,type==='image/png'?undefined:q);
          c.width=0;c.height=0;
          items.push({blob,name:baseName(it.file.name)+'.'+ext});
          prog.set(++i,state.length,it.file.name);
        }
        items.zipName='converted-images';
        showResult(el,{title:'Converted to '+ext.toUpperCase(),stats:items.length+' file'+(items.length>1?'s':'')+' · total '+fmtBytes(items.reduce((s,x)=>s+x.blob.size,0)),items});
      }catch(err){toast(err.message,true);}
      finally{setBusy(goBtn,false);prog.hide();}
    });
    if(pre)addFiles(pre);
  }
};

/* ================= 9 · QR code ================= */
TOOLS['qr-code']={
  name:'QR code maker',desc:'Turn any link or text into a scannable code.',match:()=>false,
  icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 14h3v3h-3zM21 14v.01M14 21v.01M18 18h3v3h-3z"/></svg>',
  mount(root){
    const el=toolShell(this,
      '<div class="field"><label for="qrText" style="font-size:.78rem;font-weight:700;letter-spacing:.02em;color:var(--muted);text-transform:uppercase">Link or text</label>'+
      '<input type="text" id="qrText" placeholder="https://example.com or any text"></div>'+
      '<div class="opts"><div class="opt"><label for="qrSize">Size</label><select id="qrSize"><option value="256">256 px — screens</option><option value="512" selected>512 px — print</option><option value="1024">1024 px — posters</option></select></div></div>'+
      '<div class="actions"><button class="btn btn-primary" id="qrGo">Make QR code</button></div>'+
      '<div class="qr-out"><div class="qr-frame"><img id="qrImg" alt="Generated QR code" width="220" height="220"></div>'+
      '<div class="actions" style="justify-content:center"><button class="btn btn-ghost" id="qrDl">'+I.dl+'Download PNG</button></div></div>');
    root.appendChild(el);
    let dataUrl=null;
    on($('#qrGo',el),'click',async()=>{
      const text=$('#qrText',el).value.trim();
      if(!text)return toast('Type a link or some text first.',true);
      const goBtn=$('#qrGo',el);
      try{
        setBusy(goBtn,true,'Drawing…');
        await loadLib('qrcode');
        const size=+$('#qrSize',el).value;
        const holder=document.createElement('div');
        holder.style.cssText='position:absolute;left:-9999px;top:0';
        document.body.appendChild(holder);
        new QRCode(holder,{text,width:size,height:size,colorDark:'#12151A',colorLight:'#ffffff',correctLevel:QRCode.CorrectLevel.M});
        await new Promise(r=>setTimeout(r,60));
        const canvas=holder.querySelector('canvas');
        if(!canvas)throw new Error('Could not draw this code.');
        dataUrl=canvas.toDataURL('image/png');
        holder.remove();
        $('#qrImg',el).src=dataUrl;
        $('.qr-out',el).classList.add('show');
      }catch(err){
        toast(/overflow/i.test(String(err))?'That text is too long for one QR code — trim it a little.':(err.message||'Could not draw this code.'),true);
      }finally{setBusy(goBtn,false);}
    });
    on($('#qrDl',el),'click',()=>{
      if(!dataUrl)return;
      const b=atob(dataUrl.split(',')[1]);
      const arr=new Uint8Array(b.length);
      for(let i=0;i<b.length;i++)arr[i]=b.charCodeAt(i);
      downloadBlob(new Blob([arr],{type:'image/png'}),'qr-code.png');
    });
    on($('#qrText',el),'keydown',e=>{if(e.key==='Enter')$('#qrGo',el).click();});
  }
};

/* ================= 10 · Password generator ================= */
TOOLS['password-generator']={
  name:'Password generator',desc:'Strong random passwords, made on your device.',match:()=>false,
  icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="7.5" cy="15.5" r="3.5"/><path d="M10.2 12.8 21 2M15 8l3.2 3.2M12 11l2 2"/></svg>',
  mount(root){
    const el=toolShell(this,
      '<div class="pw-out"><output id="pwOut" aria-live="polite"></output>'+
      '<button class="mini-btn" id="pwNew" aria-label="New password" style="width:46px;height:auto">'+I.refresh+'</button>'+
      '<button class="mini-btn" id="pwCopy" aria-label="Copy password" style="width:46px;height:auto">'+I.copy+'</button></div>'+
      '<div class="meter"><i id="pwBar"></i></div><p class="meter-label" id="pwLabel"></p>'+
      '<div class="opts">'+optRange('pwLen','Length',8,64,1,16,'')+
      '<div class="opt"><label>Include</label><div class="checks">'+
        '<label class="check"><input type="checkbox" id="pwU" checked>Uppercase (A–Z)</label>'+
        '<label class="check"><input type="checkbox" id="pwL" checked>Lowercase (a–z)</label>'+
        '<label class="check"><input type="checkbox" id="pwD" checked>Digits (0–9)</label>'+
        '<label class="check"><input type="checkbox" id="pwS" checked>Symbols (!@#$…)</label>'+
        '<label class="check"><input type="checkbox" id="pwA" checked>Avoid look-alikes (l, 1, O, 0)</label>'+
      '</div></div></div>'+
      '<p class="note">Generated with your browser\u2019s cryptographic random source. Nothing is stored or sent anywhere.</p>');
    root.appendChild(el);
    const SETS={
      U:{full:'ABCDEFGHIJKLMNOPQRSTUVWXYZ',safe:'ABCDEFGHJKLMNPQRSTUVWXYZ'},
      L:{full:'abcdefghijklmnopqrstuvwxyz',safe:'abcdefghijkmnopqrstuvwxyz'},
      D:{full:'0123456789',safe:'23456789'},
      S:{full:'!@#$%^&*()-_=+[]{};:,.?',safe:'!@#$%^&*()-_=+[]{};:,.?'}
    };
    function randInt(max){ // unbiased
      const lim=Math.floor(4294967296/max)*max;
      const buf=new Uint32Array(1);
      let x;do{crypto.getRandomValues(buf);x=buf[0];}while(x>=lim);
      return x%max;
    }
    function generate(){
      const len=+$('#pwLen',el).value;
      const avoid=$('#pwA',el).checked;
      const pools=[];
      ['U','L','D','S'].forEach(k=>{if($('#pw'+k,el).checked)pools.push(avoid?SETS[k].safe:SETS[k].full);});
      if(!pools.length){$('#pwL',el).checked=true;pools.push(avoid?SETS.L.safe:SETS.L.full);}
      const all=pools.join('');
      const chars=[];
      pools.forEach(p=>chars.push(p[randInt(p.length)]));      // guarantee each set
      while(chars.length<len)chars.push(all[randInt(all.length)]);
      for(let i=chars.length-1;i>0;i--){const j=randInt(i+1);const t=chars[i];chars[i]=chars[j];chars[j]=t;}
      const pw=chars.slice(0,len).join('');
      $('#pwOut',el).textContent=pw;
      const bits=Math.round(len*Math.log2(all.length));
      const tier=bits<45?['Weak','var(--danger)',25]:bits<70?['Fair','var(--warn)',50]:bits<100?['Strong','var(--ok)',78]:['Excellent','var(--ok)',100];
      $('#pwBar',el).style.width=tier[2]+'%';
      $('#pwBar',el).style.background=tier[1];
      $('#pwLabel',el).textContent='Entropy \u2248 '+bits+' bits \u2014 '+tier[0];
    }
    wireRange(el,'pwLen');
    on($('#pwLen',el),'input',generate);
    ['U','L','D','S','A'].forEach(k=>on($('#pw'+k,el),'change',generate));
    on($('#pwNew',el),'click',generate);
    on($('#pwCopy',el),'click',async()=>{
      const pw=$('#pwOut',el).textContent;
      try{await navigator.clipboard.writeText(pw);toast('Copied to clipboard');}
      catch(e){toast('Copy blocked by browser — select the password and copy manually.',true);}
    });
    generate();
  }
};

/* ================= 11 · Word counter ================= */
TOOLS['word-counter']={
  name:'Word counter',desc:'Words, characters and reading time as you type.',match:()=>false,
  icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h16M4 11h16M4 16h8"/><path d="m15.5 17.5 2 2L21 16"/></svg>',
  mount(root){
    const el=toolShell(this,
      '<div class="field"><textarea id="wcText" placeholder="Paste or type your text here…" aria-label="Text to analyze"></textarea></div>'+
      '<div class="stats">'+
        '<div class="stat"><b id="stWords">0</b><span>Words</span></div>'+
        '<div class="stat"><b id="stChars">0</b><span>Characters</span></div>'+
        '<div class="stat"><b id="stNoSp">0</b><span>No spaces</span></div>'+
        '<div class="stat"><b id="stSent">0</b><span>Sentences</span></div>'+
        '<div class="stat"><b id="stPara">0</b><span>Paragraphs</span></div>'+
        '<div class="stat"><b id="stUniq">0</b><span>Unique words</span></div>'+
        '<div class="stat"><b id="stRead">0 s</b><span>Reading time</span></div>'+
        '<div class="stat"><b id="stSpeak">0 s</b><span>Speaking time</span></div>'+
      '</div>');
    root.appendChild(el);
    function timeFmt(words,wpm){
      if(!words)return '0 s';
      const s=Math.max(1,Math.round(words/wpm*60));
      return s<60?s+' s':Math.round(s/60)+' min';
    }
    function update(){
      const t=$('#wcText',el).value;
      const words=t.match(/\S+/g)||[];
      $('#stWords',el).textContent=words.length;
      $('#stChars',el).textContent=t.length;
      $('#stNoSp',el).textContent=t.replace(/\s/g,'').length;
      const sent=(t.match(/[^.!?\u2026]+[.!?\u2026]+/g)||[]).length;
      $('#stSent',el).textContent=sent||(words.length?1:0);
      $('#stPara',el).textContent=t.split(/\n\s*\n/).filter(s=>s.trim()).length;
      $('#stUniq',el).textContent=new Set(words.map(w=>w.toLowerCase().replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu,'')).filter(Boolean)).size;
      $('#stRead',el).textContent=timeFmt(words.length,220);
      $('#stSpeak',el).textContent=timeFmt(words.length,130);
    }
    on($('#wcText',el),'input',update);
    update();
  }
};

/* ================= 12 · Signature maker ================= */
TOOLS['signature']={
  name:'Signature maker',desc:'Draw a signature and save it as a transparent PNG.',match:()=>false,
  icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m14.5 4.5 5 5L8 21H3v-5z"/><path d="m12.5 6.5 5 5"/></svg>',
  mount(root){
    const el=toolShell(this,
      '<div class="sig-wrap"><canvas id="sigCanvas"></canvas><div class="sig-hint" id="sigHint">Sign here — mouse, finger or stylus</div></div>'+
      '<div class="opts"><div class="opt"><label>Pen</label><div class="radio-row">'+
        '<label class="radio-pill"><input type="radio" name="sigColor" value="#12151A" checked>Black ink</label>'+
        '<label class="radio-pill"><input type="radio" name="sigColor" value="#1B3FBF">Blue ink</label></div></div>'+
      optRange('sigSize','Thickness',1,7,0.5,2.5,'')+
      '<div class="opt"><label>&nbsp;</label><label class="check"><input type="checkbox" id="sigBg">White background</label></div></div>'+
      '<div class="actions"><button class="btn btn-primary" id="sigDl">'+I.dl+'Download PNG</button>'+
      '<button class="btn btn-ghost btn-sm" id="sigUndo">Undo</button>'+
      '<button class="btn btn-ghost btn-sm" id="sigClear">Clear</button></div>');
    root.appendChild(el);
    const wrap=$('.sig-wrap',el),cv=$('#sigCanvas',el),ctx=cv.getContext('2d');
    const strokes=[];let cur=null,cssW=0,cssH=0;
    function sizeCanvas(){
      const w=wrap.clientWidth||600;
      const hgt=Math.max(170,Math.round(w/2.7));
      const ratio=cssW?w/cssW:1;
      if(ratio!==1&&cssW)strokes.forEach(s=>s.pts.forEach(p=>{p.x*=ratio;p.y*=ratio;}));
      cssW=w;cssH=hgt;
      const dpr=Math.min(window.devicePixelRatio||1,2);
      cv.width=Math.round(w*dpr);cv.height=Math.round(hgt*dpr);
      cv.style.height=hgt+'px';
      ctx.setTransform(dpr,0,0,dpr,0,0);
      redraw();
    }
    function drawStroke(c,s){
      c.strokeStyle=s.color;c.lineWidth=s.size;c.lineCap='round';c.lineJoin='round';
      const p=s.pts;
      if(p.length===1){c.beginPath();c.arc(p[0].x,p[0].y,s.size/2,0,7);c.fillStyle=s.color;c.fill();return;}
      c.beginPath();c.moveTo(p[0].x,p[0].y);
      for(let i=1;i<p.length-1;i++){
        const mx=(p[i].x+p[i+1].x)/2,my=(p[i].y+p[i+1].y)/2;
        c.quadraticCurveTo(p[i].x,p[i].y,mx,my);
      }
      c.lineTo(p[p.length-1].x,p[p.length-1].y);
      c.stroke();
    }
    function redraw(){
      ctx.clearRect(0,0,cssW,cssH);
      strokes.forEach(s=>drawStroke(ctx,s));
      $('#sigHint',el).style.display=strokes.length?'none':'flex';
    }
    function pos(e){const r=cv.getBoundingClientRect();return{x:e.clientX-r.left,y:e.clientY-r.top};}
    on(cv,'pointerdown',e=>{
      e.preventDefault();cv.setPointerCapture(e.pointerId);
      cur={color:$('input[name="sigColor"]:checked',el).value,size:+$('#sigSize',el).value,pts:[pos(e)]};
      strokes.push(cur);redraw();
    });
    on(cv,'pointermove',e=>{if(!cur)return;cur.pts.push(pos(e));redraw();});
    ['pointerup','pointercancel','pointerleave'].forEach(ev=>on(cv,ev,()=>{cur=null;}));
    wireRange(el,'sigSize');
    on($('#sigUndo',el),'click',()=>{strokes.pop();redraw();});
    on($('#sigClear',el),'click',()=>{strokes.length=0;redraw();});
    on($('#sigDl',el),'click',async()=>{
      if(!strokes.length)return toast('Draw your signature first.',true);
      const ex=document.createElement('canvas');
      ex.width=cssW*2;ex.height=cssH*2;
      const c=ex.getContext('2d');c.scale(2,2);
      if($('#sigBg',el).checked){c.fillStyle='#ffffff';c.fillRect(0,0,cssW,cssH);}
      strokes.forEach(s=>drawStroke(c,s));
      try{downloadBlob(await canvasToBlob(ex,'image/png'),'signature.png');}
      catch(err){toast(err.message,true);}
    });
    const ro=new ResizeObserver(()=>sizeCanvas());
    ro.observe(wrap);
    sizeCanvas();
  }
};

/* ================= boot ================= */
applyTheme();
filterCards();
route();
})();
