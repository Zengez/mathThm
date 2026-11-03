"use strict";
/* Self-contained visual editor for an explicit nested Boolean expression tree. */
(function (root, factory) {
  const api = factory(root);
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.MathThmQueryEditor = api;
})(typeof window !== "undefined" ? window : null, function (root) {
  let serial = 0;
  const term = (text = "") => ({kind:"term", id:"t"+(++serial), text});
  const group = (items = [term()]) => ({
    kind:"group", id:"g"+(++serial),
    clauses:items.map(expr=>({op:"AND", expr}))
  });
  const escape = value => String(value ?? "").replace(/[&<>"']/g,
    ch=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
  function findGroup(node, id) {
    if (node.id === id && node.kind === "group") return node;
    for (const item of node.clauses || []) {
      if (item.expr.kind === "group") {
        const found=findGroup(item.expr,id);
        if (found) return found;
      }
    }
    return null;
  }
  function findClause(parent, id) {
    for (let i=0;i<parent.clauses.length;i++) {
      const clause=parent.clauses[i];
      if (clause.expr.id===id) return {parent,index:i,clause};
      if (clause.expr.kind==="group") {
        const found=findClause(clause.expr,id);
        if (found) return found;
      }
    }
    return null;
  }
  function create(container, side, onChange = () => {}) {
    if (!container) throw Error("Boolean query builder container required");
    if (!["hypotheses","conclusions"].includes(side)) throw Error("Unknown query side");
    let tree=group();
    const documentRoot=container.ownerDocument || document;
    const logic=documentRoot.getElementById(side+"-logic");
    const inputId=side==="hypotheses"?"hypothesis-query":"conclusion-query";
    const placeholder=side==="hypotheses"?"e.g. compactness":"e.g. maximum";
    const title=side==="hypotheses"?"hypothesis":"conclusion";
    let usedPrimary=false;
    const action=(name,id,text,label)=>'<button type="button" class="query-action" data-action="'+name+
      '" data-id="'+escape(id)+'" aria-label="'+escape(label)+'">'+text+'</button>';
    function draw(node,isRoot=false) {
      let html='<div class="query-group'+(isRoot?' query-root':'')+'" data-group-id="'+escape(node.id)+'">';
      for (let i=0;i<node.clauses.length;i++) {
        const entry=node.clauses[i],sub=entry.expr;
        const connector=i===0?
          '<span class="query-connector-placeholder" aria-hidden="true"></span>':
          '<select class="query-connector" data-connector="true" data-group-id="'+escape(node.id)+
          '" data-index="'+i+'" aria-label="Join with previous clause">'+
          '<option value="AND"'+(entry.op==="AND"?' selected':'')+'>AND</option>'+
          '<option value="OR"'+(entry.op==="OR"?' selected':'')+'>OR</option></select>';
        let operand;
        if (sub.kind==="term") {
          const first=!usedPrimary;
          usedPrimary=true;
          operand='<input type="search" class="query-term" data-term-id="'+escape(sub.id)+
            '" id="'+(first?inputId:'query-'+escape(sub.id))+
            '" aria-label="'+escape(title)+' term '+(i+1)+
            '" placeholder="'+(first?placeholder:'Add a search phrase')+
            '" autocomplete="off" spellcheck="false" value="'+escape(sub.text)+'">';
        } else {
          operand='<div class="query-nested" role="group" aria-label="Nested '+escape(title)+' group">'+
            '<div class="query-group-label">Grouped clauses</div>'+draw(sub)+'</div>';
        }
        const controls=sub.kind==="term"?
          action("wrap",sub.id,"Group","Make a nested group containing this term"):
          (sub.clauses.length===1?action("ungroup",sub.id,"Ungroup","Remove these parentheses"):"");
        html+='<div class="query-row">'+connector+'<div class="query-operand">'+operand+'</div>'+
          '<div class="query-row-controls">'+controls+
          (isRoot && node.clauses.length===1?"":action("remove",sub.id,"×","Remove this clause"))+
          '</div></div>';
      }
      html+='<div class="query-add">'+action("add-term",node.id,"+ Term","Add a term to this group")+
        action("add-group",node.id,"+ Group","Add a nested group to this group")+'</div></div>';
      return html;
    }
    function preview() {
      if (logic) logic.textContent="Interpreted: "+(root?.MathThmSearch?.describeExpression(tree)||"No filters (all theorems)");
    }
    function render() {
      usedPrimary=false;
      container.innerHTML=draw(tree,true);
      preview();
    }
    function changed() {preview();onChange();}
    function focus(id) {container.querySelector?.('[data-term-id="'+id+'"]')?.focus();}
    container.addEventListener("input",event=>{
      const id=event.target?.dataset?.termId;
      if (!id) return;
      const found=findClause(tree,id);
      if (!found || found.clause.expr.kind!=="term") return;
      found.clause.expr.text=event.target.value;
      changed();
    });
    container.addEventListener("change",event=>{
      if (!event.target?.dataset?.connector) return;
      const parent=findGroup(tree,event.target.dataset.groupId);
      const index=Number(event.target.dataset.index);
      if (!parent || !Number.isInteger(index) || index<1 || index>=parent.clauses.length) return;
      parent.clauses[index].op=event.target.value==="OR"?"OR":"AND";
      changed();
    });
    container.addEventListener("click",event=>{
      const button=event.target?.closest?.("button[data-action]");
      if (!button || !container.contains(button)) return;
      const {action:command,id}=button.dataset;
      let focusTerm=null;
      if (command==="add-term" || command==="add-group") {
        const parent=findGroup(tree,id);
        if (!parent) return;
        const t=term();
        parent.clauses.push({op:"AND",expr:command==="add-term"?t:group([t])});
        focusTerm=t.id;
      } else {
        const hit=findClause(tree,id);
        if (!hit) return;
        if (command==="remove") {
          hit.parent.clauses.splice(hit.index,1);
          if (!tree.clauses.length) tree.clauses.push({op:"AND",expr:term()});
        } else if (command==="wrap" && hit.clause.expr.kind==="term") {
          hit.clause.expr=group([hit.clause.expr]);
        } else if (command==="ungroup" && hit.clause.expr.kind==="group" &&
                   hit.clause.expr.clauses.length===1) {
          hit.clause.expr=hit.clause.expr.clauses[0].expr;
        } else return;
      }
      render();changed();
      if (focusTerm) focus(focusTerm);
    });
    render();
    return {
      expression:()=>tree,
      clear:()=>{
        tree=group();render();changed();
      }
    };
  }
  return Object.freeze({create});
});
