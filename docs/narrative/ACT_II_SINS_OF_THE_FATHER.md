# Dust & Debt — Act II: Sins of the Father
Narrative script pack 02 | First-draft screenplay and production specification

**Status:** Narrative source only. No gameplay code or cinematic assets are installed by this document.
**Continuity:** Direct follow-up to Act I MAIN_01–MAIN_05. Main character: Elias Ward.

## MAIN_06 — A Familiar Brand
**Site:** Existing Galloway-region ranch to be mapped to a verified location.
**Objectives:** investigate burned barn; identify Blackthorn mark; interview Ada Galloway; decide whether to help survivors.

ADA: "Black coats came before dawn. Said a debt was past due."
ELIAS: "What debt?"
ADA: "My father never owed that company a cent. They brought papers anyway."
ELIAS: "Did you see who led them?"
ADA: "Silver thorn on his collar. Man with a gray beard. Never took his gloves off."

**Branches:** Offer shelter (galloway_aided, restitution+2); decline (galloway_declined). The family can reappear during the Act IV refugee missions. Cinematic: CIN_BRAND_IN_ASH, short in-engine reveal.

## MAIN_07 — The Man at the Table
**Site:** Boarding house and the Hollow Creek ruins.
**Objectives:** confront Gideon Price; visit old eviction site; inspect family marker; respond to accusation.

PRICE: "You came back to the place you helped empty."
ELIAS: "I came to see what was left."
PRICE: "That's more than you did twelve years ago."
ELIAS: "I didn't light that barn."
PRICE: "Didn't stop it neither."

**Branches:** Confess (price_confessed, restitution+1); deflect (price_deflected); threaten (price_threatened, reputation-2). CIN_HOLLOW_CREEK_EXTENDED shows the fixed historical event: young Elias guarded the path during an eviction, but did not set the fire.

## MAIN_08 — Old Blood
**Site:** Existing Valleyford region.
**Objectives:** hear warning bell; speak to Captain Mara Vale; protect civilians in grain hall; resolve surrendered/escaping attackers.

MARA: "We have fifteen people inside the grain hall. Five of them children."
ELIAS: "How many riders?"
MARA: "Seven, maybe eight. They say the land belongs to the railroad."
ELIAS: "They won't stop at the fence."
MARA: "Then hold the gate while I get people to the creek."

**Branches:** Capture attackers alive (gunmen_captured, mercy+2); kill combatants (gunmen_killed); draw riders away (gunmen_escaped, reputation-1). Protect people rather than require a specific kill count. Cinematic: CIN_RAID_WARNING.

## MAIN_09 — What Clara Knew
**Site:** County records office, location to confirm.
**Objectives:** recover Clara's letter bundle; compare two conflicting deeds; examine Elias's signature; read her letter.

NORA FINCH: "Mrs. Ward was here twice in the week before the fire."
ELIAS: "She didn't tell me."
NORA: "I suspect she tried."

**CIN_CLARAS_LETTER:** Slow illustrated cuts of Clara writing by oil lamp. Voiceover:

CLARA: "The rail company has used the same agreements for years. The names change. The families do not."
CLARA: "Your signature is on the oldest papers I found. That does not make you the author of every cruelty, but you must not pretend you were a stranger to it."
CLARA: "I do not need you to be innocent, Elias. I need you to be the man you promised our son you would become."
CLARA: "If the truth is ugly, let it be ugly. Just don't bury it because you're ashamed to look."
CLARA: "Whatever happens, get Sam away from the fighting. Please choose us over the land."

**Outcome:** clara_letter_read and fraud_pattern_known, unlocking the Act III financial investigation. No player-choice gate on these critical facts.

## MAIN_10 — The Names We Carry
**Site:** Hollow Creek survivors' camp.
**Objectives:** meet Eliza Price; recover/return original deed; choose restitution; enter short playable fixed-memory scene.

ELIZA: "Paper won't grow the orchard again. But it might keep them from taking the next one."
ELIAS: "I can help rebuild."
ELIZA: "Then start with the roof. We'll see who you are after it rains."

**Branches:** Rebuild without conditions (hollow_creek_restitution, restitution+3); pledge later aid (hollow_creek_promise, restitution+1); refuse (hollow_creek_refused). CIN_HOLLOW_CREEK_TRUTH dramatizes an unchangeable past. Chapter II closes with Elias: "I used to believe forgetting was the same as changing."

**Chapter transition:** ACT III — THE DEVIL'S LEDGER.

## Integration rules
- Existing game: Python/Tkinter, deterministic route graph in frontier_routes.py, original 4,800×3,200 starting parcel and expanded mainland. Treat map location strings above as placeholders until coordinates are verified.
- Do not overwrite existing bounty missions or NPC IDs; integrate via a narrative event bridge.
- Every mission must support checkpoint/retry and idempotent payout; both mercy and violence branches maintain the main path.
- Skip cinematics safely, applying completion flags once and resuming actor AI and game controls.
- This file is **narrative source**, not a production runtime patch.
- The user's existing "Forsaken to This Land.m4a" is the musical reference; recordings are not embedded.
- Separate Gideon Price (Hollow Creek survivor) from Gideon Shaw (later railroad agent).
- Fire-order amendment and Shaw's role remain unrevealed until Act V.
