"use strict";
const test=require("node:test"), assert=require("node:assert/strict");
const fs=require("node:fs"), path=require("node:path");
const core=require("../web/search-core.js");
const catalog=JSON.parse(fs.readFileSync(path.join(__dirname,"../data/theorems.json"),"utf8")).records;
test("empty queries select all once",()=>{
  const hits=core.search(catalog,"","");
  assert.equal(hits.length,20);
  assert.equal(new Set(hits.map(h=>h.theorem.id)).size,20);
});
test("hypothesis/conclusion AND is directional",()=>{
  const hits=core.search(catalog,"finite group","orbit");
  assert.ok(hits.some(h=>h.theorem.id==="thm.algebra.orbit-stabilizer"));
  assert.equal(core.search(catalog,"orbit","compactness").length,0);
});
test("tags and inflections retrieve records",()=>{
  assert.ok(core.search(catalog,"compactness","maximum").some(h=>h.theorem.id==="thm.analysis.extreme-value"));
  assert.ok(core.search(catalog,"complete","fixed point").some(h=>h.theorem.id==="thm.analysis.banach-fixed-point"));
  assert.deepEqual(core.tokens("ran running runs"),["run","run","run"]);
});
test("compound iff theorem is indexed in either direction but displayed once",()=>{
  const one=core.search(catalog,"closed","compactness");
  const reverse=core.search(catalog,"compactness","closed");
  assert.ok(one.some(h=>h.theorem.id==="thm.topology.heine-borel"));
  assert.ok(reverse.some(h=>h.theorem.id==="thm.topology.heine-borel"));
  assert.equal(reverse.filter(h=>h.theorem.id==="thm.topology.heine-borel").length,1);
});
test("display switches at 10 hits",()=>{
  assert.equal(core.modeFor("auto",10),"full");
  assert.equal(core.modeFor("auto",11),"compact");
  assert.equal(core.modeFor("full",20),"full");
  assert.equal(core.modeFor("compact",1),"compact");
});
test("conservative matching does not mistake words embedded in other words",()=>{
  assert.equal(core.containsPhrase(core.normalized("unbounded"),core.normalized("bounded")),false);
  assert.equal(core.containsPhrase(core.normalized("george's"),core.normalized("george")),true);
});
