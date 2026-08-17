# Nine questions, in plain words

The same nine fields as the confirmation sheet, asked so that someone with no technical background
can answer them. Do not send all nine at once — that is a questionnaire dump. Take the two or three
that matter most for this task and ask those. See
[references/clarify-loop.md](../references/clarify-loop.md).

Each question has an example answer, because a question with an example attached is much easier to
answer than a question alone.

**Goal** — What do you want to be able to do that you can't do now?
> "Right now I copy 300 photo names into a spreadsheet by hand every month."

**In scope** — When this is finished, what will you have in your hands?
> "One spreadsheet, and a thing I can double-click to make it."

**Out of scope** — Is there anything nearby you *don't* want me touching?
> "Don't rename the original photos. I need them as they are."

**Inputs** — What do I start from, and can you send me one real example?
> "This folder. Here's a zip with 20 of the photos in it."

**Outputs** — Where should the result end up, and in what form?
> "An Excel file on my desktop. One row per photo."

**Acceptance** — After I hand it over, what will you do to check it's right?
> "Open the spreadsheet and see if the 300 rows match my folder."

**Constraints** — Is there a date you need it by, a budget, or anything I'm not allowed to use?
> "Before the 30th. And it has to work without installing Python."

**Where it runs** — Whose computer does this run on, and what is it?
> "Mine. Windows 11 laptop."

**Open items** — What am I still guessing about?
> This one is yours to answer, not theirs. List what you have not been told and say which of those
> you are deciding yourself.

---

## Two things to do with the answers

**Read the important lines back in their words** before you lock anything. Not the whole sheet — the
two or three lines that would be expensive to get wrong.

> "So: I read the folder, you get one Excel row per photo, it has to run on your Windows laptop with
> nothing installed, and you'll check it by counting rows against the folder. Right?"

**Say which parts you decided yourself.** One line, plainly. This is the whole point of the
`INFERRED` label.

> "Two things I picked without asking, both easy to change: the columns are filename, date taken,
> size; and old runs get overwritten rather than kept."
