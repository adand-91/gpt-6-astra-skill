# Evidence rules

A retrospective is quoted later as fact. That is why it has to be harder to write than an
opinion.

## Mechanical layer first

Run the scanner before reading any conversation. Reading first and counting afterwards
produces conclusions in search of evidence: you will find the numbers that support the story
you already formed.

Order is: script → numbers → read the flagged messages → interpret → write.

## Numbers the model may not produce

Never write one of these from memory or by eye:

- how many messages, turns, sessions, or tool calls there were
- how much of the context, time, or output some activity took
- proportions, percentages, "most of", "the majority of"
- how many times something was repeated
- how big a file or session is

All of them come from the scanner's JSON. If the scanner does not report it, either extend
the scanner or write that it is unknown. Do not interpolate.

A figure a subagent stated in prose is **not** a measurement. Only the script's output is.

## Quote, do not paraphrase

User messages go in verbatim, with their timestamp. Paraphrasing a correction is how the real
requirement gets lost — the user's own phrasing is the evidence, and your summary of it is
already an interpretation.

Trim with an ellipsis if it is long. Do not clean up grammar, do not translate, do not make it
more professional. If the user swore, the quote has the swearing in it; that is signal about
how badly the thing had gone wrong.

## Corrections are candidates, not findings

The scanner flags messages containing correction markers. That is keyword recall, so it over-
and under-catches: "这个不错" contains 不 and is praise; a correction can arrive as a bare
"?" or a screenshot with no words at all.

Every flagged message gets a human-or-model judgement before it enters the ledger. Every
un-flagged message near a flagged one is worth a look, because corrections cluster.

## Disk beats transcript

When the conversation says a file was written and the file is not there, the file is right.
Writes fail, later steps overwrite, temp directories vanish, and "done" gets said before the
verification that never ran.

Before recording an outcome as achieved, check the artifact: it exists at the stated path,
the command exits zero, the content is what was promised. Where transcript and filesystem
disagree, report the difference rather than choosing the flattering one.

## Three labels that never merge

| Label | Means | Rule |
|---|---|---|
| `SAID` | The user's words, quoted | Must carry a timestamp |
| `INFERRED` | Your reading | Stays marked; never presented as what they said |
| `UNKNOWN` | The transcript does not answer it | Must not be filled in to look complete |

An `INFERRED` item promoted to `SAID` is the one unforgivable error here. The whole point of
a retrospective is that someone will act on it without re-reading the source; if your guesses
are indistinguishable from their words, they will act on your guesses.

`UNKNOWN` is a real answer. A retrospective with three honest unknowns is more useful than one
with no gaps and two inventions.

## Windows and time zones

State the window explicitly, with an offset, in the report header. Sessions are timestamped
in UTC while people think in local time, and a retrospective labelled with the wrong day gets
filed against the wrong work. Pass `--since` / `--until` rather than eyeballing which files
look recent.
