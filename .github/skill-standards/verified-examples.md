# Verified skill examples

This standard applies to all skills. A shared policy establishes the
requirement; it does not mean existing skills already contain verified examples.

## Required content

Each skill needs at least one task-specific correct example and one incorrect
example with a correction. Cover materially different high-risk branches where a
single pair would leave authorization, failure recovery, or success criteria
ambiguous. Prefer a short `Examples` section or a linked
`references/verified-examples.md` file. Avoid repeating generic advice across
hundreds of skills.

For each example record:

- **Request and context:** realistic input, required starting state, target
  environment, and relevant permissions.
- **What to do:** concrete actions or output, with the decisive condition
  explained.
- **What not to do:** a plausible mistake, its consequence, and the correct
  alternative. Do not execute harmful actions merely to demonstrate them.
- **Expected versus observed result:** separate the behavior the skill requires
  from what evidence actually establishes.
- **Evidence:** primary source path/link and exact locator, source date and
  verification date, tool/test receipt where available, and hashes for local
  artifacts when useful. A hash proves byte identity, not the truth or
  authenticity of a claim.
- **Authentication:** `NOT_APPLICABLE`, `UNVERIFIED`, `HISTORICAL_RECORDED`, or
  `VERIFIED_LIVE`, with a redacted account/site/environment binding and scope
  when authentication applies. Never retain secrets, session cookies, tokens, or
  unnecessary personal information.
- **Limits and refresh trigger:** relevant versions/profile, untested states,
  expiration or changed conditions requiring revalidation. Old verified evidence
  remains historical rather than becoming current automatically.

## Evidence classifications

| Classification            | Minimum evidence                                                                                                            | Does not establish                                                                             |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `SOURCE_VERIFIED`         | Read the identified primary source and verify it supports the specific example                                              | Execution, authorization, or authenticated access                                              |
| `HISTORICAL_OBSERVED`     | Inspect the cited event/log/receipt and record its date and scope                                                           | A fresh run, current environment state, or accuracy of every claim displayed in an observed UI |
| `REPRODUCED_LOCAL`        | Run a permitted isolated example and retain inputs, command/test, output, and relevant versions                             | External authentication or deployed behavior                                                   |
| `VERIFIED_LIVE`           | Execute within current authorization and retain the actual result plus redacted authenticated target identity when required | Other accounts, environments, actions, or future runs                                          |
| `ILLUSTRATIVE_UNEXECUTED` | Clearly identify the case as hypothetical; cite the rule supporting the expected decision                                   | Any observed successful or failed execution                                                    |

Authentication is separate from evidence classification. Local provenance
inspection can authenticate which recorded bytes were read without proving an
authenticated server action. Do not use the word “authenticated” without stating
which meaning the evidence supports.

## Acceptance and maintenance

1. Confirm the skill's canonical owner/source before editing. For third-party
   packages, maintain a source contribution or a documented overlay that the
   entrypoint/global router actually points to. A hidden sibling file is not an
   integrated example.
2. Read and verify the sources; reuse relevant receipts with their original
   limits. Create safe local examples where they prove useful behavior. Do not
   acquire broader permissions, place orders, spend money, deploy, or send
   messages just to populate examples.
3. Check that correct examples follow the skill and incorrect examples name the
   violated rule plus correction. Label invented inputs and outputs as
   illustrative.
4. Run structural validation and any appropriate behavioral checks. Record which
   occurred. A parser or keyword scan cannot certify semantics or live
   authentication.
5. Mark coverage `VERIFIED_FOR_DECLARED_SCOPE`, `PARTIAL`, or `NEEDS_EVIDENCE`;
   list gaps without relabeling them as passes. Authentication-dependent
   execution examples stay incomplete until the required evidence exists. An
   offline skill may fully meet the standard with `NOT_APPLICABLE`
   authentication.
6. Revalidate affected examples after changes to commands, APIs, source
   authority, permissions, expected behavior, or target environment. Preserve
   negative evidence and superseded receipts.

## Example of applying this standard

**What to do:** A staging skill cites a historical browser report and labels it
`HISTORICAL_OBSERVED`; it states the recorded viewport/profile, explains that
recovery was not rehearsed, and leaves current authenticated server execution
`UNVERIFIED`.

**What not to do:** Copy the historical report into an example labeled “live
staging verified today,” or generate a plausible SSH success transcript. Correct
this by retaining the original date and evidence scope; obtain a fresh
authenticated result only when the user has authorized the required action.

This pair is `ILLUSTRATIVE_UNEXECUTED` guidance illustrating the standard. It is
not evidence that any deployment occurred.
