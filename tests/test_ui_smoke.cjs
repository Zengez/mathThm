"use strict";
const test=require("node:test"), assert=require("node:assert/strict");
const fs=require("node:fs"), path=require("node:path"), vm=require("node:vm");
const core=require("../web/search-core.js");
const adapter=require("../web/mathdef-v2.js");
const linker=require("../web/definition-links.js");
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
    window:{MathThmSearch:core,MathThmDefinitions:adapter,MathThmLinks:linker},
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


test("expanded v2 definitions hide self and ancestors; other branches stay available",async()=>{
  const ids=["hypothesis-query","conclusion-query","results","total","result-count",
    "results-summary","definitions-status","error","clear-search"];
  const els=Object.fromEntries(ids.map(k=>[k,element()]));
  const group=(id,term,aliases,body,deps=[])=>({
    id,term,aliases,original_ids:[],
    meanings:[{id:"meaning."+id,subject:"Topology"}],
    formulations:[{key:"form."+id,meaning_id:"meaning."+id,
      subject:"Topology",body,source:"https://example.org/source",dependencies:deps}],
  });
  const snapshot={
    schema:"mathdef.definition-snapshot.v2",
    consolidated_ids:{group_aliases:{},meaning_aliases:{},formulation_aliases:{}},
    definitions:[
      group("g.subspace","Subspace topology",[],
        "The subspace topology uses a topology from the ambient space. The subspace topology is inherited.",
        [{id:"g.subspace"},{id:"g.topology"},{id:"g.topology"}]),
      group("g.topology","Topology",[],
        "A topology induces the subspace topology on subsets.",
        [{id:"g.subspace"},{id:"g.compact"}]),
      group("g.compact","Compact space",[],
        "A compact space can have a subspace topology."),
    ],
  };
  const makeNode=()=>({
    dataset:{},children:[],innerHTML:"",nextElementSibling:null,
    append(v){this.children.push(v);},
    after(v){this.nextElementSibling=v;},
    setAttribute(){}
  });
  const sandbox={
    window:{MathThmSearch:core,MathThmDefinitions:adapter,MathThmLinks:linker},
    document:{getElementById:id=>els[id],querySelectorAll:()=>[],
      createElement:()=>makeNode()},
    fetch:async url=>({ok:true,json:async()=>url.includes("theorems.json")?records:snapshot}),
    console,encodeURIComponent,
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,"../web/app.js"),"utf8"),sandbox);
  await new Promise(resolve=>setImmediate(resolve));
  await new Promise(resolve=>setImmediate(resolve));
  assert.match(els["definitions-status"].textContent,/3 terms/);
  function open(id,path=[]){
    const host=makeNode();
    const button={dataset:{defId:id,defPath:JSON.stringify(path),sourceSubject:"Topology"},
      setAttribute(){},
      closest(selector){
        if(selector==="[data-def-id]")return button;
        if(selector==="p")return host;
        return null;
      }
    };
    els.results.listeners.click({target:button});
    return host.nextElementSibling;
  }
  const subspace=open("g.subspace");
  assert.ok(subspace,"initial definition should open");
  assert.match(subspace.innerHTML,/The subspace topology is inherited/);
  assert.doesNotMatch(subspace.innerHTML,/data-def-id="g.subspace"/,
    "the open definition cannot link to its own heading");
  assert.match(subspace.innerHTML,/data-def-id="g.topology"/,
    "the distinct concept topology should still be linkable");
  assert.ok(subspace.children.length);
  assert.deepEqual(Array.from(subspace.children[0].children, b=>b.dataset.defId),["g.topology"],
    "dependency controls must also drop self and repeated IDs");
  const topology=open("g.topology",["g.subspace"]);
  assert.ok(topology);
  assert.doesNotMatch(topology.innerHTML,/data-def-id="g.subspace"/,
    "an ancestor must not reappear inside the nested definition text");
  assert.deepEqual(Array.from(topology.children[0].children,b=>b.dataset.defId),["g.compact"]);
  assert.equal(open("g.subspace",["g.subspace","g.topology"]),null,
    "direct attempts to reopen an ancestor must also be rejected");
  const otherBranch=open("g.compact");
  assert.match(otherBranch.innerHTML,/data-def-id="g.subspace"/,
    "a separate branch should remain able to use the same definition");
});
