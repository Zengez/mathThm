"use strict";
const test=require("node:test"), assert=require("node:assert/strict");
const core=require("../web/search-core.js");
const T=(text)=>({kind:"term",text});
const G=(...rows)=>({kind:"group",clauses:rows.map(([op,expr])=>({op,expr}))});
const records=[
  {id:"a",hypotheses:["compact complete"],conclusions:["fixed point"]},
  {id:"b",hypotheses:["closed bounded real"],conclusions:["maximum"]},
  {id:"c",hypotheses:["compact"],conclusions:["maximum"]},
  {id:"d",hypotheses:["complete"],conclusions:["maximum"],hypothesis_tags:["bounded"]},
  {id:"e",hypotheses:["compact complete"],conclusions:["minimum"]},
];
const ids=(h,c="")=>core.search(records,h,c).map(r=>r.theorem.id);
test("legacy single-field search remains directional and conjunction across columns",()=>{
  assert.deepEqual(ids("compact","maximum"),["c"]);
  assert.deepEqual(ids("",""),["a","b","c","d","e"]);
  assert.deepEqual(ids("maximum","compact"),[]);
});
test("explicit grouped conjunctions and disjunctions",()=>{
  const query=G(["AND",G(["AND",T("compact")],["AND",T("complete")])],
    ["OR",G(["AND",T("closed")],["AND",T("bounded")],["AND",T("real")])]);
  assert.deepEqual(ids(query),["a","b","e"]);
  assert.equal(core.describeExpression(query),
    "((compact AND complete) OR ((closed AND bounded) AND real))");
  assert.deepEqual(ids(query,T("maximum")),["b"]);
});
test("nested OR under a broad AND constraint",()=>{
  const query=G(["AND",T("complete")],
    ["AND",G(["AND",T("compact")],["OR",T("bounded")])]);
  assert.deepEqual(ids(query),["a","d","e"]);
});
test("mixed operators are explicitly left-associated rather than using implicit SQL precedence",()=>{
  const query=G(["AND",T("compact")],["OR",T("closed")],["AND",T("bounded")]);
  assert.deepEqual(ids(query),["b"]);
  assert.equal(core.describeExpression(query),"((compact OR closed) AND bounded)");
});
test("blank rows, blank subgroups, and punctuation-only clauses impose no conditions",()=>{
  const query=G(["AND",T("")],["OR",T("!!")],
    ["AND",G(["AND",T("compact")],["OR",T("")])]);
  assert.deepEqual(ids(query),["a","c","e"]);
  assert.deepEqual(ids(G(["AND",T(" ")],["OR",G(["AND",T("")])])),["a","b","c","d","e"]);
});
test("tags remain searchable within Boolean groups",()=>{
  const query=G(["AND",T("complete")],["AND",T("bounded")]);
  assert.deepEqual(ids(query),["d"]);
  const hit=core.search(records,query,"")[0].hypothesisHit;
  assert.equal(hit.matched,true);
  assert.equal(hit.why,"tag");
});
test("equivalence sides still search each direction and return one theorem",()=>{
  const one={id:"iff",hypotheses:[],conclusions:[],
    equivalence_sides:[["compact"],["closed"]]};
  const query=G(["AND",T("compact")],["OR",T("closed")]);
  assert.deepEqual(core.search([one],query,T("closed")).map(h=>h.theorem.id),["iff"]);
});
