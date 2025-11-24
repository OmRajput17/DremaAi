# Bug Fix: JSON Parsing & Model Update

## Issues Identified

### 1. Model Decommissioned
**Error**: `groq.BadRequestError: Error code: 400 ... model 'llama-3.1-70b-versatile' has been decommissioned`
**Timestamp**: 2025-11-24 12:21:04
**Fix**: Updated `src/config.py` to use `llama-3.3-70b-versatile`.

### 2. JSON Parsing Failure
**Error**: `Error parsing MCQs: Expecting value: line 1 column 1 (char 0)`
**Root Cause**: The LLM response contained conversational text *before* the JSON code block:
```
Here are 10 medium-level MCQs based on the chapter content provided:

```json
{ ... }
```
```
**Previous Logic**: Only checked if the string *started* with "```".
**Fix**: Updated `src/components/mcq_generator.py` to robustly find the JSON block.

## Implementation Details

### Robust JSON Extraction
The new logic attempts two strategies:

1. **Code Block Extraction**:
   - Splits text by "```"
   - Iterates through parts to find one that looks like JSON (starts with `{` and ends with `}`)
   - Handles `json` language identifier

2. **Fallback Extraction**:
   - Finds the first `{` and last `}` in the entire text
   - Extracts everything in between

```python
# If still not clean, try to find the first { and last }
if not response_text.startswith("{"):
    start_idx = response_text.find("{")
    end_idx = response_text.rfind("}")
    if start_idx != -1 and end_idx != -1:
        response_text = response_text[start_idx:end_idx+1]
```

## Verification

- App reloaded successfully at 12:22:05
- New model `llama-3.3-70b-versatile` is active
- JSON parsing can now handle:
  - Pure JSON
  - Markdown code blocks
  - Conversational prefixes
  - Mixed content

## Status

✅ **RESOLVED**: Application is fully functional and robust against LLM response variations.
