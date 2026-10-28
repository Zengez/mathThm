"use strict";
/* Browser/Node mathDef v2 phrase matcher.
 * Longest phrase wins; never guess between unresolved homonymous headings.
 * Includes a SMALL reviewed adjective-to-noun map, not a general stemmer.
 * Excludes TeX spans at the rendering boundary, never edits definitions.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==="object" && module.exports)module.exports=api;
  if(root)root.MathThmLinks=api;
})(typeof window==="object"?window:null,()=>{
  const WORD=/[\p{L}\p{N}]+/gu;
  const PREVIEW_ALIASES=Object.freeze([
    ["uniformly continuous","analysis.uniform-continuity"],
    ["continuous","topology.continuity"],
    ["compact","topology.compactness"],
    ["connected","topology.connected-space"],
    ["closed","topology.closed-set"]
  ]);
  const words=text=>Array.from(String(text||"").matchAll(WORD),
    m=>({key:m[0].normalize("NFKC").toLowerCase(),start:m.index,end:m.index+m[0].length}));
  const keyFor=text=>words(text).map(w=>w.key).join(" ");
  function create(reference,aliases=PREVIEW_ALIASES){
    if(!reference?.groups||!reference?.resolveId)throw Error("Expected mathDef v2 reference index");
    const root={next:new Map(),options:[]};
    const diagnostics={unresolvedCurated:[]};
    function insert(label,target,kind){
      if(typeof label!=="string" || /[$\\]/.test(label))return;
      const tok=words(label);
      if(!tok.length || tok.length>9 || (kind==="auto" && label.trim().length<5))return;
      const canonical=reference.resolveId(target);
      if(!canonical){if(kind==="curated")diagnostics.unresolvedCurated.push({label,target});return;}
      let node=root;
      for(const t of tok){
        if(!node.next.has(t.key))node.next.set(t.key,{next:new Map(),options:[]});
        node=node.next.get(t.key);
      }
      if(!node.options.some(o=>o.id===canonical && o.kind===kind))
        node.options.push({id:canonical,kind});
    }
    for(const d of reference.groups.values()){
      insert(d.term,d.id,"auto");
      for(const label of d.aliases||[])insert(label,d.id,"auto");
    }
    for(const [label,target] of aliases)insert(label,target,"curated");
    const subjectMatches=(id,subject)=>{
      if(!subject)return false;
      const g=reference.groups.get(id);
      const s=subject.normalize("NFKC").trim().toLowerCase();
      return (g?.meanings||[]).some(m=>String(m.subject||"").trim().toLowerCase()===s)||
             (g?.formulations||[]).some(f=>String(f.subject||"").trim().toLowerCase()===s);
    };
    function select(options,subject){
      const curated=[...new Set(options.filter(o=>o.kind==="curated").map(o=>o.id))];
      if(curated.length===1)return {id:curated[0],reason:"curated"};
      if(curated.length>1)return {id:null,reason:"ambiguous-curated"};
      const ids=[...new Set(options.map(o=>o.id))];
      if(ids.length===1)return {id:ids[0],reason:"unique"};
      const qualified=ids.filter(id=>subjectMatches(id,subject));
      if(qualified.length===1)return {id:qualified[0],reason:"unique-subject"};
      return {id:null,reason:"ambiguous"};
    }
    function match(text,{subject="",path=[],hints=[],excluded=[]}={}){
      const seen=words(text),opts=[];
      // Scan all token positions against the indexed phrase tree.
      for(let start=0;start<seen.length;start++){
        let node=root;
        for(let end=start;end<seen.length && end<start+9;end++){
          node=node.next.get(seen[end].key);
          if(!node)break;
          if(node.options.length){
            const chosen=select(node.options,subject);
            opts.push({start:seen[start].start,end:seen[end].end,
              id:chosen.id,reason:chosen.reason,priority:1});
          }
        }
      }
      // Explicit theorem hints are strictly local, not global semantic aliases.
      for(const hint of hints){
        if(!Array.isArray(hint)||hint.length!==2||typeof hint[0]!=="string")continue;
        const canonical=reference.resolveId(hint[1]);
        if(!canonical)continue;
        const phrase=words(hint[0]);if(!phrase.length)continue;
        for(let start=0;start<=seen.length-phrase.length;start++){
          if(!phrase.every((p,i)=>p.key===seen[start+i].key))continue;
          opts.push({start:seen[start].start,end:seen[start+phrase.length-1].end,
            id:canonical,reason:"explicit",priority:3,originalId:hint[1]});
        }
      }
      // Longest phrase wins even if unresolved/blocked, preventing a weaker
      // interior link from misrepresenting a compound technical expression.
      opts.sort((a,b)=>(b.end-b.start)-(a.end-a.start)||
        b.priority-a.priority||a.start-b.start||
        String(a.id).localeCompare(String(b.id)));
      const selected=[],excludedSet=new Set(excluded.map(id=>reference.resolveId(id)).filter(Boolean));
      for(const o of opts){
        if(selected.some(s=>o.start<s.end && o.end>s.start))continue;
        const canonical=o.id;
        const ancestors=path.map(id=>reference.resolveId(id));
        const available=canonical && !excludedSet.has(canonical) &&
          ancestors.length===path.length && ancestors.length<8 &&
          !ancestors.includes(canonical);
        selected.push({...o,blocked:!available});
      }
      return selected.sort((a,b)=>a.start-b.start);
    }
    return Object.freeze({match,diagnostics,termCount:reference.groups.size});
  }
  return Object.freeze({create,words,keyFor,PREVIEW_ALIASES});
});
