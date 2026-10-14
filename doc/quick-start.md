# Strategy Boardroom: Quick Start

The Strategy Boardroom is an AI advisory board. You bring it a growth question, such as "Which market should we enter first?" Researchers gather sourced facts from the web, then a board of AI directors with different viewpoints debates, votes and gives a verdict. Everything runs in your web browser. There's nothing to install.

**Your link:** [paste the shared link here]

---

## Before you start

- **You need a Claude account.** Sign up free at claude.ai. A free plan may run out partway through a full session, so a paid plan is more comfortable.
- **Usage counts against your own Claude plan,** not the plan of the person who shared the app. The app shows an estimate before you start (step 2).
- **You need permission to use the page, not just view it.** If a note says "View only: you can read sessions but not convene the board", ask the person who shared the link to give you access that lets you use it.
- **Allow 20 to 40 minutes** for a full session, plus several minutes for research. Your progress is saved, so you can stop and come back.
- **Assume that others using the same link can see what you enter.** Don't enter confidential figures until whoever shared the link confirms who can open it.

---

## The 6 steps

### 1. Open the link and sign in

Open the link in Chrome, Safari or Edge. If asked, sign in to Claude and allow the page to use Claude.

> To see how it works first, click **Load an example** at the top of the first page. It fills in a sample company you can run from start to finish. Click **How it works** on the left for a diagram of the whole process.

### 2. Describe your question

Fill in the form on the first page, **Put a growth question to the board**:

| Field | What to write | Example |
| --- | --- | --- |
| Company name | Your company | Acme Testing Labs |
| Sector or industry | What you do | Construction materials testing |
| Geography you serve | Where you work | South Jersey and Philadelphia |
| Growth area to explore | The area you're considering | Public infrastructure testing |
| Decision question | The decision, in one sentence | Which public market should we pursue first over the next 2 years? |
| Markets you already have in mind (optional) | One per line, or leave blank for the board to propose them | State DOT materials testing |
| Company profile | Size, services, locations, licenses, key clients, and which way you're leaning | 60 staff, 2 labs, AASHTO accredited… |
| Constraints | What limits you | Hiring certified technicians is slow |
| Your assumptions | What you believe but haven't proven | State DOT spending will grow |

Then, further down the same form:

- **Directors seated for this session:** tick 3 to 12 directors. All the default directors are ticked to start with.
- **Notes for the researcher (optional):** sources to check, or things you already know.
- **Debate depth:**
  - **Quick:** the 4 directors most relevant to your question, 1 round. For smaller, reversible decisions.
  - **Standard:** every seated director, 1 round of cross-examination. For most decisions.
  - **Deep:** 2 rounds plus a red team that argues against the leading option. For big or hard-to-undo decisions. Uses the most of your Claude plan.
- **Ratify a draft resolution (optional):** after the vote, the directors sign off on a written plan. It costs about one more call per director.

Check the **Estimate** line under Debate depth. It shows about how many Claude calls and tokens the session will use, and it updates as you change the seats, depth or ratification. Then click **Ask Counsel for an analysis plan**.

### 3. Review and approve the plan

The Strategy Counsel, a neutral adviser who doesn't vote, proposes 3 to 5 markets to research and the questions that will decide each one.

- Untick any markets you don't care about, rename them, or add your own. Two or three markets give the board a real choice without making the research long.
- Add any instructions for the researchers, such as "focus on New Jersey and Pennsylvania".
- Click **Approve plan and request research**. To get a different set of markets first, click **Regenerate plan**.

### 4. Run the research (the one manual step)

The page shows a **Waiting for sourced research** panel. It lists the research limits and holds a full research request: the approved markets, their questions, and the rules the researchers follow.

1. Click **Copy**.
2. Open a **new Claude chat** at claude.ai in another tab, with web search turned on.
3. Paste the request and send it.
4. Leave it running. The research usually takes several minutes.
5. Return to the Boardroom tab. When the research finishes, the evidence appears: sourced facts, a summary, a market scorecard and the gaps the researchers couldn't fill. The status changes to **Evidence ready**.

> If nothing appears after the chat finishes, refresh the Boardroom page. If it still doesn't appear, contact the person who shared the link.

### 5. Convene the board

Before you start, you can still change who sits on the board in the **Who sits on the board** panel. Seats lock once the debate begins.

Click **Convene the board** and watch the debate unfold:

1. **Brief:** the Counsel summarizes the evidence and points out where it is thin.
2. **Opening positions:** each director gives a sealed view, without seeing the others.
3. **Cruxes:** the Counsel names the real disagreements.
4. **Cross-examination and rebuttals:** directors challenge each other. Deep sessions also include a **red team**, which runs in other sessions only if the board agrees too quickly.
5. **Vote:** each director scores every option in a sealed vote.
6. **Draft and ratification,** if you chose it: the Counsel drafts a resolution and the directors endorse, amend or dissent.
7. **Record of decision:** the Counsel writes up the result.

To go one stage at a time, use **Run first stage only** and then **Run next stage only**. Click **Stop session** at any time; finished turns are kept.

### 6. Read the verdict and save it

The verdict comes from the directors' weighted scores, not a show of hands. It is one of:

| Verdict | Meaning |
| --- | --- |
| **GO** | Strong support. Proceed. |
| **GO WITH CONDITIONS** | Proceed, but only if the listed conditions are met. |
| **RESHAPE** | The idea has merit but needs changes. |
| **DON'T DO IT** | The board doesn't support it. |
| **HOLD** | Pursue none of the options for now. |

A single director can cap the verdict:
- **Ruin, or a breached red line:** if a director flags a risk that could sink the company, or says the option breaks its red line, the verdict can go no higher than **RESHAPE**.
- **A red line at risk, or a hard-to-undo bet the board is split on:** the verdict can go no higher than **GO WITH CONDITIONS**.

Any cap is shown next to the verdict.

Read the **dissents**, **red lines**, **key assumptions to test** and **kill criteria**, not just the verdict.

To keep a copy, either:
- click **Print or save as PDF** at the top of the session, then choose **Save as PDF**; or
- click **Download report** to save the whole record as a page you can open and print later.

---

## Other useful features

- **Ask one director:** on the **Board members** page, click **Ask this director** for a single director's answer to a quick question, without running a full session.
- **Board members:** see each director's lens, mandate and red line, edit them, or add new directors.
- **Supporting data:** give a director your own files or notes (PDF, Word, Excel, CSV or text). Click **Pin** on the most important ones so they're always read in full.
- **Summary cards:** for a long file, the app drafts a short summary card of the key figures, names and conclusions. You edit it before saving, and the director reads it every session. Use **Make card** to create one for any file.
- **Export board / Import board:** save your directors and their data to a file, or load a board someone sent you. Import asks before overwriting anything.
- **Add a debate round:** after a session, run another round if the debate felt unfinished.
- **Compare sessions:** set the votes and verdicts of past sessions side by side.

---

## If something goes wrong

| Message or problem | What to do |
| --- | --- |
| "Claude usage limit reached" | Your plan's limit is used up. Completed turns are saved. Come back later and click **Continue to the decision**. |
| "Claude access wasn't allowed for this page" | Reload the page and allow Claude when asked. Make sure you're signed in. |
| "Your Claude session expired" | Sign in to claude.ai again, then continue. |
| "Saving is unavailable" banner | Your work won't be saved. Don't start a session; tell the person who shared the link. |
| "View only" note | You can read sessions but not run them. Ask for access that lets you use the page. |
| A session stopped partway | Click **Continue to the decision** to resume from where it stopped. |
| A stage looks wrong | Choose it under **Regenerate from**, click **Regenerate**, then click again to confirm. That stage and every later one are replaced. |
| The research never appears | Refresh the page, and check that the research chat finished without errors. |

---

## Tips for better results

- **Be specific.** "Should we add geotechnical drilling in Burlington County?" beats "How should we grow?"
- **Say which way you're leaning,** in the company profile or your assumptions. The board will test it instead of agreeing with it.
- **List your assumptions.** The board is designed to challenge them.
- **Give directors real numbers,** with dates, through Supporting data. Generic boards give generic advice.
- **Treat the verdict as advice, not a decision.** The board works only from the evidence it found and the data you gave it.
