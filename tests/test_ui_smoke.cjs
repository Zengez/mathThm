"use strict";
const test=require("node:test"), assert=require("node:assert/strict");
const fs=require("node:fs"), path=require("node:path"), vm=require("node:vm");
const core=require("../web/search-core.js");
const records=JSON.parse(fs.readFileSync(path.join(__dirname,"../data/theorems.json"),"utf8"));
function element(){
  return {value:"",textContent:"",innerHTML:"",hidden:true,listeners:{},addEventListener(type,fn){this.listeners[type]=fn;},
    focus(){},setAttribute(){}};
}
test("browser-like boot renders live theorem and mathDef-linked full statement",async()=>{
  const ids=["hypothesis-query","conclusion-query","results","total","result-count","results-summary",
    "definitions-status","error","clear-search"];
  const els=Object.fromEntries(ids.map(k=>[k,element()]));
  const snapshot={schema:"mathdef.definition-snapshot.v1",definitions:[
    {id:"topology.compactness",term:"Compact space",aliases:["Compactness"],body:"A compact topological space has finite subcovers.",source:"https://example.org/compact",dependencies:[]},
    {id:"topology.continuity",term:"Continuous function (topological)",aliases:["Topological continuity"],body:"A continuous function.",source:"https://example.org/continuous",dependencies:[]},
  ]};
  const sandbox={
    window:{MathThmSearch:core},
    document:{getElementById:id=>els[id],querySelectorAll:()=>[]},
    fetch:async url=>({ok:true,json:async()=>url.includes("theorems.json")?records:snapshot}),
    console,encodeURIComponent,
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,"../web/app.js"),"utf8"),sandbox);
  await new Promise(resolve=>setImmediate(resolve));
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(els.total.textContent,"20 draft results");
  assert.match(els["definitions-status"].textContent,/2;/);
  els["hypothesis-query"].value="compactness";
  els["conclusion-query"].value="maximum";
  els["conclusion-query"].listeners.input();
  assert.match(els["results"].innerHTML,/Extreme value theorem/);
  assert.match(els["results"].innerHTML,/definition-link/);
  assert.match(els["results"].innerHTML,/Proof 1/);
  assert.match(els["result-count"].textContent,/result/);
});
