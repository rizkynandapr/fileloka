/* Fileloka core-logic test suite.
 * Mirrors the exact functions shipped in index.html, using the same
 * pdf-lib@1.17.1 / jszip@3.10.1 versions loaded from cdnjs in production. */
const { PDFDocument, StandardFonts, rgb } = require('pdf-lib');
const JSZip = require('jszip');
const crypto = require('crypto');

let pass = 0, fail = 0;
function ok(cond, name){ if(cond){pass++;console.log('  PASS  '+name);} else {fail++;console.log('  FAIL  '+name);} }
async function throws(fn, name){ try{ await fn(); fail++; console.log('  FAIL  '+name+' (no error thrown)'); } catch(e){ pass++; console.log('  PASS  '+name+' → "'+e.message+'"'); } }

/* ---- functions copied VERBATIM from index.html ---- */
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
function fmtBytes(n){
  if(!isFinite(n))return '—';
  const u=['B','KB','MB','GB'];let i=0;
  while(n>=1024&&i<u.length-1){n/=1024;i++;}
  return (n<10&&i>0?n.toFixed(1):Math.round(n))+' '+u[i];
}
function randInt(max){ // node polyfill of the browser version (crypto.getRandomValues)
  const lim=Math.floor(4294967296/max)*max;
  let x;do{x=crypto.randomBytes(4).readUInt32LE(0);}while(x>=lim);
  return x%max;
}
const SETS={
  U:{full:'ABCDEFGHIJKLMNOPQRSTUVWXYZ',safe:'ABCDEFGHJKLMNPQRSTUVWXYZ'},
  L:{full:'abcdefghijklmnopqrstuvwxyz',safe:'abcdefghijkmnopqrstuvwxyz'},
  D:{full:'0123456789',safe:'23456789'},
  S:{full:'!@#$%^&*()-_=+[]{};:,.?',safe:'!@#$%^&*()-_=+[]{};:,.?'}
};
function generatePassword(len, keys, avoid){
  const pools=keys.map(k=>avoid?SETS[k].safe:SETS[k].full);
  const all=pools.join('');
  const chars=[];
  pools.forEach(p=>chars.push(p[randInt(p.length)]));
  while(chars.length<len)chars.push(all[randInt(all.length)]);
  for(let i=chars.length-1;i>0;i--){const j=randInt(i+1);const t=chars[i];chars[i]=chars[j];chars[j]=t;}
  return chars.slice(0,len).join('');
}
function wordStats(t){
  const words=t.match(/\S+/g)||[];
  const sent=(t.match(/[^.!?\u2026]+[.!?\u2026]+/g)||[]).length;
  return {
    words: words.length,
    chars: t.length,
    noSp: t.replace(/\s/g,'').length,
    sent: sent||(words.length?1:0),
    para: t.split(/\n\s*\n/).filter(s=>s.trim()).length,
    uniq: new Set(words.map(w=>w.toLowerCase().replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu,'')).filter(Boolean)).size
  };
}
/* ---- helpers ---- */
async function makePdf(nPages, label){
  const doc = await PDFDocument.create();
  const font = await doc.embedFont(StandardFonts.Helvetica);
  for(let i=1;i<=nPages;i++){
    const p = doc.addPage([595.28, 841.89]);
    p.drawText(label+' page '+i, {x:60,y:760,size:24,font,color:rgb(0.1,0.1,0.2)});
  }
  return doc.save();
}
const PNG_1x1 = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==','base64');

(async()=>{
  console.log('\n== 1. Merge PDF ==');
  const a = await makePdf(2,'A'), b = await makePdf(3,'B');
  const out = await PDFDocument.create();
  for(const src of [a,b]){
    const s = await PDFDocument.load(src);
    (await out.copyPages(s, s.getPageIndices())).forEach(p=>out.addPage(p));
  }
  const merged = await out.save();
  const check = await PDFDocument.load(merged);
  ok(check.getPageCount()===5, 'merge 2pg + 3pg → 5 pages');
  ok(Buffer.from(merged.slice(0,5)).toString()==='%PDF-', 'merged output starts with %PDF- header');

  console.log('\n== 2. Split PDF (extract ranges) ==');
  const src5 = await PDFDocument.load(await makePdf(5,'S'));
  const idx = parseRanges('1-2, 5', 5);
  ok(JSON.stringify(idx)==='[0,1,4]', 'parseRanges("1-2, 5") → [0,1,4]');
  const ex = await PDFDocument.create();
  (await ex.copyPages(src5, idx)).forEach(p=>ex.addPage(p));
  const exBytes = await ex.save();
  ok((await PDFDocument.load(exBytes)).getPageCount()===3, 'extracted PDF has 3 pages');
  ok(JSON.stringify(parseRanges('3-1',5))==='[0,1,2]', 'reversed range "3-1" normalises to 1-3');
  ok(JSON.stringify(parseRanges('2,2,2',5))==='[1]', 'duplicate pages de-duplicated');
  await throws(()=>parseRanges('0-2',5), 'range below 1 rejected');
  await throws(()=>parseRanges('4-9',5), 'range beyond page count rejected');
  await throws(()=>parseRanges('abc',5), 'garbage input rejected');
  await throws(()=>parseRanges('',5),   'empty input rejected');

  console.log('\n== 3. Split PDF (every page → zip) ==');
  const zip = new JSZip();
  for(let i=0;i<5;i++){
    const d = await PDFDocument.create();
    const [p] = await d.copyPages(src5,[i]); d.addPage(p);
    zip.file('doc-page-'+(i+1)+'.pdf', await d.save());
  }
  const zipBuf = await zip.generateAsync({type:'nodebuffer',compression:'DEFLATE'});
  const zread = await JSZip.loadAsync(zipBuf);
  ok(Object.keys(zread.files).length===5, 'zip contains 5 per-page PDFs');
  const page3 = await zread.file('doc-page-3.pdf').async('nodebuffer');
  ok((await PDFDocument.load(page3)).getPageCount()===1, 'zip entry is a valid 1-page PDF');

  console.log('\n== 4. Compress PDF (balanced re-save) ==');
  const big = await makePdf(10,'C');
  const reload = await PDFDocument.load(big);
  const resaved = await reload.save({useObjectStreams:true});
  ok((await PDFDocument.load(resaved)).getPageCount()===10, 'balanced re-save keeps all 10 pages, output valid');
  console.log('        sizes: '+fmtBytes(big.length)+' → '+fmtBytes(resaved.length));

  console.log('\n== 5. Images → PDF ==');
  const ipdf = await PDFDocument.create();
  const png = await ipdf.embedPng(PNG_1x1);
  const A4=[595.28,841.89];
  const pg = ipdf.addPage(A4);
  const s = Math.min(A4[0]/png.width, A4[1]/png.height, Infinity);
  pg.drawImage(png,{x:(A4[0]-png.width*s)/2, y:(A4[1]-png.height*s)/2, width:png.width*s, height:png.height*s});
  const ibytes = await ipdf.save();
  ok((await PDFDocument.load(ibytes)).getPageCount()===1, 'PNG embedded into a valid 1-page PDF');

  console.log('\n== 6. Encrypted-PDF guard ==');
  // pdf-lib cannot create encrypted files; simulate the guard on corrupt input instead
  await throws(async()=>{ 
    try{ await PDFDocument.load(Buffer.from('not a pdf at all')); }
    catch(err){ if(/encrypt/i.test(String(err))) throw new Error('That PDF is password-protected — not supported yet.'); throw new Error('Could not read this PDF. The file may be damaged.'); }
  }, 'corrupt file rejected with friendly message');

  console.log('\n== 7. Password generator ==');
  for(const len of [8,16,64]){
    const pw = generatePassword(len, ['U','L','D','S'], true);
    ok(pw.length===len, 'length '+len+' respected → '+ (len===16?pw:'(hidden)'));
  }
  let allSetsOk=true, lookalikeOk=true;
  for(let i=0;i<300;i++){
    const pw = generatePassword(12, ['U','L','D','S'], true);
    if(!(/[A-Z]/.test(pw)&&/[a-z]/.test(pw)&&/[0-9]/.test(pw)&&/[!@#$%^&*()\-_=+\[\]{};:,.?]/.test(pw))) allSetsOk=false;
    if(/[l1O0I]/.test(pw)) lookalikeOk=false;
  }
  ok(allSetsOk, '300 samples: every selected charset always present');
  ok(lookalikeOk, '300 samples: look-alike chars (l 1 O 0 I) never appear when avoided');
  const bits=Math.round(16*Math.log2(SETS.U.safe.length+SETS.L.safe.length+SETS.D.safe.length+SETS.S.safe.length));
  ok(bits>=100, '16-char full-charset entropy ≈ '+bits+' bits (Excellent)');

  console.log('\n== 8. Word counter ==');
  const st = wordStats('Hello world! This is fine.\n\nNew paragraph here');
  ok(st.words===8, 'words = 8');
  ok(st.sent===2, 'sentences = 2 (trailing text without "." not miscounted)');
  ok(st.para===2, 'paragraphs = 2');
  ok(st.uniq===8, 'unique words = 8 (punctuation stripped)');
  const empty = wordStats('');
  ok(empty.words===0&&empty.sent===0&&empty.para===0, 'empty text → all zeros');

  console.log('\n== 9. fmtBytes ==');
  ok(fmtBytes(0)==='0 B'&&fmtBytes(1024)==='1.0 KB'&&fmtBytes(1536)==='1.5 KB'&&fmtBytes(10*1024*1024)==='10 MB', 'byte formatting: 0 B / 1.0 KB / 1.5 KB / 10 MB');

  console.log('\n=================================');
  console.log(' RESULT: '+pass+' passed, '+fail+' failed');
  console.log('=================================\n');
  process.exit(fail?1:0);
})().catch(e=>{console.error('SUITE CRASH:',e);process.exit(1);});
