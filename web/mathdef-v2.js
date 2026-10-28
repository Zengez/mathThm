"use strict";
/* v2 mathDef adapter shared by browser code and Node regression tests.
 * Consumers use canonical term-heading IDs; old original IDs and retired
 * group/meaning/formulation IDs resolve through mathDef's published aliases.
 * No ambiguous mathematical meaning is guessed by text matching.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==="object" && module.exports)module.exports=api;
  if(root)root.MathThmDefinitions=api;
})(typeof window==="object"?window:null,()=>{
  const norm=x=>String(x||"").trim().toLocaleLowerCase();
  function index(snapshot){
    if(snapshot?.schema!=="mathdef.definition-snapshot.v2" ||
       !Array.isArray(snapshot.definitions) || !snapshot.definitions.length)
      throw Error("Expected complete mathDef v2 definition snapshot");
    const groups=new Map(), oldIds=new Map(), meaningGroup=new Map(), formGroup=new Map();
    const register=(id,gid)=>{if(!id)return;
      if(oldIds.has(id) && oldIds.get(id)!==gid)
        throw Error("Conflicting mathDef legacy ID: "+id);
      oldIds.set(id,gid);
    };
    for(const g of snapshot.definitions){
      if(!g.id || groups.has(g.id) || !Array.isArray(g.meanings) ||
         !Array.isArray(g.formulations))throw Error("Invalid mathDef v2 group");
      groups.set(g.id,g);
      register(g.id,g.id);
      for(const oid of g.original_ids||[])register(oid,g.id);
      for(const m of g.meanings){
        if(meaningGroup.has(m.id))throw Error("Duplicate mathDef meaning ID");
        meaningGroup.set(m.id,g.id);register(m.id,g.id);
      }
      for(const f of g.formulations){
        if(formGroup.has(f.key) || !meaningGroup.has(f.meaning_id) ||
           meaningGroup.get(f.meaning_id)!==g.id)
          throw Error("Invalid mathDef formulation/meaning ownership");
        formGroup.set(f.key,g.id);register(f.key,g.id);
      }
    }
    const aliases=snapshot.consolidated_ids||{};
    for(const [kind,owners] of [
      ["group_aliases",oldIds],["meaning_aliases",meaningGroup],
      ["formulation_aliases",formGroup]]){
      const table=aliases[kind]||{};
      for(const [retired,live] of Object.entries(table)){
        const gid=owners.get(live);
        if(!gid)throw Error("Stale mathDef "+kind+" redirect: "+retired);
        register(retired,gid);
      }
    }
    return Object.freeze({
      groups, resolve(id){return groups.get(oldIds.get(id)||id)||null;},
      resolveId(id){return oldIds.get(id)||null;},
      meaningGroup, formGroup,
    });
  }
  function orderedForms(group,{sourceSubject=null,preferredMeaningId=null,
                              preferredFormulationId=null,legacyOriginalId=null}={}){
    if(!group)return [];
    const forms=group.formulations||[];
    const requested=norm(sourceSubject);
    const subjectMatch=requested && forms.some(f=>norm(f.subject)===requested);
    const hasOverride=preferredFormulationId &&
      forms.some(f=>f.key===preferredFormulationId);
    let originalMeaning=null;
    if(legacyOriginalId){
      const m=group.meanings?.find(m=>
        m.original_definition_id===legacyOriginalId ||
        (m.legacy_original_definition_ids||[]).includes(legacyOriginalId));
      originalMeaning=m?.id||null;
    }
    return forms.map((form,i)=>({form,i,score:[
      hasOverride && form.key===preferredFormulationId?0:(hasOverride?1:0),
      subjectMatch && norm(form.subject)===requested?0:(subjectMatch?1:0),
      preferredMeaningId && form.meaning_id===preferredMeaningId?0:
        (preferredMeaningId?1:0),
      originalMeaning && form.meaning_id===originalMeaning?0:(originalMeaning?1:0),
      i
    ]})).sort((a,b)=>{
      for(let i=0;i<a.score.length;i++){
        if(a.score[i]!==b.score[i])return a.score[i]-b.score[i];
      }
      return 0;
    }).map(x=>x.form);
  }
  // Mirrors mathDef's *current* portable recursive UI: block only canonical
  // definition headings on the active ancestry path, not unrelated siblings.
  // Resolve redirects before comparing IDs, so an old ID cannot re-open its
  // own canonical v2 heading through another spelling or alias.
  function branchPath(reference, ancestors, nextId, maxDepth=8){
    if(!reference || !Array.isArray(ancestors))return null;
    const path=ancestors.map(id=>reference.resolveId(id)).filter(Boolean);
    if(path.length!==ancestors.length || path.length>=maxDepth)return null;
    const next=reference.resolveId(nextId);
    if(!next || path.includes(next))return null;
    return [...path,next];
  }
  function visibleDependencies(reference, path, dependencies){
    if(!reference || !Array.isArray(path) || !Array.isArray(dependencies))return [];
    const blocked=new Set(path.map(id=>reference.resolveId(id)).filter(Boolean));
    const seen=new Set();
    return dependencies.flatMap(dep=>{
      const canonical=dep?.id && reference.resolveId(dep.id);
      if(!canonical || blocked.has(canonical) || seen.has(canonical) ||
         !branchPath(reference,path,canonical))return [];
      seen.add(canonical);
      return [{...dep,id:canonical}];
    });
  }
  return Object.freeze({index,orderedForms,branchPath,visibleDependencies});
});
