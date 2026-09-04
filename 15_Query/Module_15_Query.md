# Module 15: Query

**Project: Simple RAG System**  
**Team Leader**  
**Prepared by:** Mokshith H S  
**USN:** 4BB23AIO20  
**Department:** Artificial intelligence and Machine Learning

## 1. Purpose and scope

The Query module is the entry point for a user's question. It collects the question, validates the request, resolves the permitted domain and passes a consistent request to the RAG pipeline. It also manages the browser's submission, waiting and retry behavior.

For example, a user types “What is the submission deadline for Lab 3?” The module checks the input and submits it to Module 13. The pipeline retrieves evidence and generates an answer; Module 15 formats the answer and citations. The deadline is determined by the indexed documents, not by this module.

The first version supports single-turn questions in a browser, a JSON API and optional selection of a permitted domain. Conversation history, voice input, file uploads and automatic question rewriting are later features. A question about the subject does not train or fine-tune the model: it starts retrieval against the prepared knowledge base.

### Ownership and dependencies

| Module | Responsibility at the query boundary |
| - | - |
| 1: Project Setup | Shared settings, schemas, dependencies and Docker configuration |
| 14: Query | Question form, request validation, route and submission lifecycle |
| 13: RAG Pipeline Integration | Embedding, retrieval, evidence gate and generation coordination |
| 15: Output | Response structure, source cards and safe answer display |


Modules 7 and 10 implement embedding and retrieval behind Module 13. Query should not maintain another embedding model, query Qdrant independently or construct a second prompt. Keeping one pipeline prevents conflicting behavior.

## 2. API contract

**Endpoint:** `POST /query` | **Content type:** `application/json`

The browser sends a JSON body. FastAPI supports request-body models with validation and generated API documentation. Declare a shared Pydantic request model rather than passing an unrestricted dictionary through the application. [FastAPI request bodies](https://fastapi.tiangolo.com/tutorial/body/).

| Field | Proposed contract |
| - | - |
| `question` | Required string; 1–2,000 Unicode code points after trimming outer whitespace; whitespace-only text is invalid |
| `domain` | Optional string or null; must identify a configured domain the current user may access |
| `session\_id` | Omitted or null in version 1; reject non-null values until conversation support exists |
| Unknown fields | Reject, including client-supplied permissions, model URLs or collection names |


Use strict string validation rather than silently converting numbers, arrays or objects into questions. The 2,000-character ceiling is a proposed product limit, not a model context limit. Enforce token limits separately.

```
\{  
  "question": "What is the submission deadline for Lab 3?",  
  "domain": "training",  
  "session\_id": null  
\}
```

If domain is omitted, select the configured default only when it is permitted. If no unambiguous permitted default exists, return a domain-required validation error and ask the user to choose. Do not interpret a missing domain as unrestricted access to every collection.

The client cannot specify `user\_id`, `access\_scope`, `collection`, `system\_prompt` or `llm\_base\_url`. The backend derives identity and permissions from authenticated context, or from a documented fixed local profile in the single-user demonstration. A local profile is not a substitute for authentication in a shared deployment.

## 3. Validation and preprocessing

Apply validation on the server even when the browser has already checked the input. Browser controls improve usability, but requests can bypass them. Preserve legitimate punctuation, numbers, negation, code identifiers and Unicode text; broad keyword or character blacklists can change the question's meaning. [OWASP input validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html).

1. Enforce the proposed 16 KiB request-body limit before parsing the entire body. Count bytes actually received, including streamed requests; do not rely only on `Content-Length`.

2. Require JSON, parse it and verify that the body is an object with the allowed fields and types.

3. Trim leading and trailing whitespace from the question. Reject empty text, whitespace-only text and unsupported control characters; permit ordinary line breaks and tabs. Do not lowercase, remove stop words or silently correct technical terms.

4. Enforce the question's character limit and the configured domain identifier format. Reject extra fields. Pydantic custom validators can implement checks beyond the basic field types. [Pydantic validators](https://docs.pydantic.dev/latest/concepts/validators/).

5. Resolve the user's allowed domain and source scope. Check permissions again in retrieval and in source-serving routes; the domain selector is not an authorization boundary.

6. Check tokenizer limits before embedding or generation. Return a shortening instruction if the question does not fit, rather than silently truncating its final words.

### Two token budgets must be respected

The baseline MiniLM embedder truncates beyond 256 WordPieces by default. Count the actual query embedding input with truncation disabled, including special tokens and any configured prefix. A question below 2,000 characters can still exceed this limit. Delegate this check to the shared tokenizer/embedding adapter used by the pipeline. [MiniLM model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2).

The generator has a separate configured 4,096-token runtime window in the project baseline. Module 13 must count the fully rendered prompt, including system instructions, question, evidence, chat template and the reserved output budget. Embedding tokens and generator tokens are not interchangeable. Query validation cannot guarantee that the later evidence-packed prompt will fit.

For consistency, use Python Unicode code-point length as the server's character-count definition. A browser counter should match it, for example with `Array.from(text).length`; JavaScript string length and HTML length controls use UTF-16 units and may count emoji differently.

## 4. Request lifecycle and pipeline handoff

The API boundary creates one server-generated `request\_id` and starts the overall request deadline. Module 13 reuses that identifier and the remaining deadline; it does not restart the timer. Keep an immutable copy of the submitted question and domain so later edits in the form cannot change an in-flight request.

The following pseudocode specifies behavior and dependencies. Its helpers must be implemented; it is not a runnable FastAPI application.

```
handle\_query(http\_request):  
    context = begin\_request(deadline\_seconds=120)  
    enforce\_body\_size\_and\_content\_type(http\_request)  
    query = validate\_query\_schema(http\_request.body)  
    principal = resolve\_backend\_identity(http\_request)  
    scope = authorize\_domain(principal, query.domain)  
    enforce\_query\_token\_limits(query.question)  
    enforce\_rate\_and\_queue\_limits(principal)  
  
    result = pipeline.answer(  
        query=query,  
        principal=principal,  
        permitted\_scope=scope,  
        request\_context=context  
    )  
    return serialize\_output\_contract(result)
```

Perform request-size and cheap structural checks before expensive work. Authentication and authorization must finish before any protected retrieval. The module must reject invalid input without invoking the generator. Do not let a user-provided field replace the backend identity or scope.

Module 13 resolves the corpus release, checks embedding compatibility, retrieves evidence and handles its evidence gate. A valid question with no supporting documents receives `insufficient\_evidence`; it is not an input-validation error. Ambiguity can lead to `clarification\_needed`, using Module 15's existing response contract.

## 5. Browser behavior

Provide a labeled multiline question field, an optional permitted-domain selector, an Ask button and a visible status message. A placeholder can show an example, but must not be the only label. Keep the first version in the same browser application served by the API.

| State | Required behavior |
| - | - |
| Ready | Question is editable; empty submission is prevented |
| Invalid input | Explain the issue near the field and preserve the text |
| Waiting | Show “Searching the documents…” and prevent duplicate submission |
| Answered | Hand the validated response to Module 15 |
| No evidence / clarification | Display the pipeline's explanation or question |
| Failed | Preserve the question and show the relevant retry guidance |
| Cancelled | Stop waiting and ignore late responses from that request |


Track the active request locally. If a cancelled or older response arrives after a new submission, it must not overwrite the new result. Do not automatically resend a timed-out POST: the server may still be processing the first request.

Browser cancellation can use `AbortController` to abort a fetch request. This does not guarantee that server-side model computation has stopped; propagate cancellation through Module 13 where supported and retain the server deadline. [MDN AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController).

Use a real form, keyboard-accessible controls, readable contrast and an accessible live status region. For multiline input, keep Enter as a newline and offer an explicit submit button. Display submitted text as escaped text; Module 15 owns sanitized answer rendering. Input validation alone is not protection against executable HTML.

## 6. Responses and failures

Successful and domain-outcome responses reuse Module 15's `AnswerResponse`: `schema\_version`, `request\_id`, `status`, `answer`, `citations`, `warnings` and `corpus\_version`. Do not introduce a different success envelope or return an unstructured model string from this route.

| HTTP status | Situation and handling |
| - | - |
| 200 | Answered, insufficient evidence or clarification needed |
| 413 | Body-byte cap or query-token limit exceeded; ask for a shorter request |
| 415 | Unsupported content type; require JSON |
| 422 | Invalid JSON, missing/invalid fields, blank question or character limit exceeded |
| 401 / 403 | Missing valid authentication / access denied, where authentication is enabled |
| 429 | Rate or generation queue limit reached; show retry guidance |
| 502 | Invalid upstream model response |
| 503 | Required service or compatible corpus is not ready |
| 504 | Overall request deadline exceeded |


Use one safe error envelope across Query and Pipeline. The following example is an application validation error, not FastAPI's unchanged default response:

```
\{  
  "request\_id": "demo-query-001",  
  "error": \{  
    "code": "EMPTY\_QUESTION",  
    "message": "Enter a question before submitting.",  
    "retryable": false  
  \}  
\}
```

FastAPI provides default validation error handlers and allows custom handlers. Implement and document the conversion to this project's envelope, including JSON-parsing failures and route errors. Avoid copying raw validation inputs, stack traces or internal exception messages into responses. [FastAPI error handling](https://fastapi.tiangolo.com/tutorial/handling-errors/).

An invalid question becomes valid only after correction; a retry button alone is not the remedy. Service or network failures should preserve the question and allow a deliberate retry. Return `Retry-After` where the backend can determine an appropriate wait for throttling.

## 7. Implementation and Docker integration

| Proposed path | Implementation responsibility |
| - | - |
| `15\_Query/Module\_14\_Query.md` | This module's documentation |
| `app/contracts.py` | Shared `QueryRequest`, success and error models |
| `app/query.py` | Route, validation and handoff to Module 13 |
| `app/config.py` | Body/character limits, domain configuration and deadline |
| `app/static/` | Browser form, request lifecycle and accessibility behavior |
| `tests/test\_query.py` | Input, authorization and handoff acceptance checks |


These are proposed application paths, not a claim that the repository already contains them. Define the shared schema once and import it from Query, Pipeline and Output. Resolve package versions through Module 1's lock process.

The Query module runs inside the existing FastAPI container and needs no separate container. Browser JavaScript should submit to the relative `/query` URL. Compose names such as `http://api:8000` are for container-to-container traffic and are not the browser's service addresses. Keep the documented local browser entry point `http://localhost:8000` and test on each claimed OS/architecture.

Serve browser assets locally for offline operation. If the frontend later runs on another origin, configure the explicit allowed origins and the chosen authentication protections; do not make permissive cross-origin settings the default. Keep model and database endpoints in backend configuration.

Log request ID, validation outcome, domain where permitted, duration and response status. Do not routinely log full questions, authorization headers or source text. A body carried by POST can still be captured by application or proxy logging, so configure those logs deliberately.

## 8. Acceptance checks and handover

The following checks are required implementation evidence. No results are claimed in this document. Use a fake pipeline for request-boundary checks, then repeat the successful path with the real services.

| Check | Expected result |
| - | - |
| Supported valid question | Exactly one pipeline invocation; output matches Module 15 |
| Empty, spaces or missing question | 422; pipeline is not called |
| Wrong type or additional field | 422; no coercion into a question or permissions |
| Character count at / over 2,000 | At-limit input passes this check; over-limit returns 422 |
| Body exceeds 16 KiB | 413 before full body parsing, including streamed bodies |
| Question exceeds embedding tokens | 413; no silent truncation or generation |
| Unknown / forbidden domain | Controlled validation / access-denied response |
| Missing domain without a default | Domain-required error; no unrestricted search |
| Non-null session ID in version 1 | 422; unsupported history is not silently accepted |
| HTML, punctuation and Unicode | Text remains inert; meaning is preserved |
| Valid but unsupported question | 200 with insufficient evidence |
| Double click, cancellation, late reply | No unintended duplicate submission or stale overwrite |
| Unavailable service / deadline | 503 / 504; question remains available to retry |
| Keyboard and cross-OS use | Form, status and output work on declared target browsers |


Check both sides of each numerical boundary. Test a short character string that exceeds the embedding token limit, and verify emoji counting agrees between browser and server. A model-free validation test does not establish retrieval or answer quality; those remain pipeline evaluation responsibilities.

**Handover package:** the query specification, shared request schema, route and browser implementation, error mapping, representative payloads, test results and screenshots of ready, waiting, invalid and failed states. Record the application commit and test environment.

**Suggested team explanation:** “I build the question-entry part of the RAG system. It validates what the user submits, applies the permitted domain, passes one consistent request to the pipeline and manages loading, errors and retries.”

## 9. Sources and design decisions

Official framework, model and security references are linked beside the claims they support. The body cap, character cap, single-turn scope, error mapping and 120-second starting deadline are proposed project decisions. Validate them on the team's hardware and corpus before release.

- [FastAPI: request bodies](https://fastapi.tiangolo.com/tutorial/body/) — typed JSON inputs and API documentation.

- [Pydantic: validators](https://docs.pydantic.dev/latest/concepts/validators/) — custom field and model validation.

- [FastAPI: handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) — exceptions and custom error handlers.

- [OWASP: input validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) — server validation and preservation of legitimate free text.

- [MiniLM model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) — embedding model properties and truncation limit.

- [MDN: AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController) — browser request cancellation.

Related repository documents: `02\_Project\_Setup/Module\_1\_Project\_Setup.md`, `14\_RAG\_Pipeline\_Integration/Module\_13\_RAG\_Pipeline\_Integration.md` and `16\_Output/Module\_15\_Output.md`.

