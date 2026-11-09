# Dust & Debt — Development Roadmap: v2.4 → v3.0

**Updated:** November 9, 2026  
**Current playable source:** v2.7 — Handcrafted Frontier  
**Release target:** v3.0 — Living Frontier  
**Operating model:** GitHub-first development, one milestone at a time; user pulls the current main branch when desired.

**v2.4, v2.5, the 10× world map, v2.6 regional gameplay, the New Austellia geography, and v2.7 Handcrafted Frontier are implemented and Linux-CI tested.** Optional procedural WAV effects and background atmospheres work with ffplay/mpv. The user's actual title recording, production SFX, mixing and remaining v2.7–v3.0 features remain to be finished.

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
v2.6-map Great Territory (IMPLEMENTED) #16
  60,000×40,960 • preliminary terrain • rest stops
       │
       ▼
v2.6 Roads & Consequences (IMPLEMENTED) #10
  four road jobs • escorts • regional standing • ambushes
  + audio playback foundation (PROGRESS): SFX and ambient beds #15
       │
       ▼
New Austellia Atlas Alignment (GEOGRAPHY IMPLEMENTED) #17
  traced cities • routes • lakes • coastline • bridge collisions
  image packaging and art polish remain open
       │
       ▼
v2.7 Handcrafted Frontier (IMPLEMENTED) #11
  unique town landmarks • interiors • 2 regional stories • faster horse
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
| 2.6-map | Great Territory — implemented | 10× world area, earlier provisional terrain, zoomable atlas, local radar | [#16](https://github.com/nuentoter/dust-and-debt/issues/16) |
| 2.6 | Roads and Consequences — implemented | Four rotating road contracts, escorts, varied incidents, regional reputation and optional generated audio; [soundtrack sprint still open #15](https://github.com/nuentoter/dust-and-debt/issues/15) | [#10](https://github.com/nuentoter/dust-and-debt/issues/10) |
| 2.6-atlas | New Austellia alignment — geography implemented | 15 named illustrated regions, 30+ sites, railways, rivers, coastline and relocated frontier quests; source artwork packaging remains | [#17](https://github.com/nuentoter/dust-and-debt/issues/17) |
| 2.7 | Handcrafted Frontier — implemented | Distinct town landmarks, regional interiors, two multi-stop quests, atlas selector, 1.5× trot/2.5× gallop and stamina | [#11](https://github.com/nuentoter/dust-and-debt/issues/11) |
| 2.8 | Combat and Character Progression | Weapon depth, enemy morale, earned upgrades, difficulty options | [#12](https://github.com/nuentoter/dust-and-debt/issues/12) |
| 2.9 | Presentation and Reliability | Settings, polish, accessibility, profiling, current-version save reliability | [#13](https://github.com/nuentoter/dust-and-debt/issues/13) |
| 3.0 | Living Frontier Release | Integrated testing, documentation and a verified source release | [#14](https://github.com/nuentoter/dust-and-debt/issues/14) |

## Milestone priorities

**First: make arresting people matter.** Version 2.4 builds on 2.2/2.3 lasso mechanics rather than discarding them. Outlaws should have a chance to surrender when injured or outmatched; sheriffs and deputies should patrol outside the starting town; arrested criminals should visibly occupy jail cells. These changes must not introduce new story softlocks or confusing **E** versus **Shift+E** prompts.

**Second: settle the physical map, then populate it.** Version 2.5 adds repeatable honest work and audio hooks; the **10× Great Territory map foundation** freezes geographic names, highways, and exploration stops in [WORLD_ATLAS.md](WORLD_ATLAS.md). Version 2.6 populates distant territory with dispatchers, jobs, escorts and incidents; v2.7 adds distinct settlement landmarks, two regional questlines and faster horse traversal. Original authored title music and professionally recorded/mixed SFX are still planned in [Audio Sprint #15](https://github.com/nuentoter/dust-and-debt/issues/15); v2.6 already plays original synthesized ambient beds and effects when ffplay/mpv is available. The 60,000×40,960 Great Territory must remain camera-local and lightweight; do not solve the art problem by loading a giant full-map bitmap.

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

**Next: [v2.8 Combat & Character Progression](https://github.com/nuentoter/dust-and-debt/issues/12).** New Austellia geography and v2.7 story routes are implemented. Finish the remaining illustrated map packaging/art polish in [#17](https://github.com/nuentoter/dust-and-debt/issues/17), and investigate silent audio on the owner's Archcraft computer under [Audio Sprint #15](https://github.com/nuentoter/dust-and-debt/issues/15).
