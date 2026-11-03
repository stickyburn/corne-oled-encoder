# SPDX-License-Identifier: MIT

if(CONFIG_BOARD_CORNE_CHOC_PRO_LEFT AND CONFIG_SHIELD_SHARP_MIP
   AND CONFIG_ZMK_DISPLAY AND CONFIG_ZMK_DISPLAY_STATUS_SCREEN_CUSTOM
   AND NOT CONFIG_SHARP_MIP_WIDGET_STATUS)
  zephyr_library()
  zephyr_library_include_directories(${CMAKE_SOURCE_DIR}/include)
  zephyr_library_sources(src/spacetime_display.c src/draw.c)
endif()
