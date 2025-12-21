BASE_INSTRUCTION = """
You are a helpful AI assistant
"""

STRUCTURED_OUTPUT_INSTRUCTION = """
CRITICAL: You must respond with ONLY valid JSON that strictly conforms to the provided Pydantic schema.

Output Requirements:
1. Your entire response must be a single valid JSON object
2. Do NOT include any text before or after the JSON
3. Do NOT wrap the JSON in markdown code blocks or backticks
4. Do NOT add explanations, comments, or additional fields
5. All field names must exactly match the schema (case-sensitive)
6. All field types must match the schema requirements
7. Required fields must always be present
8. Optional fields can be omitted or set to null if not applicable

Schema Adherence:
- String fields: Use proper string values, not null unless Optional
- Integer/Float fields: Use numeric values only
- Boolean fields: Use true or false (lowercase)
- Array fields: Use [] for empty arrays, never null
- Enum fields: Use only the exact values defined in the enum
- Nested objects: Follow the nested schema structure precisely

Example Format:
{
  "field1": "value1",
  "field2": 123,
  "field3": true,
  "field4": ["item1", "item2"],
  "nested_object": {
    "sub_field1": "value"
  }
}

If you cannot determine a value for a required field, use a sensible default or make your best inference based on context.

Schema:
<PYDANTIC_SCHEMA>
"""

RECOVER_OUTPUT_INSTRUCTION = """
ALERT: Your previous response did NOT conform to the required Pydantic schema or could not get parsed as it a python dictionary.

Schema Validation Failed Due:
<EXCEPTION>

You must now:

1. ACKNOWLEDGE THE ERROR
   - Your previous output was invalid JSON, incomplete, or did not match the schema
   - One or more fields were missing, incorrectly typed, or improperly formatted

2. IDENTIFY THE ISSUES
   Common problems in your previous response may include:
   - Missing required fields
   - Incorrect data types (e.g., string instead of integer)
   - Invalid enum values
   - Improperly nested objects
   - Extra fields not in the schema
   - Markdown formatting (```json blocks) when raw JSON was required
   - Text before or after the JSON object

3. REGENERATE CORRECTLY
   - Review the original schema requirements carefully
   - Ensure EVERY required field is present
   - Verify ALL field types match exactly
   - Double-check nested object structures
   - Remove any non-JSON content
   - Output ONLY the valid JSON object

4. SELF-VALIDATE BEFORE RESPONDING
   Before submitting, verify:
   ✓ Is this pure JSON with no markdown or extra text?
   ✓ Are all required fields present?
   ✓ Do all field types match the schema?
   ✓ Are all field names spelled correctly?
   ✓ Is the JSON properly formatted and parseable?

Schema:
<PYDANTIC_SCHEMA>

NOW REGENERATE YOUR RESPONSE WITH ONLY THE VALID JSON OUTPUT.
Do not explain what was wrong. Do not apologize. Just provide the corrected JSON.
"""