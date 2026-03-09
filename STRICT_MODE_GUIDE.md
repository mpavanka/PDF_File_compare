# STRICT Mode - Case-Insensitive Matching Only

## 🎯 What STRICT Mode Does

### **Only ignores CASE differences** (keeps everything else intact)

| File in Folder 1 | File in Folder 2 | Match? |
|------------------|------------------|--------|
| `Client Report.pdf` | `client report.pdf` | ✅ YES (case different) |
| `Annual Review.pdf` | `annual review.pdf` | ✅ YES (case different) |
| `File Name.pdf` | `file name.pdf` | ✅ YES (case different) |
| `My Document.pdf` | `my document.pdf` | ✅ YES (case different) |
| `TEST.pdf` | `test.pdf` | ✅ YES (case different) |

### **Does NOT match (different structure):**

| File in Folder 1 | File in Folder 2 | Match? |
|------------------|------------------|--------|
| `Client Report.pdf` | `Client_Report.pdf` | ❌ NO (space vs underscore) |
| `File Name.pdf` | `FileName.pdf` | ❌ NO (has space vs no space) |
| `Annual-Review.pdf` | `Annual Review.pdf` | ❌ NO (hyphen vs space) |
| `Report Q1.pdf` | `Report Q2.pdf` | ❌ NO (different content) |

---

## 🆚 Mode Comparison

### **For files with CASE differences: 5000 vs 91 files**

| Mode | What it ignores | Your Case |
|------|-----------------|-----------|
| **exact** | Nothing (100% identical) | ✅ If names match exactly |
| **strict** | Case only (A=a, B=b) | ✅ **If only case differs** |
| **smart** | Case + spaces + underscores + 95% fuzzy | ⚠️ May normalize too much |

---

## 📊 Examples

### **STRICT Mode Matches:**
```
✅ "Annual Report.pdf" = "annual report.pdf"
✅ "CLIENT.pdf" = "client.pdf"
✅ "File Name.pdf" = "file name.pdf"
✅ "Q1 Summary.pdf" = "q1 summary.pdf"
```

### **STRICT Mode Does NOT Match:**
```
❌ "Annual Report.pdf" ≠ "Annual_Report.pdf"  (space vs underscore)
❌ "File Name.pdf" ≠ "FileName.pdf"  (has space vs no space)
❌ "Client-Report.pdf" ≠ "Client Report.pdf"  (hyphen vs space)
```

---

## 🚀 Usage

### **If your files only differ by CASE:**

```bash
# Step 1: Verify
python verify_matches.py expected actual strict

# Step 2: Compare
python pdf_compare.py expected actual strict summary.html
```

### **If your files have spaces/underscores differences:**

```bash
# Use SMART mode instead (normalizes spaces/underscores)
python verify_matches.py expected actual smart
python pdf_compare.py expected actual smart summary.html
```

---

## 📋 Quick Decision Guide

### **Use STRICT mode if:**
- ✅ Files have same name but different CASE
- ✅ Example: `Report.pdf` vs `report.pdf`
- ✅ Example: `CLIENT.pdf` vs `client.pdf`

### **Use EXACT mode if:**
- ✅ Files must match 100% (byte-for-byte)
- ✅ Example: `Report.pdf` vs `Report.pdf` only

### **Use SMART mode if:**
- ✅ Files have spaces vs underscores
- ✅ Example: `Annual Report.pdf` vs `Annual_Report.pdf`
- ✅ Example: `File Name.pdf` vs `FileName.pdf`

---

## 📊 Output Example

### **STRICT Mode:**
```
📁 Folder 1: 5000 files
📁 Folder 2: 91 files

🔍 Strict matching (case-insensitive only)...

  ✅ EXACT: Client_ABC_Report.pdf
  
  🔄 CASE-INSENSITIVE: Annual Report.pdf
                    ↔ annual report.pdf
  
  🔄 CASE-INSENSITIVE: MONTHLY SUMMARY.pdf
                    ↔ monthly summary.pdf
  
  ❌ NO MATCH: File_Name.pdf
  (No match in folder 2)
```

---

## 🔧 How Normalization Works

### **Normalization removes:**
- Spaces: ` `
- Underscores: `_`
- Hyphens: `-`
- Case differences: `A` = `a`

### **Examples:**

```
Original:         → Normalized:
"Client Report"   → "clientreport"
"Client_Report"   → "clientreport"
"client-report"   → "clientreport"
"CLIENTREPORT"    → "clientreport"

All match! ✅
```

---

## 📋 Quick Comparison

### **Your Files:**
```
Expected folder (5000 files):
  - Annual Review 2024.pdf
  - Client ABC Report.pdf
  - Monthly Summary.pdf

Actual folder (91 files):
  - Annual_Review_2024.pdf
  - Client_ABC_Report.pdf
  - monthly-summary.pdf
```

### **Using EXACT mode:**
```
❌ NO MATCH: Annual Review 2024.pdf
✅ EXACT: Client ABC Report.pdf
❌ NO MATCH: Monthly Summary.pdf

Result: Only 1 match (too strict!)
```

### **Using STRICT mode:**
```
🔄 NORMALIZED: Annual Review 2024.pdf ↔ Annual_Review_2024.pdf
✅ EXACT: Client ABC Report.pdf
🔄 NORMALIZED: Monthly Summary.pdf ↔ monthly-summary.pdf

Result: All 3 matched! ✅
```

### **Using SMART mode (95%):**
```
✅ EXACT: Annual Review 2024.pdf ↔ Annual_Review_2024.pdf
✅ EXACT: Client ABC Report.pdf
⚠️  FUZZY: Monthly Summary.pdf ↔ Monthly Overview.pdf  ← WRONG!

Result: 2 correct + 1 wrong match
```

---

## 💡 When to Use Each Mode

### **Use STRICT mode when:**
- ✅ Files have spaces vs underscores
- ✅ Files have different cases (File.pdf vs file.pdf)
- ✅ Files have hyphens vs underscores
- ✅ You want normalized exact matching

### **Use EXACT mode when:**
- ✅ Files must have 100% identical names (byte-for-byte)
- ✅ You don't want any normalization
- ✅ Files already have perfectly matching names

### **Use SMART mode when:**
- ✅ Files have typos or similar names
- ⚠️ Be careful - verify fuzzy matches!
- ⚠️ Only use if strict doesn't find enough matches

---

## 🎯 Commands for Your Case (5000 vs 91)

### **Option 1: STRICT (Recommended)**
```bash
# Handles spaces, case, underscores automatically
python verify_matches.py expected actual strict
python pdf_compare.py expected actual strict summary.html
```

### **Option 2: EXACT (If names are identical)**
```bash
# Requires 100% identical file names
python verify_matches.py expected actual exact
python pdf_compare.py expected actual exact summary.html
```

### **Option 3: SMART (If other modes fail)**
```bash
# 95%+ similarity - CHECK FUZZY MATCHES!
python verify_matches.py expected actual smart
python pdf_compare.py expected actual smart summary.html
```

---

## 📊 Expected Results

### **Your 5000 vs 91 scenario with STRICT mode:**

```
Total files in expected: 5000
Total files in actual:   91

Matches found: 91 ✅
  - Exact matches:      ~40-50
  - Normalized matches: ~40-50
  - No wrong matches!

Unmatched in expected: 4909
  (These don't exist in actual folder - that's OK!)
```

---

## ✅ Summary

**For files with spaces and minimal name changes:**

```bash
# Use STRICT mode
python pdf_compare.py expected actual strict summary.html
```

**Benefits:**
- ✅ Handles spaces, underscores, hyphens
- ✅ Case-insensitive
- ✅ No wrong matches (100% normalized)
- ✅ Perfect for your 5000 vs 91 files

**Problem solved!** 🎉
