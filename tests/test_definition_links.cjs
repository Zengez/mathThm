"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const adapter=require("../web/mathdef-v2.js"),links=require("../web/definition-links.js");
function group(id,term,original,subject,aliases=[]){
  const meaning="m."+id;
  return {id,term,aliases,original_ids:original?[original]:[],
    meanings:[{id:meaning,subject}],
    formulations:[{key:"f."+id,meaning_id:meaning,subject,body:"Example definition.",dependencies:[]}]};
}
function fixture(){
  const definitions=[
    group("g.continuity","Continuous function (topological)","topology.continuity","Topology"),
    group("g.uniform","Uniform continuity","analysis.uniform-continuity","Analysis"),
    group("g.compact","Compact space","topology.compactness","Topology"),
    group("g.connected","Connected space","topology.connected-space","Topology"),
    group("g.closed","Closed set","topology.closed-set","Topology"),
    group("g.subspace","Subspace topology","topology.subspace-topology","Topology"),
    group("g.topology","Topology","topology.topological-space","Topology"),
    group("g.amb-one","Spectrum",null,"Algebra"),
    group("g.amb-two","Spectrum",null,"Analysis")
  ];
  return adapter.index({schema:"mathdef.definition-snapshot.v2",definitions,
    consolidated_ids:{group_aliases:{},meaning_aliases:{},formulation_aliases:{}}});
}
const scan=(text,context={})=>links.create(fixture()).match(text,context);
test("Heine Cantor: uniformly continuous is a single longer link and continuous is distinct",()=>{
  const hits=scan("Every continuous function on a compact space is uniformly continuous.",{subject:"Analysis"});
  const text="Every continuous function on a compact space is uniformly continuous.";
  const asLabels=hits.map(h=>[text.slice(h.start,h.end),h.id,h.blocked]);
  assert.deepEqual(asLabels,[
    ["continuous","g.continuity",false],
    ["compact","g.compact",false],
    ["uniformly continuous","g.uniform",false]]);
});
test("does not match adjective embedded in larger word; identical repeated occurrences behave consistently",()=>{
  const txt="A continuous map is continuous; a discontinuous map is not continuous.";
  assert.deepEqual(scan(txt).map(x=>txt.slice(x.start,x.end)),
    ["continuous","continuous","continuous"]);
});
test("matching is phrase-wide, respects punctuation and keeps math out at the renderer boundary",()=>{
  const hits=scan("Subspace topology, topology and uniform continuity.",{subject:"Topology"});
  assert.deepEqual(hits.map(x=>x.id),["g.subspace","g.topology","g.uniform"]);
});
test("ambiguous same-term headings are unlinked without unique mathematical context",()=>{
  const no=scan("The spectrum of an operator.");
  assert.equal(no[0].id,null);
  assert.equal(no[0].blocked,true);
  const algebra=scan("The spectrum of an operator.",{subject:"Algebra"});
  assert.equal(algebra[0].id,"g.amb-one");
  const analysis=scan("The spectrum of an operator.",{subject:"Analysis"});
  assert.equal(analysis[0].id,"g.amb-two");
});
test("explicit hints win for equal phrases, but never override ancestry protection",()=>{
  const index=fixture();
  const matcher=links.create(index);
  const explicit=matcher.match("A spectrum is continuous.",{
    subject:"Analysis",hints:[["spectrum","g.amb-one"]],path:[]});
  assert.equal(explicit[0].id,"g.amb-one");
  const blocked=matcher.match("Subspace topology contains a topology.",{
    path:["topology.subspace-topology"],subject:"Topology"});
  assert.equal(blocked[0].id,"g.subspace");
  assert.equal(blocked[0].blocked,true);
  assert.equal(blocked[1].id,"g.topology");
  assert.equal(blocked[1].blocked,false);
});
test("curated aliases are only used when the target v2 group exists",()=>{
  const lone=adapter.index({schema:"mathdef.definition-snapshot.v2",
    definitions:[group("g.only","Topology",null,"Topology")],
    consolidated_ids:{group_aliases:{},meaning_aliases:{},formulation_aliases:{}}});
  const matcher=links.create(lone);
  assert.equal(matcher.match("uniformly continuous").length,0);
  assert.ok(matcher.diagnostics.unresolvedCurated.length>=1);
});
test("constant-time-ish indexed scanner handles many candidate labels without duplicate links",()=>{
  const idx=fixture();
  const matcher=links.create(idx);
  const results=matcher.match("a compact and connected subspace topology is closed");
  assert.deepEqual(results.map(r=>r.id),["g.compact","g.connected","g.subspace","g.closed"]);
  assert.equal(new Set(results.map(r=>r.start)).size,results.length);
});
