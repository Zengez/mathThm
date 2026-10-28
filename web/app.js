"use strict";
(() => {
  const $=id=>document.getElementById(id), core=window.MathThmSearch;
  const mathdef=window.MathThmDefinitions;
  const state={records:[],mode:"auto",expanded:new Set(),defs:new Map(),
    definitions:null,fullHtmlCache:new Map(),snapshotVersion:null};
  const resolve=id=>state.definitions?.resolve(id)||state.defs.get(id)||null;
  const esc=x=>String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const href=u=>/^https:\/\//i.test(String(u))?esc(u):"#";
  const math=root=>{if(window.renderMathInElement)window.renderMathInElement(root,{
    delimiters:[{left:"$$",right:"$$",display:true},{left:"\\[",right:"\\]",display:true},
      {left:"\\(",right:"\\)",display:false},{left:"$",right:"$",display:false}],throwOnError:false,strict:"ignore"})};
  const splitMath=s=>String(s).split(/(\$\$[\s\S]*?\$\$|\$[^$]*\$|\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\])/g);
  const escapeRE=label=>[...label].map(c=>"\\^$.*+?()[]{}|".includes(c)?"\\"+c:c).join("");
  const regexFor=label=>new RegExp("(^|[^\\p{L}\\p{N}_])("+escapeRE(label)+")(?=$|[^\\p{L}\\p{N}_])","giu");
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
    for(const c of labels)c.regex=regexFor(c.label);
  }
  function linkified(text,theorem,path=[]){
    const hints=(theorem?.link_hints||[]).filter(h=>Array.isArray(h)&&resolve(h[1]))
      .map(h=>({label:h[0],id:resolve(h[1]).id,originalId:h[1]}));
    const candidates=[...hints,...labels];
    return splitMath(text).map(part=>{
      if(!part)return "";
      if(/^(?:\$|\\\(|\\\[)/.test(part))return esc(part);
      const options=[];
      for(const c of candidates){
        const blocked=Boolean(state.definitions &&
          !mathdef.branchPath(state.definitions,path,c.id));
        const regex=c.regex || regexFor(c.label);
        regex.lastIndex=0;
        let m;
        while((m=regex.exec(part))){
          const start=m.index+m[1].length,end=start+m[2].length;
          options.push({start,end,id:c.id,originalId:c.originalId,
            blocked,explicit:Boolean(c.originalId)});
        }
      }
      // Longest whole phrase wins, even when its link is blocked by ancestry.
      // Reserve the span so e.g. the 'topology' inside an unavailable
      // 'subspace topology' link does not acquire a misleading shorter link.
      options.sort((a,b)=>(b.end-b.start)-(a.end-a.start)||
        Number(b.explicit)-Number(a.explicit)||a.start-b.start);
      const chosen=[];
      for(const c of options){
        if(chosen.some(x=>c.start<x.end&&c.end>x.start))continue;
        chosen.push(c);
      }
      chosen.sort((a,b)=>a.start-b.start);
      let result="",pos=0;
      for(const c of chosen){
        result+=esc(part.slice(pos,c.start));
        if(!c.blocked){
          result+='<button type="button" class="definition-link" data-def-id="'+esc(c.id)+
            '" data-def-path="'+esc(JSON.stringify(path))+
            '" data-source-subject="'+esc(theorem?.area||"")+
            '" data-original-def-id="'+esc(c.originalId||"")+
            '" title="Expand mathDef v2 definition">'+esc(part.slice(c.start,c.end))+'</button>';
        }else result+=esc(part.slice(c.start,c.end));
        pos=c.end;
      }
      return result+esc(part.slice(pos));
    }).join("");
  }
  const paras=(text,theorem,path=[])=>String(text).split(/\n\s*\n/).map(p=>"<p>"+linkified(p,theorem,path).replace(/\n/g," ")+"</p>").join("");
  const preview=(text,n=175)=>text.length<=n?text:text.slice(0,Math.max(90,text.slice(0,n).lastIndexOf(" ")))+"…";
  function card(hit,total){
    const t=hit.theorem,full=core.modeFor(state.mode,total,state.expanded.has(t.id))==="full";
    const hq=$("hypothesis-query").value.trim(),cq=$("conclusion-query").value.trim();
    const tags=[hq&&hit.hypothesisHit.why==="tag"?"Hypothesis tag: "+hit.hypothesisHit.tag:"",
      cq&&hit.conclusionHit.why==="tag"?"Conclusion tag: "+hit.conclusionHit.tag:""].filter(Boolean);
    const body=full?'<div class="statement">'+(state.fullHtmlCache.get(t.id)||(()=>{const h=paras(t.statement,t);state.fullHtmlCache.set(t.id,h);return h;})())+'</div>':
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
    const branch=mathdef.branchPath(state.definitions,path,id);
    if(!branch)return; // suppress self-links, ancestors, aliases and over-deep links
    id=branch[branch.length-1];
    // Insert beneath the containing paragraph (or dependency controls), not mid-sentence.
    const host=target.closest("p") || target.closest(".def-dependencies") || target;
    const existing=host.nextElementSibling;
    if(existing?.classList.contains("definition-insert")){
      existing.remove();target.setAttribute("aria-expanded","false");
      if(existing.dataset.definitionId===id)return;
    }
    const d=resolve(id),el=document.createElement("div");
    el.className="definition-insert";el.dataset.definitionId=id;
    if(!d)el.textContent="This mathDef definition is not currently available: "+id;
    else{
      const forms=mathdef.orderedForms(d,{
        sourceSubject:target.dataset.sourceSubject||"",
        preferredMeaningId:target.dataset.preferredMeaning||null,
        preferredFormulationId:target.dataset.preferredFormulation||null,
        legacyOriginalId:target.dataset.originalDefId||null,
      });
      const best=forms[0];
      // Every inline cue in every formulation carries the canonical path,
      // including this currently open definition, not just its parents.
      const formBody=(f)=>paras(f.body||d.body||"",{area:f.subject||""},branch);
      const cited=best?.source||d.source;
      const sourceLink=cited&&/^https:\/\//i.test(cited)?
        '<a class="source" href="'+href(cited)+'" target="_blank" rel="noopener noreferrer">Definition source ↗</a>':
        '<a class="source" href="https://zengez.github.io/mathDef/" target="_blank" rel="noopener noreferrer">View mathDef ↗</a>';
      el.innerHTML='<h5>Definition: '+esc(d.term)+'</h5><div class="definition">'+
        formBody(best)+'</div>'+sourceLink+
        (forms.length>1?'<details><summary>'+forms.length+' contextual formulations</summary>'+
          forms.slice(1).map(f=>'<div class="definition"><p><strong>'+
            esc(f.label||f.subject||"Alternative")+'</strong></p>'+formBody(f)+'</div>').join("")+
          '</details>':"");
      // Reference per-formulation dependencies, not group-wide dependencies
      // from a possibly different mathematical context.
      const deps=mathdef.visibleDependencies(state.definitions,branch,best?.dependencies||[]);
      if(deps.length){
        const wrap=document.createElement("div");wrap.className="def-dependencies";const seen=new Set();
        for(const v of deps.slice(0,16)){
          const resolved=resolve(v.id);if(seen.has(resolved.id))continue;seen.add(resolved.id);
          const b=document.createElement("button");b.type="button";b.dataset.defId=resolved.id;
          b.dataset.defPath=JSON.stringify(branch);
          b.dataset.sourceSubject=best.subject||"";
          b.dataset.preferredMeaning=v.target_meaning||"";
          b.dataset.preferredFormulation=v.preferred_formulation||"";
          b.textContent="Definition: "+resolved.term;wrap.append(b);
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
  async function liveV2(){
    const base="https://zengez.github.io/mathDef/api/definitions/v2/";
    const manifest=await json(base+"manifest.json");
    if(manifest.schema!=="mathdef.definition-manifest.v2" ||
       manifest.snapshot_schema!=="mathdef.definition-snapshot.v2" ||
       manifest.dataset!=="merged" ||
       !/^[0-9a-f]{64}$/.test(manifest.sha256||"") ||
       manifest.version!=="sha256:"+manifest.sha256 ||
       manifest.snapshot_path!=="snapshot.json")throw Error("Unexpected mathDef v2 manifest");
    const response=await fetch(base+manifest.snapshot_path+"?v="+manifest.sha256,
                               {cache:"no-cache"});
    if(!response.ok)throw Error("HTTP "+response.status);
    const raw=await response.arrayBuffer();
    if(!globalThis.crypto?.subtle)throw Error("Web Crypto checksum unavailable");
    const digest=Array.from(new Uint8Array(await globalThis.crypto.subtle.digest("SHA-256",raw)))
      .map(x=>x.toString(16).padStart(2,"0")).join("");
    if(digest!==manifest.sha256)throw Error("mathDef v2 snapshot integrity check failed");
    const defs=JSON.parse(new TextDecoder().decode(raw));
    if(defs.definitions?.length!==manifest.definition_count)throw Error("Incomplete mathDef v2");
    return defs;
  }
  async function loadMathDef(){
    let defs,from="";
    try{
      defs=await json("./mathdef-snapshot.json");from="verified site-build v2 snapshot";
      if(defs?.schema!=="mathdef.definition-snapshot.v2")
        throw Error("Old or invalid site-build snapshot");
    }catch(_e){
      try{defs=await liveV2();from="live verified v2 snapshot";}
      catch(_e2){/* Theorem search remains usable if feed is unavailable. */}
    }
    try{
      if(!defs)throw Error("No available mathDef feed");
      const reference=mathdef.index(defs);
      state.definitions=reference;
      state.defs=reference.groups;
      state.fullHtmlCache.clear();
      state.snapshotVersion="v2";
      rebuildLabels();
      $("definitions-status").textContent="mathDef v2 definitions loaded ("+
        state.defs.size+" terms; "+from+
        "). Click a linked mathematical term to expand its definition here.";
      render();
    }catch(error){
      $("definitions-status").textContent=
        "mathDef v2 definitions unavailable. Theorem search still works; definition expansion requires a verified v2 snapshot.";
      console.warn("mathThm mathDef v2 loader:",error.message);
    }
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
