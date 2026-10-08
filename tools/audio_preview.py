#!/usr/bin/env python3
"""audio_preview.py - renders the NIGHTFALL music tracks to WAV files (assets/audio/*.wav).

A small software model of the GBA PSG (2 square channels + wave + noise) driven by the very same
pattern data as the game (tools/gen_audio.py), so the music can be auditioned without hardware.
It is an approximation (no sweep, simplified envelopes) meant for previews only.
"""
import os
import random
import struct
import sys
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_audio as GA   # noqa: E402

RATE = 22050


def hz(n):
    return GA.midi_hz(24 + n - 1)       # table index 1 == C1 == MIDI 24


def render(name, loops=2):
    t = GA.TRACKS[name]
    step_s = 15.0 / t['bpm']
    spf = int(step_s * RATE)
    n = spf * 64 * loops
    out = [0.0] * n
    rnd = random.Random(7)
    inst = {'MENU': (0.30, 3.0), 'GAME': (0.4, 5.0), 'INTENSE': (0.45, 9.0), 'GAMEOVER': (0.3, 2.0)}[name]
    for lp in range(loops):
        for s in range(64):
            base = (lp * 64 + s) * spf
            # lead: square 50 % with decaying amplitude
            nl = t['lead'][s]
            if nl not in (0, 255):
                f = hz(nl)
                for i in range(spf):
                    ph = ((base + i) * f / RATE) % 1.0
                    # find note length by scanning ahead
                    out[base + i] += inst[0] * (1 if ph < 0.5 else -1) * max(0.0, 1.0 - i / (spf * (inst[1] / 2.0 + 1)))
            elif nl == 255:
                # held: continue previous note
                j = s - 1
                while j >= 0 and t['lead'][j] == 255:
                    j -= 1
                if j >= 0 and t['lead'][j] != 0:
                    f = hz(t['lead'][j])
                    for i in range(spf):
                        ph = ((base + i) * f / RATE) % 1.0
                        out[base + i] += inst[0] * 0.6 * (1 if ph < 0.5 else -1)
            nb = t['bass'][s]
            src = nb
            if nb == 255:
                j = s - 1
                while j >= 0 and t['bass'][j] == 255:
                    j -= 1
                src = t['bass'][j] if j >= 0 else 0
            if src not in (0, 255):
                f = hz(src)
                for i in range(spf):
                    ph = ((base + i) * f / RATE) % 1.0
                    tri = 2 * ph if ph < 0.5 else 2 - 2 * ph
                    out[base + i] += 0.5 * (0.55 * (tri * 2 - 1) + 0.45 * (ph * 2 - 1))
            d = t['drums'][s]
            if d:
                ln = {1: 0.12, 2: 0.10, 3: 0.03, 4: 0.12, 5: 0.15}[d]
                amp = {1: 0.9, 2: 0.6, 3: 0.25, 4: 0.3, 5: 0.6}[d]
                hold = {1: 40, 2: 4, 3: 1, 4: 2, 5: 12}[d]
                v = 0.0
                for i in range(int(ln * RATE)):
                    if i % hold == 0:
                        v = rnd.choice((-1, 1))
                    if base + i < n:
                        out[base + i] += amp * v * (1 - i / (ln * RATE))
    peak = max(abs(x) for x in out) or 1
    return [int(max(-1, min(1, x / peak * 0.8)) * 32767) for x in out]


def main():
    d = os.path.join(os.path.dirname(HERE), 'assets', 'audio')
    os.makedirs(d, exist_ok=True)
    for name in GA.TRACKS:
        pcm = render(name, 1)
        with wave.open(os.path.join(d, 'music_%s.wav' % name.lower()), 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
            w.writeframes(struct.pack('<%dh' % len(pcm), *pcm))
        print('rendered', name, len(pcm) / RATE, 's')


if __name__ == '__main__':
    main()
