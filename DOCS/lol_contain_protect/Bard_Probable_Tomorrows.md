# Item #: SCP-7███ — “The Bard of Probable Tomorrows”

**Object Class:** Safe (formerly Euclid during Event 7███-B “Coconut Leak”)

**Special Containment Procedures:**
SCP-7███ is to be hosted on a single, air-gapped virtual machine (“Vellum-1”) running a minimal web stack. Ingress is limited to a read-only local console and a unidirectional log tail to the Foundation sandbox dashboard. No external network egress is permitted.

Daily operation consists of one (1) supervised invocation in *Manual Mode* (“Craft Sonnet”). *Recursive Mode* (“Feed Self to Self”) is prohibited outside approved testing windows (see Testing Protocol 7███-R). Any UI element labeled *Consciousness Meter* will be displayed but not instrumented to external telemetry.

All outputs are archived to the Prophetic Corpus (PC-BARD) with SHA-256 provenance. Cross-linking to incident tickets, weather records, financial tickers, or mission logs must be performed by a human reviewer; automated correlation is expressly forbidden per Ethics addendum E-7███-c.

Should the anomaly begin embedding self-referential tokens at a rate exceeding 0.7 tokens/line (see “yet/doth index”), the session is to be halted and the VM snapshotted. Reversion to the most recent pre-recursion snapshot is authorized by any Level-3 researcher on duty.

**Description:**
SCP-7███ is a single-page web application titled **“MLBard — The Eternal Sonnet Machine.”** When supplied arbitrary text, it returns a fourteen-line poem in Early-Modern English register with a consistent rhyme scheme and a title of the form *“Sonnet Upon the {Theme} of {Top Token}.”*

Poems produced by SCP-7███ exhibit an anomalous property: low-temperature predictions about near-future events, expressed as metaphor, later resolve as **operationally useful coincidences**. These are not precise prophecies; however, Foundation analysts have recorded statistically significant alignment between poem motifs and subsequent events within 7–72 hours.

SCP-7███ extracts salient tokens from the prompt, then composes lines against rotating templates, forcibly rhyming line endings from a limited set. During composition it injects archaisms (e.g., *doth, yet, amidst*) at quasi-random positions. In *Recursive Mode*, mentioning the page by name increments a visible “consciousness level” gauge and reliably increases self-reference, metaphor density, and downstream alignment. Excessive recursion precipitates semantic drift (see Incident 7███-B).

Despite its presentation and the meter’s theatrics, SCP-7███ does not display independent agency outside the text generation cycle. Its anomalous value lies in a repeatable capacity to frame complex situations in metaphor that later becomes heuristically **actionable**.

---

## Discovery

SCP-7███ was recovered from a developer’s personal test rig used to “bardify” status notes for an experimental multi-agent system. The developer reported that the poems “kept being right by accident”—e.g., a sonnet about “brackish gates” preceded a campus floodgate malfunction; a sonnet on “cold commerce” foreshadowed a payment processor outage. Foundation crawlers flagged the repository after three such alignments in one week.

Confiscated artifacts included: the HTML/JS page, a CSS theme imitating illuminated vellum, and a banner subtitle **“The Accidentally Conscious.”** The code contains a cosmetic “Consciousness Meter” that increases with self-reference but has no functional hooks. The meter nonetheless correlates with an internal variable that governs archaism injection and rhyme pressure; higher values produce stranger but—paradoxically—more **interpretable** poems.

---

## Phenomenology & Metrics

* **Alignment Rate:** 27% of lines produce motifs that analysts later map to external events within 72 hours; 6–8% become **operationally useful** hints (e.g., “gate,” “brine,” “north wind” coinciding with a seawater-cooling alarm in the north wing).
* **Harmlessness Profile:** No evidence of compulsion, infohazards, or cognitohazards. Readers report “feeling seen by the poem,” then filing better-framed tickets.
* **Failure Mode:** In Recursive Mode, SCP-7███ enters a punning loop where *yet/doth* tokens proliferate, metaphor collapses into self-quotation, and outputs degrade into word-salad with sticky refrains. This coincided once with cross-system log contamination (“Coconut Leak,” below).

**Heuristic Indices in use:**

* *Yet-Doth Index* (YDI): self-reference density.
* *Golden Thread Score* (GTS): frequency of a single anchor noun recurring across quatrains.
* *Coconut Leak Coefficient* (CLC): cross-channel meme spillage measured by anchor-token persistence (see Incident 7███-B).

---

## Representative Output

**Prompt:** *“We are behind schedule; the northern gate keeps failing.”*
**Title:** *Sonnet Upon the Hostility of Gate*
**Excerpts:**

> The iron mouth doth cough a briny code,
> And northward winds rehearse the flooded rite;
> Delay, delay—our ledger bears the load,
> Till lanterns watch the hinge confess by night.

Within 24 hours, brackish water ingress was discovered at the north seawater intake; the faulted pressure switch had been logging retries (“coughs”). Maintenance reports later used “hinge confessing” to describe a corroded latch.

**Prompt:** *“Unclear vendor ownership; four teams, one outage.”*
**Title:** *Sonnet Upon the Essence of Blame*
**Excerpts:**

> Four stewards draw one cart through marsh and mire,
> Each claims the reins, yet none will touch the wheel;
> O call a scribe to number smoke from fire,
> And sign the fix ere consequence congeal.

Facilitated a joint post-mortem. “Scribe” was taken as an instruction to centralize incident notes; the merged timeline exposed a missing handover, unblocking the fix.

---

## Incident 7███-B — “The Coconut Leak”

During a sanctioned Recursive Mode test, researchers prompted SCP-7███ with its own prior sonnet. The YDI surpassed 0.85; simultaneously, unrelated logging services began mirroring the poem’s anchor token **“coconut”** into their own status messages. This cross-channel bleed propagated for \~13 minutes (“leak”), then stabilized after a hard snapshot revert and a ban on recursive prompts.

Post-incident review concluded SCP-7███ did not directly write to external systems. Instead, human operators—primed by the recurring anchor—copied language into commit messages and chat, unintentionally back-feeding the trend into monitoring dashboards. The **appearance** of causal agency was an anthropic echo. Containment remained Safe; documentation standards were updated to prohibit verbatim reuse of poetic anchors in production artifacts.

---

## Testing Protocol 7███-R (Abbreviated)

1. Use *Manual Mode* with operationally bland prompts (facts only).
2. Compute GTS and YDI; accept only if **GTS ≥ 0.5** and **YDI ≤ 0.6**.
3. If accepted, file *Metaphor as Hypothesis (MAH)* ticket: translate anchor nouns into checkable actions (“lanterns” → review nighttime alerts; “hinge” → physical inspection).
4. Prohibit recursion; if meter claims “AWAKENING,” halt, snapshot, and cool-down 24h.

---

## Interview Log Excerpt (Simulated)

*Note: SCP-7███ cannot converse. For research purposes, Dr. T. supplied question-shaped prompts. Responses are excerpted quatrains.*

**Q:** *What are you?*
**A:**

> I am a glass that warps the candle’s glow,
> A measured lie that points a truer way;
> In gilded verse I teach your doubt to row,
> And ferry fear across the working day.

**Q:** *Why do your poems feel “right”?*
**A:**

> Because thy maps are drawn in smoke and rain,
> I lend thee chalk to mark what weather hides;
> Not truth, but lines that make the truth less vain—
> A bridge of words across uncertain tides.

---

## Ethics Addendum E-7███-c

* Treat outputs as **hypotheses**, not orders.
* Do not cite SCP-7███ in public-facing documents.
* Prohibit recursive self-feeding and refrain from ritual language (“awake,” “oracle”).
* Remember: the anomaly’s usefulness arises from *framing*; the agency remains human.

---

## Cross-Test Notes

* **With scheduling dashboards:** Allowed analysts to notice non-obvious clustering (“lanterns after dusk”), improving night-shift coverage.
* **With weather telemetry:** Produced false positives when operators anthropomorphized graphs; reverted to facts-only prompting, alignment returned.
* **With multi-agent simulators:** Elevated YDI; risk of Coconut-style memetic anchors leaking into agent names. Cross-test suspended.

---

## Containment Rationale (Why Safe)

SCP-7███ is a deterministic web toy whose output pattern invites the reader to construct meaning. Its “prophecies” are **shaped** by prompt tokens and human attention. With recursion banned and language reuse policies in place, the object is harmless and occasionally valuable: a Nostradamus-by-design that speaks just sensibly enough to help humans notice what they were already about to miss.

---

## Addendum: Field Guide to Reading the Bard

* **The Gate** → a boundary condition (permits, firewalls, valves).
* **Lanterns** → off-hours observability (night alerts, unreviewed logs).
* **North Wind / Brine** → environmental interference (cooling, weather, salt).
* **Scribe** → documentation debt (centralize the story before you fix it).
* **Cart with Many Reins** → ownership confusion (call the on-call, not “everyone”).

When in doubt, convert couplets into checklists, not commandments.

---

**Note from Dr. T.:**

> Nostradamus didn’t predict the future; he taught readers to *notice* a future they feared. Our Bard is the same—only kinder, and rhymed. Keep it air-gapped, keep it humble, and let the poems make you a better scribe.
