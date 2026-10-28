"use strict";
const assert=require("node:assert/strict");
const test=require("node:test");
const {index,orderedForms,branchPath,visibleDependencies}=require("../web/mathdef-v2.js");
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


function recursiveSample(){
 const v=sample();
 v.definitions[0].term="Subspace topology";
 v.definitions[0].aliases=["Subspace topology"];
 v.definitions[0].original_ids=["topology.subspace-topology"];
 v.definitions.push({
   id:"g.topology",term:"Topology",aliases:["Topological structure"],
   meanings:[{id:"m.topology",subject:"Topology"}],
   formulations:[{key:"f.topology",meaning_id:"m.topology",subject:"Topology",
     body:"A topology is a collection of open sets.",dependencies:[]}],
 });
 v.definitions.push({
   id:"g.compact",term:"Compactness",aliases:["Compact space"],
   meanings:[{id:"m.compact",subject:"Topology"}],
   formulations:[{key:"f.compact",meaning_id:"m.compact",subject:"Topology",
     body:"Every open cover has a finite subcover.",dependencies:[]}],
 });
 return v;
}
test("recursive paths use canonical v2 IDs, suppress self and every ancestor",()=>{
 const x=index(recursiveSample());
 assert.deepEqual(branchPath(x,[],"topology.subspace-topology"),["g.basis"]);
 assert.equal(branchPath(x,["g.basis"],"topology.subspace-topology"),null);
 assert.equal(branchPath(x,["topology.subspace-topology"],"g.basis"),null);
 assert.deepEqual(branchPath(x,["g.basis"],"g.topology"),["g.basis","g.topology"]);
 assert.equal(branchPath(x,["g.basis","g.topology"],"topology.subspace-topology"),null);
 assert.deepEqual(branchPath(x,["g.basis","g.topology"],"g.compact"),
                  ["g.basis","g.topology","g.compact"]);
 // Separate branches may still expand the same term, just as mathDef's
 // current implementation permits.
 assert.deepEqual(branchPath(x,["g.topology"],"g.basis"),["g.topology","g.basis"]);
 assert.equal(branchPath(x,Array(8).fill("g.topology"),"g.compact"),null);
});
test("visible nested dependencies suppress aliases, self, ancestors and duplicates",()=>{
 const x=index(recursiveSample());
 const dependencies=[
   {id:"topology.subspace-topology",source_phrase:"self"},
   {id:"g.basis",source_phrase:"same via canonical ID"},
   {id:"g.topology",source_phrase:"parent"},
   {id:"g.compact",source_phrase:"valid"},
   {id:"g.compact",source_phrase:"duplicate"},
   {id:"unknown",source_phrase:"unresolvable"},
 ];
 const visible=visibleDependencies(x,["topology.subspace-topology","g.topology"],dependencies);
 assert.deepEqual(visible.map(d=>d.id),["g.compact"]);
 assert.equal(visible[0].source_phrase,"valid");
});
