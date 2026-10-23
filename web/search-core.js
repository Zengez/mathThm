"use strict";
/* Shared browser/Node search core; queries are retrieval aids, not formal inference. */
(function (root, factory) {
  const api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.MathThmSearch = api;
})(typeof window !== "undefined" ? window : null, function () {
  const aliases = {
    compactness:"compact",compact:"compact",compacts:"compact",
    continuity:"continu",continuous:"continu",continuously:"continu",
    completeness:"complete",completed:"complete",complete:"complete",
    closedness:"closed",closed:"closed",boundedness:"bounded",bounds:"bound",
    convergence:"converge",converges:"converge",convergent:"converge",converging:"converge",
    differentiability:"differentiable",differentiation:"differentiable",differentiable:"differentiable",
    uniqueness:"unique",uniquely:"unique",unique:"unique",
    orbits:"orbit",orbit:"orbit",stabilizers:"stabilizer",stabiliser:"stabilizer",
    probabilities:"probability",probability:"probability",primes:"prime",
    sets:"set",subsets:"subset",subsequences:"subsequence",
    runs:"run",ran:"run",running:"run",run:"run",
  };
  const tokens = (text) => String(text || "").normalize("NFKC").toLowerCase()
    .replace(/\\[a-zA-Z]+/g, " ").replace(/['’]s\b/g, "")
    .match(/[\p{L}\p{N}]+/gu)?.map(t => aliases[t] || t) || [];
  const normalized = (text) => tokens(text).join(" ");
  const containsPhrase = (haystack, needle) =>
    !needle || (" " + haystack + " ").includes(" " + needle + " ");
  function fields(t, side) {
    const primary = side === "hypotheses" ? (t.hypotheses || []) : (t.conclusions || []);
    const tags = side === "hypotheses" ? (t.hypothesis_tags || []) : (t.conclusion_tags || []);
    const extra = [];
    if (Array.isArray(t.equivalence_sides)) {
      // For an iff theorem both sides can be used in either search field.
      for (const group of t.equivalence_sides) extra.push(...group);
    }
    return {primary, tags, extra};
  }
  function matchSide(t, side, query) {
    const q = normalized(query);
    if (!q) return {matched:true,why:"blank"};
    const groups = fields(t,side);
    for (const text of groups.primary) if (containsPhrase(normalized(text),q)) return {matched:true,why:"text"};
    for (const text of groups.tags) if (containsPhrase(normalized(text),q)) return {matched:true,why:"tag",tag:text};
    for (const text of groups.extra) if (containsPhrase(normalized(text),q)) return {matched:true,why:"equivalence"};
    return {matched:false,why:"none"};
  }
  function search(records, hypothesis, conclusion) {
    return records.map(t => ({
      theorem:t,
      hypothesisHit:matchSide(t,"hypotheses",hypothesis),
      conclusionHit:matchSide(t,"conclusions",conclusion),
    })).filter(hit => hit.hypothesisHit.matched && hit.conclusionHit.matched);
  }
  function modeFor(requested, count, expanded = false) {
    return expanded ? "full" : requested === "auto" ? (count <= 10 ? "full" : "compact") : requested;
  }
  return Object.freeze({tokens,normalized,containsPhrase,matchSide,search,modeFor});
});
