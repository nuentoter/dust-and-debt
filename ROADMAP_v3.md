# Dust & Debt — Development Roadmap: v2.4 → v3.0

**Updated:** November 8, 2026  
**Current playable source:** v2.5 — Working Frontier  
**Release target:** v3.0 — Living Frontier  
**Operating model:** GitHub-first development, one milestone at a time; user pulls the current main branch when desired.

**v2.4 and v2.5 are implemented and Linux-CI tested.** v2.6–v3.0 remain planned. The audio engine is prepared; actual recordings and music playback are planned as an early v2.6 sprint.

## Timeline / dependency map

```text
v2.3 Frontier Justice (implemented)
       │
       ▼
v2.4 Living Law (IMPLEMENTED)        #8
  surrender • patrols • jails
       │
       ▼
v2.5 Working Frontier (IMPLEMENTED)  #9
  paid jobs • daily stock • ledgers • audio hooks
       │
       ▼
v2.6 Roads & Consequences           #10
  encounters • escorts • reputation
  + early audio sprint: sound and original music #15
       │
       ▼
v2.7 Handcrafted Frontier           #11
  landmarks • interiors • regional quests
       │
       ▼
v2.8 Combat & Character Progression #12
  weapons • morale • upgrades
       │
       ▼
v2.9 Presentation & Reliability     #13
  UI • accessibility • optimization • save stability
       │
       ▼
v3.0 Living Frontier Release        #14
  comprehensive verification • release packaging
```

## Milestone map

| Version | Milestone | Main outcome | GitHub tracker |
|---|---|---|---|
| 2.4 | Living Law — implemented | Outlaws surrender; law patrols roads; prisoners appear in jail | [#8](https://github.com/nuentoter/dust-and-debt/issues/8) |
| 2.5 | Working Frontier — implemented | Repeatable lawful jobs, daily shop stock, accounting, horse care and audio architecture | [#9](https://github.com/nuentoter/dust-and-debt/issues/9) |
| 2.6 | Roads and Consequences | Road encounters, escorts, meaningful reputation; [early original audio sprint #15](https://github.com/nuentoter/dust-and-debt/issues/15) | [#10](https://github.com/nuentoter/dust-and-debt/issues/10) |
| 2.7 | Handcrafted Frontier | Landmark variety, improved interiors, regional quest arcs | [#11](https://github.com/nuentoter/dust-and-debt/issues/11) |
| 2.8 | Combat and Character Progression | Weapon depth, enemy morale, earned upgrades, difficulty options | [#12](https://github.com/nuentoter/dust-and-debt/issues/12) |
| 2.9 | Presentation and Reliability | Settings, polish, accessibility, profiling, current-version save reliability | [#13](https://github.com/nuentoter/dust-and-debt/issues/13) |
| 3.0 | Living Frontier Release | Integrated testing, documentation and a verified source release | [#14](https://github.com/nuentoter/dust-and-debt/issues/14) |

## Milestone priorities

**First: make arresting people matter.** Version 2.4 builds on 2.2/2.3 lasso mechanics rather than discarding them. Outlaws should have a chance to surrender when injured or outmatched; sheriffs and deputies should patrol outside the starting town; arrested criminals should visibly occupy jail cells. These changes must not introduce new story softlocks or confusing **E** versus **Shift+E** prompts.

**Second: put life into towns.** Version 2.5 adds repeatable honest work, a small trade economy and audio integration hooks. Versions 2.6–2.7 add meaningful road encounters, deeper settlements and multi-location story content. Actual music and recorded SFX are planned for an [early v2.6 audio sprint](https://github.com/nuentoter/dust-and-debt/issues/15). The existing 19,200×12,800 frontier must remain camera-local and lightweight; do not solve the art problem by loading a giant full-map bitmap.

**Third: improve the feel and finish.** Versions 2.8–3.0 focus on deeper gunfights, progression, UX, save reliability, low-spec optimization, release packaging and a substantial integration test pass.

## Non-negotiable engineering rules

1. **Preserve player progress.** Save compatibility with earlier builds is **not required** during active development. Save formats may reset between milestones; document intentional resets and keep current-version save validation, corruption detection, and backups.
2. **Protect the original storyline.** Sheriff Bell, original main missions and their triggers must remain playable. New surrender/lasso systems must not softlock mission targets.
3. **Keep performance suitable for older Intel graphics and low-RAM Linux systems.** Tkinter, X11 and the current low-dependency Python architecture remain the baseline unless explicitly agreed otherwise.
4. **Never spawn mission enemies inside solid objects.** Extend tests to include patrol positions, arrest delivery, escort paths and scripted encounters.
5. **Avoid immediate bandit aggression in safe settlements.** Keep first-time onboarding protection.
6. **Commit and verify each milestone.** Extend `.github/workflows/linux-tests.yml`, and ensure the full GitHub Actions run is green before calling the milestone delivered.
7. **Make controls self-explanatory.** The F1 help, on-screen prompts and README must agree. Ordinary **E** interacts/talks; **Shift+E** enters buildings.
8. **Distinguish CI from real-world playtesting.** Tests under Xvfb are necessary, but they do not prove performance or presentation on a specific Archcraft installation.

## Release gates

Each milestone should be considered complete only after its issue checklist is satisfied, feature-specific regression tests are added, all existing automated tests pass, and any known limitations are documented. For **v3.0**, additionally require a full deterministic main-campaign/side-job completion check, a current-version save integrity audit, documented performance observations when hardware is available, release notes, and a verified source archive. Do not advertise binary packaging until a runnable binary actually exists.

## Next implementation

**Next: [v2.6 — Roads and Consequences](https://github.com/nuentoter/dust-and-debt/issues/10), with [Audio Sprint #15](https://github.com/nuentoter/dust-and-debt/issues/15) in the early sequence.** Build varied encounters and escorts, select an optional playback backend, and add original SFX/music when correctly licensed and tested.
