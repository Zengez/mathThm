"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const core=require("../web/search-core.js");
const editorSandbox={module:{exports:{}},window:{MathThmSearch:core}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,"../web/query-editor.js"),"utf8"),editorSandbox);
const editor=editorSandbox.module.exports;
const records=[
  {id:"compact",title:"Compact maximum",area:"Analysis",statement:"Compact implies maximum.",
   hypotheses:["compact"],conclusions:["maximum"],source_url:"https://example.org/1",proofs:[]},
  {id:"closed",title:"Closed maximum",area:"Analysis",statement:"Closed implies maximum.",
   hypotheses:["closed"],conclusions:["maximum"],source_url:"https://example.org/2",proofs:[]},
  {id:"complete",title:"Complete fixed point",area:"Analysis",statement:"Complete implies fixed point.",
   hypotheses:["complete"],conclusions:["fixed point"],source_url:"https://example.org/3",proofs:[]},
];
function element(){
  return {value:"",innerHTML:"",textContent:"",hidden:true,listeners:{},
    addEventListener(type,callback){this.listeners[type]=callback;},
    setAttribute(){},focus(){},contains(){return true;},querySelector(){return {focus(){}};}};
}
test("full app uses grouped hypothesis and conclusion builders, including reset",async()=>{
  const ids=["hypothesis-query","conclusion-query","hypothesis-builder","conclusion-builder",
    "hypotheses-logic","conclusions-logic","results","total","result-count","results-summary",
    "definitions-status","error","clear-search"];
  const els=Object.fromEntries(ids.map(id=>[id,element()]));
  const document={getElementById:id=>els[id],querySelectorAll:()=>[]};
  els["hypothesis-builder"].ownerDocument=document;
  els["conclusion-builder"].ownerDocument=document;
  let fetchCount=0;
  const sandbox={
    window:{MathThmSearch:core,MathThmQueryEditor:editor},
    document,console,encodeURIComponent,
    fetch:async url=>{
      fetchCount++;
      if(url.includes("theorems.json"))return {ok:true,json:async()=>({schema:"maththm.theorems.v1",records})};
      return {ok:false,status:404};
    }
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,"../web/app.js"),"utf8"),sandbox);
  await new Promise(resolve=>setImmediate(resolve));
  await new Promise(resolve=>setImmediate(resolve));
  assert.match(els["result-count"].textContent,/3 results/);
  const h=els["hypothesis-builder"],c=els["conclusion-builder"];
  const original=h.innerHTML.match(/data-term-id="(t\d+)"/)[1];
  h.listeners.input({target:{dataset:{termId:original},value:"compact"}});
  assert.match(els["result-count"].textContent,/1 result/);
  assert.match(els["hypotheses-logic"].textContent,/compact/);
  const matchGroup=h.innerHTML.match(/data-group-id="(g\d+)"/);
  assert.ok(matchGroup);
  h.listeners.click({target:{closest:()=>({dataset:{action:"add-term",id:matchGroup[1]}})}});
  const termIds=Array.from(h.innerHTML.matchAll(/data-term-id="(t\d+)"/g),m=>m[1]);
  h.listeners.input({target:{dataset:{termId:termIds[1]},value:"closed"}});
  h.listeners.change({target:{dataset:{connector:"true",groupId:matchGroup[1],index:"1"},value:"OR"}});
  assert.match(els["result-count"].textContent,/2 results/);
  assert.match(els["hypotheses-logic"].textContent,/compact OR closed/);
  const resultTerm=c.innerHTML.match(/data-term-id="(t\d+)"/)[1];
  c.listeners.input({target:{dataset:{termId:resultTerm},value:"fixed point"}});
  assert.match(els["result-count"].textContent,/0 results/);
  els["clear-search"].listeners.click();
  assert.match(els["result-count"].textContent,/3 results/);
  assert.match(els["hypotheses-logic"].textContent,/No filters/);
  assert.ok(fetchCount>=1);
});
