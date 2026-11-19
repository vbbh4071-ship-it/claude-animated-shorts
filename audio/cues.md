# The Train That Left Before It Arrived - soundtrack cue sheet

All sound is original: synthesized in numpy/scipy by `sfx_gen.py` / `instruments.py`, placed by `sfx.py` / `music.py`, mixed by `mix.py`.
Voice = `voice/voice.wav`, gain only (no EQ, no compression, no pitch).

## Files
| file | content |
|---|---|
| `mix.wav` | final mix, 48 kHz, stereo, 24-bit, 2,880,000 samples = 60.000 s |
| `stem_voice.wav` / `stem_music.wav` / `stem_sfx.wav` | stems at mix gain (they sum to the mix before the master limiter) |

## Master loudness (own BS.1770-4 meter)
- Integrated **-15.0 LUFS**, true peak **-1.2 dBTP**, LRA 1.2 LU, max momentary -12.2 LUFS, max short-term -14.1 LUFS
- Stems: voice -15.3 LUFS, music -26.0 LUFS, sfx -28.3 LUFS (voice gain +2.56 dB, same gain on every stem)
- Master limiter (4x oversampled look-ahead, ceiling -1.2 dBTP): max gain reduction 2.64 dB, active (>0.1 dB) on 17.34 % of samples, >0.5 dB on 5.35 %

ffmpeg ebur128 cross-check:
```
Summary:
  Integrated loudness:
    I:         -15.0 LUFS
    Threshold: -25.0 LUFS
  Loudness range:
    LRA:         1.2 LU
    Threshold: -35.0 LUFS
    LRA low:   -15.6 LUFS
    LRA high:  -14.5 LUFS
  True peak:
    Peak:       -1.2 dBFS
```

## Voice on top: per-section loudness (LUFS, integrated per stem, at mix gain)
bed = music + sfx. margin = voice - bed (integrated over the section). speech median / p10 = median and 10th percentile of the 400 ms momentary margin (voice - bed) over windows centred on spoken words.

| section (shots) | time s | voice | music | sfx | bed | margin LU | speech median LU | speech p10 LU |
|---|---|---|---|---|---|---|---|---|
| hook (1) | 0.00-4.33 | -15.1 | -24.8 | -30.0 | -24.2 | 9.1 | 9.2 | 5.9 |
| town (2) | 4.33-10.00 | -15.2 | -25.7 | -28.2 | -24.0 | 8.7 | 9.9 | 3.9 |
| march (3-4) | 10.00-21.33 | -15.4 | -24.9 | -26.8 | -22.7 | 7.3 | 7.4 | 4.8 |
| confusion (5-7) | 21.33-37.33 | -15.7 | -27.8 | -27.3 | -24.5 | 8.8 | 8.9 | 5.1 |
| pivot (8) | 37.33-42.67 | -14.8 | -25.9 | -32.0 | -24.9 | 10.1 | 10.0 | 8.1 |
| analogy (9) | 42.67-48.00 | -15.0 | -25.4 | -31.8 | -24.6 | 9.6 | 9.7 | 5.2 |
| consequence (10) | 48.00-54.00 | -14.9 | -26.4 | -31.8 | -28.4 | 13.4 | 14.1 | 9.1 |
| callback (11) | 54.00-60.00 | -15.5 | -26.4 | -43.2 | -26.4 | 10.8 | 11.2 | 7.4 |

## Music map (original march, Bb major, 120 bpm: quarter note = train wheel click)
Music target per section, LU under the voice (after a -3 dB speech duck keyed from words.json): hook -9.5, town -10.5, march -10.0, confusion -10.0, pivot -12.0, analogy -11.5, consequence -10.5, callback -11.0. Applied section gains (dB): hook -7.9, town -5.1, march -7.7, confusion -8.0, pivot -7.3, analogy -7.7, consequence -6.1, callback -8.0.

Rides (music only, dB): 3.65-4.30 s -3.0, 23.50-24.20 s -2.0, 51.00-51.90 s -3.0 - so quiet sentence-final words stay on top and the band blooms in the gaps after them.

| time s | frame | music |
|---|---|---|
| 0.00 | 0 | hook: whistle fanfare theme A1-A2, tuba/snare/cymbal |
| 4.33 | 130 | band cut exactly on the white flash (frame 130) |
| 5.00 | 150 | town: theme A1-A2 light (glock + fife, tuba on 1/3) |
| 9.00 | 270 | town: full band theme A3-A8 (cymbal) |
| 10.00 | 300 | vamp bar, no melody: room for timetables confusion |
| 16.00 | 480 | confusion: F7 pedal, chromatic climb, snare drive |
| 24.00 | 720 | build-up to pivot - roll into silence |
| 24.00 | 720 | pivot: warm pad Bb-Eb/Bb-Bb-F7-Bb, vibes, 'You see, sun time moves west' |
| 32.00 | 960 | analogy: music-box waltz, 'Imagine you're on that train' |
| 40.00 | 1200 | consequence: march returns, four standard time zones |
| 52.00 | 1560 | callback: relaxed swung ending, 'every train leaves after it arrives' |

## SFX events
Level convention: every EVENT has a naive level (LU vs the voice stem, as the event's max momentary loudness); applied = naive - 6 dB (standard mix rule) + distance/intensity offsets. BEDS are integrated loudness, not reduced. 'mix LUFS' = the event's max momentary loudness in the final mix (voice stem = -15.3 LUFS integrated). Train sounds also get the camera-distance low-pass and more station reverb.

| # | time s | frame | cue | what | naive LU | applied LU | mix LUFS | pan |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 0.0 | amb_station (bed, integrated) | station platform air: breeze, distant river, sparrows, platform murmur (all shots) | -30 | -30.0 | -45.3 | +0.00 |
| 2 | 0.500 | 15.0 | train_whistle_hook | long lonesome train whistle, distant, echoing off the station (hook) | -8 | -14.0 | -29.3 | -0.25 |
| 3 | 3.800 | 114.0 | train_whistle_button | short whistle button exactly on the white flash (frame 130) | -6 | -12.0 | -27.3 | -0.20 |
| 4 | 4.330 | 129.9 | platform_murmur | station platform: crowd murmur ~18 voices, distant town hubbub (shot 2 onwards) | -10 | -16.0 | -31.4 | +0.00 |
| 5 | 4.333 | 130.0 | whoosh_cam | camera white flash cut | -11 | -17.0 | -32.3 | +0.00 |
| 6 | 4.333 | 130.0 | whoosh_xfade | crossfade town -> timetables | -12 | -18.0 | -33.3 | +0.00 |
| 7 | 5.010 | 150.3 | platform_step | passenger footstep on the station platform | -9 | -23.0 | -38.5 | -0.36 |
| 8 | 6.293 | 188.8 | platform_step | passenger footstep on the station platform | -9 | -23.0 | -38.6 | +0.10 |
| 9 | 7.000 | 210.0 | train_chug_near | train chugging rhythm, close on the platform, wheels clicking rails | -5 | -11.0 | -26.3 | +0.10 |
| 10 | 7.601 | 228.0 | platform_step | passenger footstep on the station platform | -9 | -23.0 | -38.6 | -0.47 |
| 11 | 8.811 | 264.3 | platform_step | passenger footstep on the station platform | -9 | -23.0 | -38.4 | +0.15 |
| 12 | 9.500 | 285.0 | clock_chimes_cleveland | Cleveland town hall clock striking eleven (train departure) | -4 | -10.0 | -25.3 | -0.30 |
| 13 | 10.000 | 300.0 | whoosh_cam | camera cut to timetables | -11 | -17.0 | -32.3 | +0.00 |
| 14 | 10.191 | 305.7 | platform_step | passenger footstep on the station platform | -9 | -18.6 | -33.9 | +0.32 |
| 15 | 11.220 | 336.6 | platform_step | passenger footstep on the station platform | -9 | -18.6 | -33.9 | +0.27 |
| 16 | 12.553 | 376.6 | platform_step | passenger footstep on the station platform | -9 | -15.0 | -30.3 | +0.14 |
| 17 | 13.788 | 413.6 | platform_step | passenger footstep on the station platform | -9 | -15.0 | -30.3 | +0.17 |
| 18 | 14.500 | 435.0 | ticket_punch | conductor punches tickets: sharp clip-clop along the carriage | -10 | -16.0 | -31.3 | +0.00 |
| 19 | 15.177 | 455.3 | platform_step | passenger footstep on the station platform | -9 | -15.0 | -30.3 | -0.24 |
| 20 | 15.333 | 460.0 | whoosh_cam | camera train leaves station | -11 | -17.0 | -32.3 | +0.00 |
| 21 | 15.333 | 460.0 | whoosh_xfade | crossfade leave -> arrive | -12 | -18.0 | -33.3 | +0.00 |
| 22 | 16.197 | 485.9 | platform_step | passenger footstep on the station platform | -9 | -22.2 | -37.6 | +0.05 |
| 23 | 17.605 | 528.2 | platform_step | passenger footstep on the station platform | -9 | -19.9 | -35.2 | +0.26 |
| 24 | 18.651 | 559.5 | platform_step | passenger footstep on the station platform | -9 | -19.9 | -35.2 | +0.35 |
| 25 | 19.829 | 594.9 | platform_step | passenger footstep on the station platform | -9 | -19.9 | -35.2 | -0.00 |
| 26 | 20.000 | 600.0 | departure_bell | station departure bell: brass 'ding-ding', train about to leave | -6 | -12.0 | -27.3 | +0.00 |
| 27 | 21.248 | 637.5 | platform_step | passenger footstep on the station platform | -9 | -19.9 | -35.2 | -0.02 |
| 28 | 21.333 | 640.0 | whoosh_cam | camera train arrives early | -11 | -17.0 | -32.3 | +0.00 |
| 29 | 22.676 | 680.3 | platform_step | passenger footstep on the station platform | -9 | -15.5 | -30.8 | -0.05 |
| 30 | 23.797 | 713.9 | platform_step | passenger footstep on the station platform | -9 | -15.5 | -30.8 | +0.36 |
| 31 | 24.000 | 720.0 | clock_chimes_pittsburgh | Pittsburgh town hall clock striking eleven-eleven (impossible arrival) | -4 | -10.0 | -25.3 | +0.30 |
| 32 | 25.125 | 753.7 | platform_step | passenger footstep on the station platform | -9 | -15.5 | -30.8 | -0.28 |
| 33 | 26.301 | 789.0 | platform_step | passenger footstep on the station platform | -9 | -15.5 | -30.8 | -0.06 |
| 34 | 27.333 | 820.0 | whoosh_cam | camera confused passengers | -11 | -17.0 | -32.3 | +0.00 |
| 35 | 27.628 | 828.8 | platform_step | passenger footstep on the station platform | -9 | -19.1 | -34.4 | +0.40 |
| 36 | 28.000 | 840.0 | train_chug_depart | train pulling away, chugging fading into distance | -7 | -13.0 | -28.3 | +0.20 |
| 37 | 28.588 | 857.6 | platform_step | passenger footstep on the station platform | -9 | -19.1 | -34.4 | +0.40 |
| 38 | 30.106 | 903.2 | platform_step | passenger footstep on the station platform | -9 | -19.1 | -34.4 | -0.00 |
| 39 | 31.400 | 942.0 | platform_step | passenger footstep on the station platform | -9 | -19.1 | -34.4 | -0.07 |
| 40 | 32.667 | 980.0 | whoosh_cam | camera wait how? | -11 | -17.0 | -32.3 | +0.00 |
| 41 | 32.695 | 980.9 | platform_step | passenger footstep on the station platform | -9 | -15.8 | -31.1 | -0.25 |
| 42 | 33.656 | 1009.7 | platform_step | passenger footstep on the station platform | -9 | -15.8 | -31.1 | +0.25 |
| 43 | 34.943 | 1048.3 | platform_step | passenger footstep on the station platform | -9 | -15.8 | -31.1 | -0.14 |
| 44 | 36.418 | 1092.5 | platform_step | passenger footstep on the station platform | -9 | -15.8 | -31.1 | +0.36 |
| 45 | 37.333 | 1120.0 | amb_golden (bed, integrated) | golden-hour calm: soft breeze, blackbird phrases, faint crickets (shots 8-9) | -29 | -29.0 | -44.3 | +0.00 |
| 46 | 37.333 | 1120.0 | whoosh_cam | camera golden-hour pivot | -11 | -17.0 | -32.3 | +0.00 |
| 47 | 37.333 | 1120.0 | whoosh_xfade | crossfade to golden | -12 | -18.0 | -33.3 | +0.00 |
| 48 | 37.458 | 1123.7 | platform_step | passenger footstep on the station platform | -9 | -23.0 | -38.5 | +0.20 |
| 49 | 38.790 | 1163.7 | platform_step | passenger footstep on the station platform | -9 | -23.0 | -38.5 | +0.37 |
| 50 | 39.825 | 1194.7 | platform_step | passenger footstep on the station platform | -9 | -23.0 | -38.5 | -0.06 |
| 51 | 41.167 | 1235.0 | platform_step | passenger footstep on the station platform | -9 | -23.0 | -38.5 | -0.04 |
| 52 | 42.510 | 1275.3 | platform_step | passenger footstep on the station platform | -9 | -23.0 | -38.4 | +0.20 |
| 53 | 42.667 | 1280.0 | whoosh_cam | camera analogy on the train | -11 | -17.0 | -32.3 | +0.00 |
| 54 | 42.667 | 1280.0 | whoosh_xfade | crossfade to analogy | -12 | -18.0 | -33.3 | +0.00 |
| 55 | 43.942 | 1318.2 | platform_step | passenger footstep on the station platform | -9 | -19.0 | -34.3 | -0.13 |
| 56 | 44.986 | 1349.6 | platform_step | passenger footstep on the station platform | -9 | -19.0 | -34.3 | +0.07 |
| 57 | 46.416 | 1392.5 | platform_step | passenger footstep on the station platform | -9 | -19.0 | -34.4 | +0.28 |
| 58 | 47.679 | 1430.4 | platform_step | passenger footstep on the station platform | -9 | -19.0 | -34.4 | -0.44 |
| 59 | 48.000 | 1440.0 | whoosh_cam | camera four time zones | -11 | -17.0 | -32.3 | +0.00 |
| 60 | 48.000 | 1440.0 | whoosh_xfade | crossfade to time zones | -12 | -18.0 | -33.3 | +0.00 |
| 61 | 48.793 | 1463.8 | platform_step | passenger footstep on the station platform | -9 | -18.0 | -33.3 | -0.05 |
| 62 | 50.167 | 1505.0 | platform_step | passenger footstep on the station platform | -9 | -18.0 | -33.3 | +0.44 |
| 63 | 51.426 | 1542.8 | platform_step | passenger footstep on the station platform | -9 | -18.0 | -33.3 | -0.39 |
| 64 | 52.448 | 1573.4 | platform_step | passenger footstep on the station platform | -9 | -18.0 | -33.3 | +0.02 |
| 65 | 53.666 | 1610.0 | platform_step | passenger footstep on the station platform | -9 | -18.0 | -33.3 | +0.44 |
| 66 | 54.000 | 1620.0 | whoosh_cam | camera tourists on rebuilt platform | -11 | -17.0 | -32.3 | +0.00 |
| 67 | 54.000 | 1620.0 | whoosh_xfade | crossfade to tourists | -12 | -18.0 | -33.3 | +0.00 |
