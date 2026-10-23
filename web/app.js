"use strict";
(() => {
  const $=id=>document.getElementById(id), core=window.MathThmSearch;
  const state={records:[],mode:"auto",expanded:new Set(),defs:new Map()};
  const esc=x=>String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const href=u=>/^https:\/\//i.test(String(u))?esc(u):"#";
  const math=root=>{if(window.renderMathInElement)window.renderMathInElement(root,{
    delimiters:[{left:"$$",right:"$$",display:true},{left:"\\[",right:"\\]",display:true},
      {left:"\\(",right:"\\)",display:false},{left:"$",right:"$",display:false}],throwOnError:false,strict:"ignore"})};
  const splitMath=s=>String(s).split(/(\$\$[\s\S]*?\$\$|\$[^$]*\$|\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\])/g);
  let labels=[];
  function rebuildLabels(){
    labels=[];
    const index=new Map();
    for(const d of state.defs.values())for(const label of [d.term,...(d.aliases||[])]){
      if(typeof label!=="string"||label.length<5||/[$\\]/.test(label))continue;
      const key=label.toLowerCase();
      if(!index.has(key))index.set(key,new Set());
      index.get(key).add(d.id);
    }
    for(const [label,ids] of index)if(ids.size===1)labels.push({label,id:[...ids][0]});
    labels.sort((a,b)=>b.label.length-a.label.length);
  }
  function linkified(text,theorem){
    const hints=(theorem?.link_hints||[]).filter(h=>Array.isArray(h)&&state.defs.has(h[1]))
      .map(h=>({label:h[0],id:h[1]}));
    const candidates=[...hints,...labels];
    return splitMath(text).map(part=>{
      if(!part)return "";
      if(/^(?:\$|\\\(|\\\[)/.test(part))return esc(part);
      const chosen=[];
      for(const c of candidates){
        const regex=new RegExp("(^|[^\\p{L}\\p{N}_])("+c.label.replace(/[.*+?^\x24{}()|[\]\\]/g,"\\$&")+")(?=$|[^\\p{L}\\p{N}_])","giu");
        let m;
        while((m=regex.exec(part))){
          const start=m.index+m[1].length,end=start+m[2].length;
          if(chosen.some(x=>start<x.end&&end>x.start))continue;
          chosen.push({start,end,id:c.id});
        }
      }
      chosen.sort((a,b)=>a.start-b.start);
      let result="",pos=0;
      for(const c of chosen){
        result+=esc(part.slice(pos,c.start));
        result+='<button type="button" class="definition-link" data-def-id="'+esc(c.id)+'" title="Expand mathDef definition">'+esc(part.slice(c.start,c.end))+'</button>';
        pos=c.end;
      }
      return result+esc(part.slice(pos));
    }).join("");
  }
  const paras=(text,theorem)=>String(text).split(/\n\s*\n/).map(p=>"<p>"+linkified(p,theorem).replace(/\n/g," ")+"</p>").join("");
  const preview=(text,n=175)=>text.length<=n?text:text.slice(0,Math.max(90,text.slice(0,n).lastIndexOf(" ")))+"…";
  function card(hit,total){
    const t=hit.theorem,full=core.modeFor(state.mode,total,state.expanded.has(t.id))==="full";
    const hq=$("hypothesis-query").value.trim(),cq=$("conclusion-query").value.trim();
    const tags=[hq&&hit.hypothesisHit.why==="tag"?"Hypothesis tag: "+hit.hypothesisHit.tag:"",
      cq&&hit.conclusionHit.why==="tag"?"Conclusion tag: "+hit.conclusionHit.tag:""].filter(Boolean);
    const body=full?'<div class="statement">'+paras(t.statement,t)+'</div>':
      '<div class="preview-layout"><div class="preview-column"><h5>Hypotheses</h5><p>'+esc(preview(t.hypotheses.join(" ")))+'</p></div>'+
      '<div class="preview-column"><h5>Conclusions</h5><p>'+esc(preview(t.conclusions.join(" ")))+'</p></div></div>';
    const proofs=(t.proofs||[]).map((p,i)=>'<a href="'+href(p.url)+'" target="_blank" rel="noopener noreferrer">Proof '+(i+1)+' ↗</a>').join("");
    const issue="https://github.com/Zengez/mathThm/issues/new?title="+encodeURIComponent("Correction: "+t.id)+
      "&body="+encodeURIComponent("Theorem ID: "+t.id+"\nSource: "+t.source_url+"\n\nSuggested correction:\n");
    return '<article class="theorem-card" data-theorem-id="'+esc(t.id)+'"><div class="card-top"><div>'+
      '<div class="subject">'+esc(t.area||"Mathematics")+'</div><h4>'+esc(t.title||"Unnamed result")+'</h4></div>'+
      '<span class="proof-status">Cursory-screened · Unverified</span></div>'+body+
      (tags.length?'<div>'+tags.map(x=>'<span class="tag-hit">'+esc(x)+'</span>').join(" ")+'</div>':"")+
      '<div class="card-footer">'+(state.mode==="full"?"":'<button class="expand-button" data-toggle-id="'+esc(t.id)+'" aria-expanded="'+full+'">'+(full?"Show compact":"Read full theorem")+'</button>')+
      '<a href="'+href(t.source_url)+'" target="_blank" rel="noopener noreferrer">Source ↗</a>'+proofs+
      '<a href="'+esc(issue)+'" target="_blank" rel="noopener noreferrer">Suggest correction ↗</a></div></article>';
  }
  function render(){
    const hits=core.search(state.records,$("hypothesis-query").value,$("conclusion-query").value);
    $("result-count").textContent=hits.length+" result"+(hits.length===1?"":"s");
    const mode=core.modeFor(state.mode,hits.length);
    $("results-summary").textContent=(hits.length===state.records.length?"All prototype results":"Filtered results")+
      " · "+(mode==="compact"?"Compact previews":"Full statements")+" · Populated search columns are joined by AND.";
    $("results").innerHTML=hits.length?hits.map(h=>card(h,hits.length)).join(""):
      '<div class="empty">No matching results among the 20 prototype theorems. Try a broader term or clear one side.</div>';
    math($("results"));
  }
  function appendDefinition(target,id,path=[]){
    if(path.includes(id)||path.length>=8)return;
    // Insert beneath the containing paragraph (or dependency controls), not mid-sentence.
    const host=target.closest("p") || target.closest(".def-dependencies") || target;
    const existing=host.nextElementSibling;
    if(existing?.classList.contains("definition-insert")){
      existing.remove();target.setAttribute("aria-expanded","false");
      if(existing.dataset.definitionId===id)return;
    }
    const d=state.defs.get(id),el=document.createElement("div");
    el.className="definition-insert";el.dataset.definitionId=id;
    if(!d)el.textContent="This mathDef definition is not currently available: "+id;
    else{
      const forms=d.formulations?.length?d.formulations:[{key:"primary",body:d.body,source:d.source,label:"Definition"}],best=forms[0];
      el.innerHTML='<h5>Definition: '+esc(d.term)+'</h5><div class="definition">'+paras(best.body||d.body||"",null)+'</div>'+
        '<a class="source" href="'+href(best.source||d.source)+'" target="_blank" rel="noopener noreferrer">Definition source ↗</a>'+
        (forms.length>1?'<details><summary>'+forms.length+' contextual formulations</summary>'+
          forms.slice(1).map(f=>'<div class="definition"><p><strong>'+esc(f.label||"Alternative")+'</strong></p>'+paras(f.body||"",null)+'</div>').join("")+'</details>':"");
      const deps=(d.dependencies||[]).filter(v=>v?.id&&state.defs.has(v.id)&&!path.includes(v.id)&&v.id!==id);
      if(deps.length){
        const wrap=document.createElement("div");wrap.className="def-dependencies";const seen=new Set();
        for(const v of deps.slice(0,16)){
          if(seen.has(v.id))continue;seen.add(v.id);
          const b=document.createElement("button");b.type="button";b.dataset.defId=v.id;
          b.dataset.defPath=JSON.stringify([...path,id]);b.textContent="Definition: "+state.defs.get(v.id).term;wrap.append(b);
        }
        el.append(wrap);
      }
    }
    host.after(el);target.setAttribute("aria-expanded","true");math(el);
  }
  async function json(url){
    const response=await fetch(url,{cache:"no-cache"});
    if(!response.ok)throw new Error("HTTP "+response.status+" for "+url);
    return response.json();
  }
  async function loadMathDef(){
    let defs,from="";
    try{defs=await json("./mathdef-snapshot.json");from="site-build snapshot";}
    catch(_e){try{
      const base="https://zengez.github.io/mathDef/api/definitions/v1/";
      const manifest=await json(base+"manifest.json");
      defs=await json(base+manifest.snapshot_path+"?v="+encodeURIComponent(manifest.sha256));
      from="live snapshot";
    }catch(_e2){/* Search still works without optional definition service. */}}
    if(Array.isArray(defs?.definitions)&&defs.definitions.length){
      state.defs=new Map(defs.definitions.map(d=>[d.id,d]));rebuildLabels();
      $("definitions-status").textContent="mathDef definitions loaded ("+state.defs.size+
        "; "+from+"). Click a linked mathematical term to expand its definition here.";render();
    }else $("definitions-status").textContent="mathDef definitions unavailable. Search and proof links work; definition expansion requires the snapshot.";
  }
  async function init(){
    try{
      const result=await json("./theorems.json");
      if(result.schema!=="maththm.theorems.v1"||!Array.isArray(result.records))throw Error("Unexpected catalog format");
      state.records=result.records;$("total").textContent=result.records.length+" draft results";
      render();loadMathDef();
    }catch(e){$("error").hidden=false;$("error").textContent="Could not load theorem records: "+e.message;}
  }
  for(const key of ["hypothesis-query","conclusion-query"])$(key).addEventListener("input",()=>{state.expanded.clear();render()});
  document.querySelectorAll("[data-view]").forEach(button=>button.addEventListener("click",()=>{
    state.mode=button.dataset.view;state.expanded.clear();
    document.querySelectorAll("[data-view]").forEach(b=>{b.classList.toggle("active",b===button);b.setAttribute("aria-pressed",String(b===button));});render();
  }));
  $("clear-search").addEventListener("click",()=>{
    $("hypothesis-query").value="";$("conclusion-query").value="";state.expanded.clear();render();$("hypothesis-query").focus();
  });
  $("results").addEventListener("click",event=>{
    const button=event.target.closest("[data-toggle-id]");
    if(button){const id=button.dataset.toggleId;if(state.expanded.has(id))state.expanded.delete(id);else state.expanded.add(id);render();return;}
    const def=event.target.closest("[data-def-id]");
    if(def)appendDefinition(def,def.dataset.defId,JSON.parse(def.dataset.defPath||"[]"));
  });
  init();
})();
