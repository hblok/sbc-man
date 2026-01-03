# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

package(default_visibility = ["//visibility:public"])

# Integration tests
py_test(
    name = "test_download_install_flow",
    srcs = ["test_download_install_flow.py"],
    deps = [
        "//sbcman/core",
        "//sbcman/services",
        "//sbcman/states",	
        "//tests:test_utils",
    ],
    size = "large",
)

py_test(
    name = "test_game_launch_flow",
    srcs = ["test_game_launch_flow.py"],
    deps = [
        "//sbcman/core:core",
        "//sbcman/services",
        "//sbcman/states:states",
        "//tests:test_utils",
    ],
    size = "large",

)

py_test(
    name = "test_startup_flow",
    srcs = ["test_startup_flow.py"],
    deps = [
        "//sbcman/core",
        "//sbcman/hardware",
        "//sbcman/services",
        "//sbcman/states",	
        "//tests:test_utils",
    ],
    size = "medium",
)

py_test(
    name = "test_state_transition_flow",
    srcs = ["test_state_transition_flow.py"],
    deps = [
        "//sbcman/core:core",
        "//sbcman/services",
        "//sbcman/states:states",
        "//tests:test_utils",
        "@sbc_man_pip_deps//pygame_ce",
    ],
    size = "medium",
)