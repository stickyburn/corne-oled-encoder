# Corne OLED + Encoder

ZMK configuration for the **Keebart Corne Choc Pro BT**, six-column version
with nRF52840 controllers. Left: Sharp MiP LCD (not OLED). Right: one lower
rotary encoder and a regular key above it.

## Controls

- Encoder rotation: volume. Encoder press: mute.
- Key above encoder: play/pause.
- RGB: on by default, rainbow swirl.

## Colemak layout

```text
Tab    Q W F P G  [LCD] │ [Play] J L U Y ; Esc
Alt    A R S T D  [LCD] │ [Mute] H N E I O '
Shift  Z X C V B        │        K M , . / System
    Bksp Ctrl/Bksp Enter│ Enter Space/Symbols Brackets
```

Hold letters for capitals (250 ms). The Ctrl/Bksp thumb taps Backspace and
holds Control; the Space/Symbols thumb taps Space and holds Symbols.
Use a US/QWERTY host input source—Colemak is handled by the keyboard.

## Layers

| Layer | Access | Contents |
| --- | --- | --- |
| Colemak | Default | Typing and media controls |
| System | Hold outer bottom-right non-thumb key | Bluetooth, output, F-keys, volume, computer brightness and RGB |
| Symbols | Hold Space thumb | Numbers, symbols and navigation |
| Brackets | Hold rightmost thumb | Numbers, paired brackets and navigation |
| Maintenance | Hold play/pause + rightmost thumb together | Reboot, flashing mode and Studio unlock |

**System:**
- Z/X/C/V/B: Bluetooth profiles 0–4; Left Shift: clear selected pairing.
- Left Alt: prefer USB; A: prefer Bluetooth.
- G: RGB on/off; D: cycle solid → breathing → color cycling → rainbow.
- Q/W/F/P: F1–F4; Tab/Esc: F8; semicolon: F2.
- Comma/period/slash: volume up/down/mute.
- E/I/O: computer brightness up/down/minimum.

**Maintenance:** Q/W reboot/bootloader for the left half; J/L for the right;
F unlocks [ZMK Studio](https://zmk.studio/) live editing. Both halves must be
connected for right-side commands. Plug USB into the half being flashed.
Reboot and bootloader commands do not erase settings.

## Editing and firmware

Edit `config/corne_choc_pro.keymap` directly or with
[Keymap Editor](https://nickcoutsos.github.io/keymap-editor/).
[GitHub Actions](https://github.com/stickyburn/corne-oled-encoder/actions)
builds matching left/right UF2s. Use `settings-reset-*` only for recovery,
then reinstall normal firmware. Saved Studio/RGB settings can survive flashing.
