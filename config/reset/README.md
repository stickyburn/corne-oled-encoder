# Settings reset configuration

The `settings_reset` entries in the repository's `build.yaml` point
`ZMK_CONFIG` at this directory:

```
cmake-args: -DZMK_CONFIG=${GITHUB_WORKSPACE}/config/reset
```

This is intentional, for three reasons:

1. The per-side configuration files (`config/corne_choc_pro_left.conf`,
   `config/corne_choc_pro_right.conf`) enable the Sharp MIP display stack.
   The `settings_reset` shield compiles the display stack out and expects
   it to stay out, so the user configuration must not be merged into the
   reset firmware.
2. ZMK Studio (enabled for the normal left build) is not wanted in the
   reset firmware either; redirecting `ZMK_CONFIG` keeps the Studio cmake
   arguments and snippets scoped to the normal build matrix entries.
3. The settings reset behavior itself does not depend on this directory:
   the `settings_reset` shield supplies its own conf
   (`CONFIG_ZMK_SETTINGS_RESET_ON_START=y`, BLE and display off) and its
   own devicetree overlay (a mock kscan), which Zephyr applies regardless
   of `ZMK_CONFIG`. With this directory empty, the build falls back to the
   board-default keymap shipped inside the Keebart module.

The settings reset firmware is temporary: flash it, let it boot and clear
the stored settings, then immediately flash the normal firmware for that
half again.

This README only exists so the otherwise empty directory is kept in git.