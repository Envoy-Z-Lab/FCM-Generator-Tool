# FCM Generator Tool

A simple tool to generate a `framework_compatibility_matrix.xml` from a list of FQNames, typically sourced from `check_vintf` during an AOSP build.

## Credits

Originally written by [@SebaUbuntu](https://github.com/SebaUbuntu)

## Usage Instructions

### 1. Download the Required Files
- `generate_fcm.py` – Python script for FCM generation
- `fqnames.txt` – Input file containing FQNames (one per line)

### 2. Build AOSP Without Stock FCM
- Compile AOSP **without including the stock firmware's FCM**
- Let the build proceed until it **fails at the `check_vintf` stage**

### 3. Extract FQNames
- From the `check_vintf` error log, **copy the FQName entries**
- Clean the lines by **removing logging prefixes**, leaving just the FQNames
- Paste the cleaned list into `fqnames.txt`

### 4. Run the Script
```bash
python3 generate_fcm.py > framework_compatibility_matrix.xml
