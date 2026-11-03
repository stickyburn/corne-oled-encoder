# Corne OLED + Encoder — Colemak

Personal ZMK configuration for a **Keebart Corne Choc Pro BT, six columns**:
Sharp MiP display on the left; regular extra key above a rotary encoder on
the right. Despite this repository's name, this display is an LCD, not an OLED.

**Not for a nice!nano Corne, the five-column Mini, or another manufacturer's
Corne.** Those boards use different hardware definitions and firmware.

## Your layout, preserved

The original key positions and functions on all four layers are ported from
[`stickyburn/corne-config-zmk` at `559dd24`](https://github.com/stickyburn/corne-config-zmk/tree/559dd24e8be863bfb6e5eb777f6d7c57daafb828).
System now groups all five Bluetooth profiles on **Z/X/C/V/B**, with explicit
output preference on **Left Alt (USB) / A (Bluetooth)**. Two formerly unused
positions control RGB: **G toggles on/off; D cycles lighting modes**.
Colemak, Symbols and Brackets retain their original bindings.
Keebart's four extra matrix positions are inserted between the halves on the
top two rows; the two covered by the left display are disabled.

| Layer | Access from Colemak | Contents |
| --- | --- | --- |
| 0 Colemak | Default | Your Colemak, autoshift, and thumb bindings |
| 1 System | Hold outer bottom-right key | Bluetooth profiles 0–4, USB/Bluetooth preference, F-keys, brightness, volume and RGB |
| 2 Symbols | Hold right Space thumb | Numbers, symbols and navigation |
| 3 Brackets | Hold outer right thumb | Numbers, paired brackets and navigation |
| 4 Maintenance | Hold extra play/pause key + outer right thumb together | Reboot, bootloader, Studio unlock and other setup controls |

Most custom `htp` bindings are **autoshift**, not conventional home-row mods:
tap `Q` for `q`, hold for 250 ms for `Q`. The Control/Backspace thumb taps
Backspace and holds Control. Comma still holds semicolon. These are your
existing choices, not new defaults. Use a US/QWERTY host input source: ZMK
itself supplies Colemak; selecting host Colemak as well remaps it twice.

### New controls

- Turn the right encoder: volume down/up on every layer.
- Press the encoder: mute.
- Press the regular key above it: play/pause.

Only the fitted lower-right encoder is enabled. Its direction follows
Keebart's default volume mapping and must be confirmed on the physical board.
If turning clockwise lowers volume, swap its two keycodes in `sensor-bindings`.
The firmware keeps the vendor's four sensor slots; unused slots are harmless.

### Lighting — two keybinds

Hold your usual **System-layer key** (the outer bottom-right non-thumb key):

- Tap **G** on the left: RGB on/off.
- Tap **D** on the left: next lighting mode.

The modes cycle **solid → breathing → color cycling → rainbow swirl** and
repeat. RGB defaults to **on with rainbow swirl** on both halves. Solid and
breathing use blue as their default hue; rainbow/color-cycling cover the hue
range automatically. RGB turns off after five minutes idle and returns on
activity. Expect substantially shorter wireless battery life with LEDs on.

RGB choices are saved after about a minute and survive restarts/flashes.
Saved settings override compiled defaults: if an older setting persists,
toggle on with System+G and cycle with System+D to rainbow; no full reset is
needed. These controls act on both halves. No new RGB combo is required.

The left Sharp MiP LCD has no software brightness/contrast control. Its
driver returns unsupported for both operations; perceived contrast can depend
on lighting and viewing angle. A display that still looks washed out should
be investigated rather than "fixed" with an unrelated brightness setting.

### Devices and output

Hold the same **System-layer key** and use these normal Colemak positions:

| Key | Action |
| --- | --- |
| Z / X / C / V / B | Select Bluetooth profile 0 / 1 / 2 / 3 / 4 |
| Left Shift | Clear the selected host pairing, not all settings |
| Left Alt | Prefer USB output |
| A | Prefer Bluetooth output |

Selecting a Bluetooth profile chooses the host slot; output preference chooses
whether typing goes over USB or Bluetooth when those connections are available.
For example, use System+A to type over Bluetooth while the USB cable charges
the keyboard. These bindings do not change normal-layer Alt or A.

### Maintenance layer (recovery/setup only)

Press the **extra play/pause key and outer right thumb within 50 ms**, then
keep both held. Press one of these physical Colemak positions:

| Key position | Action |
| --- | --- |
| Q | Reboot the left/central half; does not erase settings |
| W | Enter the left half's USB bootloader; does not erase settings |
| F | Unlock ZMK Studio |
| J | Reboot the right half; does not erase settings |
| L | Enter the right half's USB bootloader; does not erase settings |

Release the combo to leave Maintenance. Reset/bootloader behaviors target
the half containing the **physical key you press**: Q/W are on the left,
J/L on the right. The halves must be paired and connected for the right-side
bindings to work. Plug USB into the half you are flashing, and use its matching
UF2. If the halves cannot communicate, use that half's physical double-reset
button instead. No custom driver is needed; this is
[native ZMK behavior](https://github.com/zmkfirmware/zmk/blob/edf5c0814fd3ea202e43aad2d68fd32e882a518c/docs/docs/keymaps/behaviors/reset.md).
A destructive full settings wipe is deliberately **not** assigned to a key.

## Build and download

Every push or pull request runs
[GitHub Actions](https://github.com/stickyburn/corne-oled-encoder/actions).
Download the successful run's **firmware** artifact and extract it. It contains:

| File | Purpose |
| --- | --- |
| `corne-oled-encoder-left.uf2` | Normal left firmware, display and USB ZMK Studio |
| `corne-oled-encoder-right.uf2` | Normal right firmware, encoder, no display |
| `settings-reset-left.uf2` | Temporary left settings-wipe firmware |
| `settings-reset-right.uf2` | Temporary right settings-wipe firmware |

Do not mix files from different builds, swap sides, or use the old nice!nano
UF2 files. Locally downloaded binaries live under ignored `firmware/`, not in
source control. Regression checks: `python3 -m unittest discover -s tests -v`.

Initial verification (2026-11-02): **35 source checks passed** and
[all four firmware builds passed at `4303d09`](https://github.com/stickyburn/corne-oled-encoder/actions/runs/41464608580).
The build logs confirm the custom keymap and per-half overlays, left display
and WPM graph, right display disabled, and both reset images with Studio
disabled. All four downloaded UF2s were checked for the nRF52840 family and
application-only flash addresses. In Keymap Editor's Clipboard mode, the
actual source/JSON loaded successfully with 46 keys, all five layers, sensor
bindings and the maintenance combo. This checks editor parsing/rendering, not
GitHub OAuth authorization or physical keyboard behavior.

The original-binding fixture intentionally detects layout changes. If you
later change those keys deliberately, update the corresponding test fixture;
a successful source test is not a replacement for compiling and testing keys.

## First installation — Linux or macOS

No special flashing application or Mac is required. Each half's UF2 bootloader
appears as a USB drive. **Bluetooth cannot flash these UF2s.** Keep another
keyboard connected while installing.

1. Connect the **right half** directly with a USB data cable. Its recessed
   reset button is on the **underside next to one of the four screws**.
   Keebart's [model-specific guide](https://www.keebart.com/downloads/corne-choc-pro-bt-guide.pdf)
   says to double-press it gently with a SIM-eject tool; a **KEEBART** drive
   should appear. This is not the side power switch and does not erase settings.
   Inspect the mounted drive's `INFO_UF2.TXT`
   to confirm this is the intended nRF52840 keyboard, not another USB device.
2. Copy **only** `corne-oled-encoder-right.uf2` to that drive. Wait for the
   copy to finish and the half to reboot; the drive normally disappears.
3. Repeat on the **left half**, using `corne-oled-encoder-left.uf2`.
4. Power both halves, let them connect, and connect the left half to the host.
   Its Bluetooth name remains **Corne Choc BT**.
5. Verify Colemak, all layer keys, tap/hold behavior, the left graph, both
   extra right controls, and encoder rotation in both directions.

On Linux, use the file manager and wait for the copy to finish (or `sync`
before unplugging). On macOS, use Finder. A drive disappearing or a resulting
"disk not ejected properly" message can be normal when the bootloader reboots;
confirm the keyboard works rather than assuming every copy error is benign.

### Do I need to reset first?

**No, not by default.** Normal flashing usually preserves Bluetooth bonds.
If a previous ZMK Studio keymap still takes precedence, connect the left half
by USB to [ZMK Studio](https://zmk.studio/), unlock it, and use **Restore Stock
Settings** to load this firmware's compiled keymap. This is different from a
full Bluetooth/settings wipe.

If the halves fail to pair, stored settings are incompatible, or you want a
clean start:

1. Flash `settings-reset-right.uf2` to the right half and let it boot for a few
   seconds. Re-enter its bootloader and flash normal right firmware.
2. Do the same on the left with `settings-reset-left.uf2`, then normal left
   firmware. Reset **both** halves when clearing split pairing.
3. Forget/remove the keyboard's old pairing on each affected host, power both
   halves, select the desired profile, and pair again.

Reset firmware erases stored bonds/settings; it is not usable keyboard
firmware. Never leave it installed. `BT_CLR` on your System layer clears the
selected **host profile**, not both halves or all settings.

## Editing

### Nick Coutsos's Keymap Editor — primary workflow

Open [Keymap Editor](https://nickcoutsos.github.io/keymap-editor/), authorize this
repository, and select `config/corne_choc_pro.keymap`. Its matching JSON gives
the 46-position geometry and encoder metadata. Two left positions appear in
the geometry but are physically covered by the display: leave them `&none`.
Save/commit, wait for a successful build, download, and flash matching halves.

### ZMK Studio — optional live editing

Use a Web Serial-capable browser, connect the **left half by USB**, and use
the maintenance unlock key. Studio changes are saved on the keyboard; they
**do not update GitHub source**. A saved runtime keymap may survive later
flashes. Restore Stock Settings when you want the compiled source defaults.
The source/editor workflow is the source of truth for this repository.

## Versions and hardware support

The initial port pins both ZMK and the reusable build workflow to upstream
**v0.3.0** (`edf5c0814fd3ea202e43aad2d68fd32e882a518c`), the latest formal
release found during the 2026-11-02 audit. It is also the version supported
by Keebart's documented `main` configuration.

Keebart's board definitions and Sharp MiP graph code are loaded as a west
module pinned to `98c5a1181ff7db1f480f684f714126922d55b8f0` (2026-10-14).
They are not copied or reinvented here. See `config/west.yml` for both pins.
This is a **vendor-supported stable baseline**, not a claim to run the newest
development ZMK commit. Keebart's older board definitions cannot simply use
the new Zephyr board naming without a coordinated migration.

The connected keyboard's read-only Bluetooth Device Information reports
manufacturer **ZMK Project** and model **Corne Choc BT**. It does not expose a
firmware revision characteristic, so its exact installed version and any
saved runtime keymap were not inferred from its name.

The right half was subsequently inspected over USB: `INFO_UF2.TXT` identifies
`keebart_nrf52840`, bootloader dated 2025-02-27, SoftDevice S140 6.1.1. Every
application block in its stock UF2 matches the vendor's downloaded right-side
image. Local-only pre-flash snapshots live in ignored
`firmware/original-device/`; do not publish those dumps, as they may contain
pairing/settings data.

Keebart also publishes a newer `keebart-studio` branch (Oct 31, vendor Studio
v0.4). This is a separate **beta editor/runtime**, not upstream ZMK v0.4: it
still uses ZMK v0.3 and replaces ordinary `.keymap` bindings. Its hardware
definitions are identical to the pinned conventional branch. This port
deliberately keeps the conventional source-keymap workflow you already use.

Miryoku is an alternative compact keymap **on top of ZMK**, not smaller ZMK
firmware. Choosing it would replace your layout, so this port does not use it.

Power policy: 30-minute deep sleep, left display/typing graph enabled, no
right display, RGB defaulting to on with rainbow swirl (previously saved
RGB settings can survive flashing), and automatic RGB off while idle. This preserves
your original sleep interval without carrying over the old board's forced
maximum Bluetooth transmit power.

## Recovery sources

The [Keebart product page](https://www.keebart.com/products/corne-wireless)
offers stock six-column firmware for returning to the vendor layout:

- [Stock left UF2](https://www.keebart.com/firmware/corne_bt/corne_choc_pro_bt_left-zmk.uf2)
- [Stock right UF2](https://www.keebart.com/firmware/corne_bt/corne_choc_pro_bt_right-zmk.uf2)
- [Vendor hardware/display source](https://github.com/Keebart/zmk-config)
- [ZMK flashing documentation](https://zmk.dev/docs/user-setup#installing-the-firmware)

Stock downloads are not a backup of any custom runtime edits currently saved
on your keyboard. Export or record those separately before restoring stock.
