/* SPDX-License-Identifier: MIT */

#include <zephyr/kernel.h>
#include <lvgl.h>
#include <string.h>

#include <zmk/battery.h>
#include <zmk/ble.h>
#include <zmk/display.h>
#include <zmk/endpoints.h>
#include <zmk/event_manager.h>
#include <zmk/events/battery_state_changed.h>
#include <zmk/events/ble_active_profile_changed.h>
#include <zmk/events/endpoint_changed.h>
#include <zmk/events/usb_conn_state_changed.h>
#include <zmk/events/wpm_state_changed.h>
#include <zmk/wpm.h>

#include "draw.h"

/* Indexed LVGL images start with two 32-bit palette entries. */
static struct {
    lv_color32_t palette[2];
    uint8_t pixels[SPACETIME_BUFFER_SIZE];
} image;

static lv_obj_t *canvas;
static uint8_t active_profile = 1;
static uint8_t wpm_history[SPACETIME_WPM_SAMPLES];

struct output_state {
    enum spacetime_output output;
    uint8_t profile;
};

static uint8_t battery_get_state(const zmk_event_t *eh) {
    const struct zmk_battery_state_changed *event = as_zmk_battery_state_changed(eh);
    return event ? event->state_of_charge : zmk_battery_state_of_charge();
}

static void battery_update(uint8_t level) {
    spacetime_draw_battery(image.pixels, level);
    lv_obj_invalidate(canvas);
}

ZMK_DISPLAY_WIDGET_LISTENER(spacetime_battery, uint8_t, battery_update, battery_get_state)
ZMK_SUBSCRIPTION(spacetime_battery, zmk_battery_state_changed);

static struct output_state output_get_state(const zmk_event_t *eh) {
    (void)eh;
    struct output_state state = {.output = SPACETIME_BLE_OPEN, .profile = 1};

    if (zmk_endpoints_selected().transport == ZMK_TRANSPORT_USB) {
        state.output = SPACETIME_USB;
    }

#if IS_ENABLED(CONFIG_ZMK_BLE)
    state.profile = zmk_ble_active_profile_index() + 1;
    if (state.output != SPACETIME_USB && !zmk_ble_active_profile_is_open()) {
        state.output = zmk_ble_active_profile_is_connected() ? SPACETIME_BLE_CONNECTED
                                                            : SPACETIME_BLE_DISCONNECTED;
    }
#endif

    return state;
}

static void output_update(struct output_state state) {
    spacetime_draw_output(image.pixels, state.output);
    if (active_profile != state.profile) {
        active_profile = state.profile;
        spacetime_draw_footer(image.pixels, active_profile, wpm_history);
    }
    lv_obj_invalidate(canvas);
}

ZMK_DISPLAY_WIDGET_LISTENER(spacetime_output, struct output_state, output_update, output_get_state)
ZMK_SUBSCRIPTION(spacetime_output, zmk_endpoint_changed);
#if IS_ENABLED(CONFIG_ZMK_BLE)
ZMK_SUBSCRIPTION(spacetime_output, zmk_ble_active_profile_changed);
#endif
#if IS_ENABLED(CONFIG_USB_DEVICE_STACK)
ZMK_SUBSCRIPTION(spacetime_output, zmk_usb_conn_state_changed);
#endif

static uint8_t wpm_get_state(const zmk_event_t *eh) {
    (void)eh;
    return CLAMP(zmk_wpm_get_state(), 0, UINT8_MAX);
}

static void wpm_update(uint8_t wpm) {
    if (wpm_history[SPACETIME_WPM_SAMPLES - 1] == wpm) {
        return;
    }

    /* Like the original screen, history advances only when WPM changes. */
    memmove(wpm_history, wpm_history + 1, sizeof(wpm_history) - 1);
    wpm_history[SPACETIME_WPM_SAMPLES - 1] = wpm;
    spacetime_draw_footer(image.pixels, active_profile, wpm_history);
    lv_obj_invalidate(canvas);
}

ZMK_DISPLAY_WIDGET_LISTENER(spacetime_wpm, uint8_t, wpm_update, wpm_get_state)
ZMK_SUBSCRIPTION(spacetime_wpm, zmk_wpm_state_changed);

lv_obj_t *zmk_display_status_screen(void) {
    lv_obj_t *screen = lv_obj_create(NULL);
    lv_obj_remove_style_all(screen);
    lv_obj_clear_flag(screen, LV_OBJ_FLAG_SCROLLABLE);

#if IS_ENABLED(CONFIG_SHARP_MIP_WIDGET_INVERTED)
    lv_color_t background = lv_color_white();
    lv_color_t foreground = lv_color_black();
#else
    lv_color_t background = lv_color_black();
    lv_color_t foreground = lv_color_white();
#endif

    lv_obj_set_style_bg_color(screen, background, 0);
    lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, 0);

    canvas = lv_canvas_create(screen);
    lv_obj_remove_style_all(canvas);
    lv_obj_set_pos(canvas, 0, 0);
    lv_canvas_set_buffer(canvas, &image, SPACETIME_NATIVE_WIDTH, SPACETIME_NATIVE_HEIGHT,
                         LV_IMG_CF_INDEXED_1BIT);
    lv_obj_set_size(canvas, SPACETIME_NATIVE_WIDTH, SPACETIME_NATIVE_HEIGHT);
    lv_canvas_set_palette(canvas, 0, background);
    lv_canvas_set_palette(canvas, 1, foreground);

    memset(image.pixels, 0, sizeof(image.pixels));
    spacetime_draw_art(image.pixels);
    spacetime_draw_footer(image.pixels, active_profile, wpm_history);
    spacetime_battery_init();
    spacetime_output_init();
    spacetime_wpm_init();

    return screen;
}
