# Module 16: Output

**Project: Simple RAG System**  
**Team Leader**  
**Prepared by:** Mokshith H S  
**USN:** 4BB23AIO20  
**Department:** Artificial intelligence and Machine Learning

**Module responsibility:** define what the user receives, how sources are shown and how failure or insufficient evidence is explained. A raw language-model string is not the final product contract.

## Output states and behavior

| State | What the user sees | Required behavior |
| - | - | - |
| answered | Direct answer and numbered source references | Every substantive claim should be supported |
| insufficient\_evidence | A clear statement of missing evidence | Do not invent a completion or show false certainty |
| clarification\_needed | A short question identifying ambiguity | Ask only for information needed to answer |
| operational error | Plain-language failure and retry guidance | Preserve diagnostic request ID, hide internals |


Use answered only after the configured validation policy passes. A question about multiple topics may receive a bounded partial answer with a warning stating which requested facts were not found. Avoid a “confidence 93%” badge unless the team has implemented and validated a calibration method. Retrieval similarity is not answer confidence.

## Response schema

Use an explicit response model for the success and domain-outcome envelope. Error responses use the separate error envelope defined below. FastAPI's response model validates structure and filters fields; application logic still owns the meaning and support of the answer. [FastAPI response models](https://fastapi.tiangolo.com/tutorial/response-model/).

| Field | Type | Contract |
| - | - | - |
| schema\_version | string | Version of this API contract |
| request\_id | string | Diagnostic correlation identifier |
| status | enum | answered, insufficient\_evidence or clarification\_needed |
| answer | string | User-facing answer or bounded explanation |
| citations | list of Citation | Backend-resolved evidence references |
| warnings | list of string | Missing facts, conflicts or other useful limits |
| corpus\_version | string | Snapshot used for this question |
| Citation.source\_id | string | Label appearing in the answer |
| Citation.doc\_id | string | Stable permitted document identifier |
| Citation.title | string | Title from stored source metadata |
| Citation.location | object | PDF page or section/paragraph location |
| Citation.document\_version | string | Immutable cited version |
| Citation.excerpt | string | Exact permitted evidence excerpt |
| Citation.url | string or null | Validated source route or allowlisted URL |


Model revision, token counts and fine-grained latency belong in a developer diagnostic view or logs, unless they help the end user make a decision. Do not expose absolute file paths, raw vectors, access-control rules or secrets.

## Worked example

The following source and answer are synthetic examples, not facts from the team's actual documents. Assume that Training Handbook v1.2, PDF page 8, explicitly says the Lab 3 report is due on Friday at 5 PM.

```
\\\{    
  "schema\\\_version": "1.0",    
  "request\\\_id": "demo-request-001",    
  "status": "answered",    
  "answer": "Submit the Lab 3 report by Friday at 5 PM. \\\[S1\\\]",    
  "citations": \\\[    
    \\\{    
      "source\\\_id": "S1",    
      "doc\\\_id": "training-handbook",    
      "title": "Training Handbook",    
      "location": \\\{"page": 8\\\},    
      "document\\\_version": "1.2",    
      "excerpt": "The Lab 3 report is due on Friday at 5 PM.",    
      "url": "/sources/training-handbook/versions/1.2?page=8"    
    \\\}    
  \\\],    
  "warnings": \\\[\\\],    
  "corpus\\\_version": "training-v1"    
\\\}
```

The source-serving route in the example must be implemented and must recheck access. If source viewing is not available, return url: null and display the title, location and excerpt. Do not show a broken link merely to make a citation look complete.

For insufficient evidence, use the same envelope with status set to insufficient\_evidence, an explanatory answer and citations set to an empty list when no supporting passage was used. For a service error, return an appropriate non-200 status and this separate envelope:

```
\\\{    
  "request\\\_id": "demo-request-002",    
  "error": \\\{    
    "code": "MODEL\\\_UNAVAILABLE",    
    "message": "The answer service is starting. Try again shortly.",    
    "retryable": true    
  \\\}    
\\\}
```

## Citation assembly and display rules

1. Parse source IDs from the generated answer and verify every ID exists in the evidence map for this request. A retrieved but unused source is not automatically a citation.

2. Build citation metadata from stored records. Never accept the model's invented page, title or URL. Keep document version and corpus version visible in developer diagnostics.

3. Verify any quoted excerpt is an exact substring of the stored evidence, subject only to documented whitespace normalization. For a cross-page passage, store its full page range rather than pretending it lies on one page.

4. Display the answer first and place source cards below it. A card should show title, page or section, a short supporting excerpt and a working source link where available.

5. Distinguish source identity checks from factual support checks. A valid S1 label can still be attached to an unsupported claim. Human evaluation must check both citation accuracy and answer correctness.

Render content as escaped text or sanitized Markdown, with raw HTML disabled. Restrict link protocols and source routes. Never execute generated shell commands, SQL, JavaScript or HTML. OWASP identifies downstream validation and sanitization as necessary when handling model output. [OWASP improper output handling](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/).

## Streaming, accessibility and feedback

Return a complete validated response in version 1. Streaming is optional later because tokens can reach the user before final source validation. If streaming is added, visibly mark the answer provisional until a final event confirms validation; cancellation and errors must terminate the stream clearly.

Provide keyboard access, readable contrast, wrapping for long titles and an accessible label for each source link. Show text explanations for loading and error states. A “helpful / not helpful” control may record request\_id and a reason category; store free-text feedback only under the project's retention and access policy.

## Module 16 acceptance and handover

The output module is complete when valid responses conform to the schema, unknown citation IDs fail safely, source links resolve with access checks, long answers wrap correctly, unsupported questions receive honest explanations, and hostile HTML remains inert. Verify error, loading, empty-source, multiple-source and partial-answer screens.

The implementation deliverables are the response schema, output formatting code, source-card behavior, example success/error payloads, citation-validation rules and screenshots from the implemented interface. Explain it as: “I turn the pipeline result into a readable answer with traceable evidence and clear limitations, and I ensure generated text is handled safely.”

