"use strict";
/* Runs on the actual generated Pages tree, not synthetic fixture definitions. */
const fs=require("node:fs");
const assert=require("node:assert/strict");
const path=require("node:path");
const {chromium}=require(process.env.MATHDEF_PLAYWRIGHT_PATH ||
  "/tmp/maththm-browser/node_modules/playwright-core");
const root=process.env.MATHTHM_SITE_ROOT || "_site";
const base=process.env.MATHTHM_SITE_URL || "http://127.0.0.1:8766/";
const snapshot=JSON.parse(fs.readFileSync(path.join(root,"mathdef-snapshot.json"),"utf8"));
assert.equal(snapshot.schema,"mathdef.definition-snapshot.v2");
const chromiumPath=["/usr/bin/google-chrome","/usr/bin/google-chrome-stable",
  "/usr/bin/chromium","/usr/bin/chromium-browser"].find(fs.existsSync);
assert(chromiumPath,"Chromium is required to verify real theorem definition expansion");
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:chromiumPath,
   args:["--no-sandbox","--disable-dev-shm-usage"]});
 try{
  const page=await browser.newPage({viewport:{width:1280,height:880}});
  const errors=[];
  page.on("pageerror",e=>errors.push(e.message));
  await page.goto(base,{waitUntil:"domcontentloaded"});
  await page.locator("#definitions-status").filter({hasText:"mathDef v2 definitions loaded ("+snapshot.definitions.length+" terms"}).waitFor();
  await page.locator("#hypothesis-query").fill("compactness");
  await page.locator("#conclusion-query").fill("maximum");
  await page.locator("#results .definition-link").first().waitFor();
  const oldId=await page.locator("#results .definition-link").first().getAttribute("data-def-id");
  assert(snapshot.definitions.some(x=>x.id===oldId),"Theorem link must resolve to a canonical v2 term ID");
  await page.locator("#results .definition-link").first().click();
  await page.locator(".definition-insert").first().waitFor();
  assert.match(await page.locator(".definition-insert").first().innerText(),/Definition:/);
  // The v2 formulation should be visible and alternatives should remain
  // discoverable when a term has multiple formulations.
  const html=await page.locator(".definition-insert").first().innerHTML();
  assert(!html.includes("not currently available"),"No broken historical v1 target");
  // Real deployed V2 snapshot: adjective and compound phrase must link to
  // DISTINCT meanings, without swallowing the shorter occurrence.
  await page.locator("#hypothesis-query").fill("compactness");
  await page.locator("#conclusion-query").fill("uniform continuity");
  const heine=page.locator(".theorem-card").filter({hasText:"Heine–Cantor theorem"});
  await heine.waitFor();
  const heineLinks=heine.locator(".statement .definition-link");
  const allTexts=await heineLinks.allTextContents();
  assert(allTexts.some(t=>t.trim().toLowerCase()==="continuous"),
    "ordinary continuous should link to mathDef V2");
  assert(allTexts.some(t=>t.trim().toLowerCase()==="uniformly continuous"),
    "uniformly continuous should link as a complete phrase");
  const continuous=heineLinks.filter({hasText:/^continuous$/i}).first();
  const uniform=heineLinks.filter({hasText:/^uniformly continuous$/i}).first();
  assert.notEqual(await continuous.getAttribute("data-def-id"),
                  await uniform.getAttribute("data-def-id"),
                  "continuity and uniform continuity must have distinct V2 targets");
  await page.setViewportSize({width:390,height:844});
  assert(await page.locator("#results .theorem-card").count()>0);
  assert.deepEqual(errors,[],"No JS errors in v2 definition expansion");
  console.log("MATHTHM_V2_BROWSER_SMOKE=PASSED "+
    JSON.stringify({terms:snapshot.definitions.length,canonical_clicked_id:oldId,
       errors:errors.length}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
