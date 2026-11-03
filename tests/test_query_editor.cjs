"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const core=require("../web/search-core.js");
function setup(){
  const listeners={},logic={textContent:""},focuses=[];
  const doc={getElementById:()=>logic};
  const container={
    ownerDocument:doc,innerHTML:"",
    addEventListener:(type,fn)=>{listeners[type]=fn;},
    contains:()=>true,
    querySelector:selector=>({focus:()=>focuses.push(selector)}),
  };
  const context={window:{MathThmSearch:core},module:{exports:{}},document:doc,console};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,"../web/query-editor.js"),"utf8"),context);
  let changes=0;
  const editor=context.module.exports.create(container,"hypotheses",()=>changes++);
  function value(id,text){listeners.input({target:{dataset:{termId:id},value:text}});}
  function click(action,id){
    listeners.click({target:{closest:()=>({dataset:{action,id}})}});
  }
  function connector(groupId,index,op){
    listeners.change({target:{dataset:{connector:"true",groupId,index:String(index)},value:op}});
  }
  return {editor,container,logic,focuses,value,click,connector,get changes(){return changes;}};
}
test("the first field is a one-term editor with no connector",()=>{
  const a=setup(),tree=a.editor.expression();
  assert.equal(tree.clauses.length,1);
  assert.match(a.container.innerHTML,/id="hypothesis-query"/);
  assert.doesNotMatch(a.container.innerHTML,/data-connector="true"/);
});
test("adding rows, joining with OR, and grouping update the actual search tree",()=>{
  const a=setup(),tree=a.editor.expression();
  const first=tree.clauses[0].expr;
  a.value(first.id,"compact");
  a.click("add-term",tree.id);
  const second=tree.clauses[1].expr;
  a.value(second.id,"bounded");
  a.connector(tree.id,1,"OR");
  assert.equal(core.describeExpression(tree),"(compact OR bounded)");
  assert.match(a.container.innerHTML,/option value="OR"/);
  a.click("wrap",first.id);
  const nested=tree.clauses[0].expr;
  assert.equal(nested.kind,"group");
  a.click("add-term",nested.id);
  const third=nested.clauses[1].expr;
  a.value(third.id,"complete");
  assert.equal(core.describeExpression(tree),"((compact AND complete) OR bounded)");
  assert.match(a.logic.textContent,/complete/);
  assert.ok(a.changes>=6);
  assert.ok(a.focuses.length);
});
test("removing, ungrouping, and clear do not leave stale conditions",()=>{
  const a=setup(),tree=a.editor.expression();
  const first=tree.clauses[0].expr;
  a.value(first.id,"compact");
  a.click("wrap",first.id);
  const nested=tree.clauses[0].expr;
  a.click("ungroup",nested.id);
  assert.equal(tree.clauses[0].expr.id,first.id);
  a.click("add-term",tree.id);
  const second=tree.clauses[1].expr;
  a.value(second.id,"bounded");
  a.click("remove",first.id);
  assert.equal(core.describeExpression(tree),"bounded");
  assert.match(a.container.innerHTML,/id="hypothesis-query"/);
  const before=a.changes;
  a.editor.clear(false);
  assert.equal(a.changes,before);
  assert.equal(core.hasTerms(a.editor.expression()),false);
  assert.match(a.logic.textContent,/No filters/);
});
