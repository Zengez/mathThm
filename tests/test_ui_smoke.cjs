"use strict";
const test=require("node:test"), assert=require("node:assert/strict");
const fs=require("node:fs"), path=require("node:path"), vm=require("node:vm");
const core=require("../web/search-core.js");
const adapter=require("../web/mathdef-v2.js");
const records=JSON.parse(fs.readFileSync(path.join(__dirname,"../data/theorems.json"),"utf8"));
function element(){
  return {value:"",textContent:"",innerHTML:"",hidden:true,listeners:{},addEventListener(type,fn){this.listeners[type]=fn;},
    focus(){},setAttribute(){}};
}
test("browser-like boot renders live theorem and mathDef-linked full statement",async()=>{
  const ids=["hypothesis-query","conclusion-query","results","total","result-count","results-summary",
    "definitions-status","error","clear-search"];
  const els=Object.fromEntries(ids.map(k=>[k,element()]));
  const snapshot={schema:"mathdef.definition-snapshot.v2",consolidated_ids:{group_aliases:{},meaning_aliases:{},formulation_aliases:{}},definitions:[
    {id:"term.compact",term:"Compact space",original_ids:["topology.compactness"],
     aliases:["Compactness"],meanings:[{id:"m.compact",subject:"Topology",original_definition_id:"topology.compactness"}],
     formulations:[{key:"f.compact",meaning_id:"m.compact",subject:"Topology",label:"Topological compactness",
     body:"A compact topological space has finite subcovers.",source:"https://example.org/compact",dependencies:[]}]},
    {id:"term.continuous",term:"Continuous function (topological)",
     original_ids:["topology.continuity"],aliases:["Topological continuity"],
     meanings:[{id:"m.continuous",subject:"Topology",original_definition_id:"topology.continuity"}],
     formulations:[{key:"f.continuous",meaning_id:"m.continuous",subject:"Topology",label:"Topological continuity",
     body:"A continuous function.",source:"https://example.org/continuous",dependencies:[]}]},
  ]};
  const sandbox={
    window:{MathThmSearch:core,MathThmDefinitions:adapter},
    document:{getElementById:id=>els[id],querySelectorAll:()=>[]},
    fetch:async url=>({ok:true,json:async()=>url.includes("theorems.json")?records:snapshot}),
    console,encodeURIComponent,
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,"../web/app.js"),"utf8"),sandbox);
  await new Promise(resolve=>setImmediate(resolve));
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(els.total.textContent,"20 draft results");
  assert.match(els["definitions-status"].textContent,/v2 definitions loaded \(2 terms;/);
  els["hypothesis-query"].value="compactness";
  els["conclusion-query"].value="maximum";
  els["conclusion-query"].listeners.input();
  assert.match(els["results"].innerHTML,/Extreme value theorem/);
  assert.match(els["results"].innerHTML,/definition-link/);
  assert.match(els["results"].innerHTML,/Proof 1/);
  assert.match(els["result-count"].textContent,/result/);
});
