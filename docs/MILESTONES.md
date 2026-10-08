# Development log

Each milestone was built, run in mGBA and checked before moving on. The repository compiled
(`-Wall -Wextra`, zero warnings) at every checkpoint.

## M1 – Bootable ROM, toolchain, title screen
* Own `crt0.s`, linker script (`gba.ld`), hardware header (`include/gba.h`), header-checksum tool.
* Procedural pixel-art pipeline (`tools/`), 8×8 tile sheets, fonts, logo, title screen with animated gears/conveyor.
* Verified: boots in mGBA, title/menus navigate, first-boot controls screen.

## M2 – Vertical slice
* Player movement + smooth camera, tile collision, enemies with flow-field navigation, auto-aim shooting,
  bullet pool, wave system, points, HUD, game over, restart.
* Verified with scripted input: shooting consumes ammo, hits score, waves progress, death → SYSTEM FAILURE → TRY AGAIN.

## M3 – Full game content
* BLACKSITE 13 (9 rooms, loops, 7 doors, generator, 5 perk machines, 5 weapon racks, 7 terminals, 41 spawn points).
* 6 weapons, 5 enemy types (+elite variants), 5 power-ups, melee, pickups, perks, lighting/power mechanic, minimap.
* Verified: door purchase prompts/prices, generator activation (lights + machines), perk and weapon purchases, ammo refill.

## M4 – Menus, saves, debug
* Pause / status / options / controls / high scores / game over, SRAM save abstraction, debug overlay + cheats,
  cycle profiler, self-playing BOT build.
* Verified: all screens, save fallback, cheats, L+R death test.

## M5 – Audio, polish, performance
* PSG effects + sequenced music (menu / game / intense / game over + low-health heartbeat), captured and spectrum-checked.
* ROM wait states + prefetch, hot code in IWRAM, aligned DMA/LDM buffers, straggler failsafe.
* Soak test: BOT build to wave 500+ at 59/60 FPS with ~30 zombies; worst frame ≈ 150–180 k of 280 k cycles.

## Known limitations / ideas
* No Nintendo boot logo in the repo (run `gbafix`).
* Revive / downed state and multiplayer are designed for (player state machine, data-driven interactions) but not implemented.
* Music is rendered to WAV only approximately by `audio_preview.py`; the real thing is the GBA PSG.
