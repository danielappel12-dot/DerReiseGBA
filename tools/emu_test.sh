#!/usr/bin/env bash
# Headless emulator smoke-test helper (developer tool).
#
#   tools/emu_test.sh ROM OUT_PREFIX "steps..."
#
# Steps are space separated tokens executed in order:
#   wait:SECONDS         sleep
#   shot:NAME            screenshot of the emulator window -> OUT_PREFIX_NAME.png
#   down:KEY / up:KEY    hold / release an X key (mGBA default map below)
#   tap:KEY              press+release (80 ms)
#   hold:KEY:SECONDS     hold a key for a while
#
# mGBA default keys: arrows = D-pad, x = A, z = B, a = L, s = R,
#                    Return = START, BackSpace = SELECT.
set -u
ROM=$1; PREFIX=$2; shift 2
export DISPLAY=:99
if ! xdpyinfo >/dev/null 2>&1; then
  Xvfb :99 -screen 0 1024x768x24 >/dev/null 2>&1 &
  sleep 1
fi
rm -f /tmp/mgba_test.log
SDL_AUDIODRIVER=dummy /usr/games/mgba -3 "$ROM" >/tmp/mgba_test.log 2>&1 &
EMU=$!
sleep 2
WIN=$(xdotool search --name "mGBA" 2>/dev/null | head -1)
[ -n "$WIN" ] && xdotool windowfocus "$WIN" 2>/dev/null
for step in "$@"; do
  case "$step" in
    wait:*)  sleep "${step#wait:}" ;;
    shot:*)  import -window "$WIN" "${PREFIX}_${step#shot:}.png" ;;
    down:*)  xdotool keydown "${step#down:}" ;;
    up:*)    xdotool keyup "${step#up:}" ;;
    tap:*)   xdotool keydown "${step#tap:}"; sleep 0.08; xdotool keyup "${step#tap:}" ;;
    hold:*)  k=${step#hold:}; key=${k%%:*}; secs=${k##*:}
             xdotool keydown "$key"; sleep "$secs"; xdotool keyup "$key" ;;
  esac
done
kill -9 $EMU 2>/dev/null
wait $EMU 2>/dev/null
exit 0
