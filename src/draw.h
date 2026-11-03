/* SPDX-License-Identifier: MIT */

#pragma once

#include <stdint.h>

/* Portrait coordinates; native framebuffer is landscape, MSB-first 1bpp.
 * Pass pixel data only, without LVGL's two 32-bit palette entries. */
#define SPACETIME_WIDTH 68
#define SPACETIME_HEIGHT 160
#define SPACETIME_NATIVE_WIDTH 160
#define SPACETIME_NATIVE_HEIGHT 68
#define SPACETIME_BUFFER_SIZE (SPACETIME_NATIVE_HEIGHT * (SPACETIME_NATIVE_WIDTH / 8))
#define SPACETIME_WPM_SAMPLES 14
#define SPACETIME_CHART_MAX_WPM 160

enum spacetime_output {
    SPACETIME_USB,
    SPACETIME_BLE_CONNECTED,
    SPACETIME_BLE_DISCONNECTED,
    SPACETIME_BLE_OPEN,
};

void spacetime_draw_art(uint8_t *pixels);
void spacetime_draw_battery(uint8_t *pixels, uint8_t level);
void spacetime_draw_output(uint8_t *pixels, enum spacetime_output output);
void spacetime_draw_footer(uint8_t *pixels, uint8_t profile,
                           const uint8_t history[SPACETIME_WPM_SAMPLES]);
