"use strict";
const assert=require("node:assert/strict");
const test=require("node:test");
const {index,orderedForms}=require("../web/mathdef-v2.js");
function sample(){
 return {schema:"mathdef.definition-snapshot.v2",
  consolidated_ids:{
   group_aliases:{"g.old":"g.basis"},
   meaning_aliases:{"m.old":"m.top"},
   formulation_aliases:{"f.old":"f.top"},
  }, definitions:[{
   id:"g.basis",term:"Basis",aliases:[],original_ids:["linear.basis"],
   meanings:[{id:"m.top",subject:"Topology",original_definition_id:"linear.basis"},
             {id:"m.alg",subject:"Algebra"}],
   formulations:[{key:"f.top",meaning_id:"m.top",subject:"Topology",body:"Topological."},
                 {key:"f.alg",meaning_id:"m.alg",subject:"Algebra",body:"Algebraic."}],
  }]};
}
test("canonical v2 IDs, original IDs, and all cleanup redirects resolve",()=>{
 const x=index(sample());
 for(const id of ["g.basis","g.old","linear.basis","m.top","m.old","f.top","f.old"])
   assert.equal(x.resolve(id).term,"Basis");
 assert.equal(x.resolve("unknown"),null);
});
test("exact source Subject outranks fallback legacy original ID",()=>{
 const group=index(sample()).resolve("linear.basis");
 assert.deepEqual(orderedForms(group,{sourceSubject:"  aLgEbRa  ",legacyOriginalId:"linear.basis"})
   .map(x=>x.key),["f.alg","f.top"]);
 assert.equal(orderedForms(group,{sourceSubject:"Geometry",legacyOriginalId:"linear.basis"})[0].key,"f.top");
});
test("explicit approved target beats Subject; meaning preference breaks Subject ties",()=>{
 const group=index(sample()).resolve("g.basis");
 assert.equal(orderedForms(group,{sourceSubject:"Topology",preferredFormulationId:"f.alg"})[0].key,"f.alg");
 assert.equal(orderedForms(group,{sourceSubject:"Geometry",preferredMeaningId:"m.alg"})[0].key,"f.alg");
 assert.equal(orderedForms(group,{sourceSubject:"Topology",preferredFormulationId:"nonexistent"})[0].key,"f.top");
});
test("stale cleanup meaning redirects fail rather than choosing a wrong link",()=>{
 const s=sample();s.consolidated_ids.meaning_aliases["unknown"]="m.missing";
 assert.throws(()=>index(s),/Stale mathDef meaning_aliases/);
});
test("duplicate v2 formulation IDs fail integrity validation",()=>{
 const s=sample();s.definitions[0].formulations[1].key="f.top";
 assert.throws(()=>index(s),/Invalid mathDef formulation/);
});
