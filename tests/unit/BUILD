# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

package(default_visibility = ["//visibility:public"])

# Unit tests
py_test(
    name = "test_config_loader",
    srcs = ["test_config_loader.py"],
    deps = [
        "//sbcman/hardware:hardware",
        "//sbcman/path:path",    
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_download_manager",
    srcs = ["test_download_manager.py"],
    deps = [
        "//sbcman/models:models",
        "//sbcman/services:services",
        "//services:services",
        "//tests:test_utils",
    ],
    size = "medium",
)

py_test(
    name = "test_download_state",
    srcs = ["test_download_state.py"],
    deps = [
        "//sbcman/models:models",
        "//sbcman/states:states",
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_input_handler",
    srcs = ["test_input_handler.py"],
    deps = [
        "//sbcman/models",
        "//sbcman/services",	
        "//tests:test_utils",
        "@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_network_service",
    srcs = ["test_network_service.py"],
    deps = [
        "//sbcman/models",    
        "//sbcman/services",
        "//tests:test_utils",
    ],
    size = "small",
)

# Split test_models.py into separate files
py_test(
    name = "test_game",
    srcs = ["test_game.py"],
    deps = [
        "//sbcman/models:models",
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_game_library",
    srcs = ["test_game_library.py"],
    deps = [
        "//sbcman/hardware:hardware",
        "//sbcman/path:path",
        "//sbcman/models:models",
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_config_manager",
    srcs = ["test_config_manager.py"],
    deps = [
        "//sbcman/hardware:hardware",
        "//sbcman/path:path",
        "//sbcman/models:models",
        "//tests:test_utils",
    ],
    size = "small",
)

# Split test_hardware_detection.py into separate files
py_test(
    name = "test_hardware_detector",
    srcs = ["test_hardware_detector.py"],
    deps = [
        "//sbcman/hardware:hardware",
        "//sbcman/path:path",
        "//tests:test_utils",
        "@sbc_man_pip_deps//pygame_ce",	
    ],
    size = "small",
)

py_test(
    name = "test_hardware_prober",
    srcs = ["test_hardware_prober.py"],
    deps = [
        "//sbcman/hardware:hardware",
        "//sbcman/path:path",
        "//tests:test_utils",
        "@sbc_man_pip_deps//pygame_ce",	
    ],
    size = "small",
)

# Split test_states.py into separate files
py_test(
    name = "test_base_state",
    srcs = ["test_base_state.py"],
    deps = [
        "//sbcman/states:states",
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_menu_state",
    srcs = ["test_menu_state.py"],
    deps = [
        "//sbcman/services:services",
        "//sbcman/states:states",
        "//tests:test_utils",
        "@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_game_list_state",
    srcs = ["test_game_list_state.py"],
    deps = [
        "//sbcman/models:models",
        "//sbcman/services:services",
        "//sbcman/states:states",
        "//tests:test_utils",
        "@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_playing_state",
    srcs = ["test_playing_state.py"],
    deps = [
        "//sbcman/services:services",
        "//sbcman/states:states",
        "//tests:test_utils",
        "@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_settings_state",
    srcs = ["test_settings_state.py"],
    deps = [
        "//sbcman/services:services",
        "//sbcman/states:states",
        "//tests:test_utils",
        "@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_protobuf_api",
    srcs = ["test_protobuf_api.py"],
    deps = [
        "//google",
    ],
    size = "small",
)

# Additional test files for missing coverage
py_test(
    name = "test_application",
    srcs = ["test_application.py"],
    deps = [
        "//sbcman/core:core",
        "//sbcman/hardware:hardware",
        "//sbcman/path:path",
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_paths",
    srcs = ["test_paths.py"],
    deps = [
        "//sbcman/path:path",
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_file_ops",
    srcs = ["test_file_ops.py"],
    deps = [
        "//sbcman/services:services",
        "//tests:test_utils",
    ],
    size = "small",
)
