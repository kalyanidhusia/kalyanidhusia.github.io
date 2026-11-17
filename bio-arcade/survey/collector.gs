/**
 * Bio-Arcade Learning Survey — collector (Google Apps Script, bound to the Sheet)
 *
 * Setup (once):
 *   1. Open the Google Sheet "Bio-Arcade Learning Survey — responses".
 *   2. Extensions → Apps Script. Delete any code there, paste this whole file, save.
 *   3. Deploy → New deployment → type "Web app".
 *        Execute as: Me          Who has access: Anyone
 *   4. Copy the Web app URL (ends in /exec) into COLLECT_URL in survey/index.html,
 *      and into the GitHub repository secret SURVEY_COLLECT_URL.
 *   Re-deploy (Deploy → Manage deployments → edit → New version) after any edit here.
 *
 * What it does:
 *   POST  (from the survey)      → appends one row to sheet "responses"; the full record is kept in column raw_json.
 *   GET ?format=csv              → the whole sheet as CSV (used by the GitHub Action to refresh survey/responses.csv).
 *   GET ?format=json             → all records as a JSON array (used by the facilitator dashboard "Load all responses").
 *   GET                          → a short status line.
 *
 * Privacy: the survey sends no names, emails or IDs. This script stores exactly what it receives plus a server timestamp.
 * It does not record IP addresses (Apps Script does not expose them).
 */
var SHEET = "responses";
var FIXED = ["server_ts","response_id","client_ts","instrument_version","role","collection","device","consent","synthetic"];
var ITEMS = [
  // student
  "S1","S2","S3","S4",
  "transcription_conf","transcription_diff","translation_conf","translation_diff","folding_conf","folding_diff",
  "immunology_conf","immunology_diff","pharmaco_conf","pharmaco_diff","antibiotics_conf","antibiotics_diff",
  "S13","S14","S15","S16","S17","S18","S19","S20","S21","S22","S23","S24","S25","S26","S27","S28","S29","S30","S31",
  // faculty
  "F1","F2","F3","F4",
  "transcription_teach","translation_teach","folding_teach","immunology_teach","pharmaco_teach","antibiotics_teach",
  "F6","F7","F8","F9","F10","F14","F11"
];
var HEADER = FIXED.concat(ITEMS, ["raw_json"]);

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET) || ss.insertSheet(SHEET);
  if (sh.getLastRow() === 0) { sh.appendRow(HEADER); sh.setFrozenRows(1); }
  return sh;
}
function cellValue_(v) {
  if (v === undefined || v === null) return "";
  if (Array.isArray(v)) return v.join("; ");
  return v;
}
function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var r = JSON.parse(e.postData.contents);
    if (!r || !r.id || !r.answers || r.consent !== "yes") return text_("rejected");
    if (r.synthetic === true) return text_("synthetic records are not stored");
    var sh = sheet_();
    // de-duplicate on response_id (retries from the survey's offline queue)
    var ids = sh.getLastRow() > 1 ? sh.getRange(2, 2, sh.getLastRow() - 1, 1).getValues().map(function(x){ return String(x[0]); }) : [];
    if (ids.indexOf(String(r.id)) >= 0) return text_("duplicate");
    var row = [new Date().toISOString(), r.id, r.ts || "", r.instrument_version || "", r.role || "", r.collection || "", r.ua || "", r.consent || "", "false"];
    ITEMS.forEach(function(k){ row.push(cellValue_(r.answers[k])); });
    row.push(JSON.stringify(r));
    sh.appendRow(row);
    return text_("ok");
  } catch (err) {
    return text_("error: " + err);
  } finally {
    lock.releaseLock();
  }
}
function doGet(e) {
  var fmt = (e && e.parameter && e.parameter.format) || "";
  var sh = sheet_();
  var n = Math.max(sh.getLastRow() - 1, 0);
  if (fmt === "csv") {
    var vals = sh.getDataRange().getValues();
    var csv = vals.map(function(row){ return row.map(function(c){ c = String(c); return /[",\n]/.test(c) ? '"' + c.replace(/"/g, '""') + '"' : c; }).join(","); }).join("\n");
    return ContentService.createTextOutput(csv).setMimeType(ContentService.MimeType.CSV);
  }
  if (fmt === "json") {
    var out = [];
    if (n > 0) {
      var col = HEADER.indexOf("raw_json") + 1;
      sh.getRange(2, col, n, 1).getValues().forEach(function(x){ try { out.push(JSON.parse(x[0])); } catch (err) {} });
    }
    return ContentService.createTextOutput(JSON.stringify(out)).setMimeType(ContentService.MimeType.JSON);
  }
  return text_("Bio-Arcade survey collector: " + n + " responses stored.");
}
function text_(s) { return ContentService.createTextOutput(s).setMimeType(ContentService.MimeType.TEXT); }
