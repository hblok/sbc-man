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
        "//sbcman/services",
        "//tests:test_utils",
    ],
    size = "medium",
)

py_test(
    name = "test_download_state",
    srcs = ["test_download_state.py"],
    deps = [
        "//sbcman/states:states",
        "//sbcman/services",
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_input_handler",
    srcs = ["test_input_handler.py"],
    deps = [
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
        "//sbcman/services",
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_game_library",
    srcs = ["test_game_library.py"],
    deps = [
        "//sbcman/hardware",
        "//sbcman/path",
	"//sbcman/services",	
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_config_manager",
    srcs = ["test_config_manager.py"],
    deps = [
        "//sbcman/hardware:hardware",
        "//sbcman/path",
	"//sbcman/services",
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
        "//sbcman/states:states",
        "//sbcman/services",
        "//tests:test_utils",
        "@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_game_list_state",
    srcs = ["test_game_list_state.py"],
    deps = [
        "//sbcman/states:states",
        "//sbcman/services",
        "//tests:test_utils",
        "@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_playing_state",
    srcs = ["test_playing_state.py"],
    deps = [
        "//sbcman/states:states",
        "//sbcman/services",
        "//tests:test_utils",
        "@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_settings_state",
    srcs = ["test_settings_state.py"],
    deps = [
        "//sbcman/states:states",
        "//sbcman/services",
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
	 "@com_google_protobuf//:protobuf"
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
        "//sbcman/services",
        "//tests:test_utils",
    ],
    size = "small",
)

# Tests for missing test coverage
py_test(
    name = "test_game_loop",
    srcs = ["test_game_loop.py"],
    deps = [
	"//sbcman/core:core",
	"//tests:test_utils",
	"@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_state_manager",
    srcs = ["test_state_manager.py"],
    deps = [
	"//sbcman/core:core",
	"//sbcman/states:states",
	"//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_compat_sdl",
    srcs = ["test_compat_sdl.py"],
    deps = [
	"//sbcman/hardware:hardware",
	"//tests:test_utils",
        "//sbcman/path:path",    	
	"@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_game_utils",
    srcs = ["test_game_utils.py"],
    deps = [
	"//sbcman/services",
	"//google",
	"@com_google_protobuf//:protobuf",
    ],
    size = "small",
)

py_test(
    name = "test_process_launcher",
    srcs = ["test_process_launcher.py"],
    deps = [
	"//sbcman/services",
	"//google",
	"@com_google_protobuf//:protobuf",
    ],
    size = "small",
)

py_test(
    name = "test_wheel_installer",
    srcs = ["test_wheel_installer.py"],
    deps = [
	"//sbcman/services",
	"//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_update_state",
    srcs = ["test_update_state.py"],
    deps = [
	"//sbcman/states:states",
	"//sbcman/services",
	"//sbcman/views/widgets:widgets",
	"//tests:test_utils",
	"@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_scrollable_list",
    srcs = ["test_scrollable_list.py"],
    deps = [
	"//sbcman/views/widgets:widgets",
	"//tests:test_utils",
	"@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_install_game",
    srcs = ["test_install_game.py"],
    deps = [
	"//sbcman/services",
	"//tests:test_utils",
	"@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_updater",
    srcs = ["test_updater.py"],
    deps = [
	"//sbcman/services",
	"//tests:test_utils",
	"@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_game_library_enhanced",
    srcs = ["test_game_library_enhanced.py"],
    deps = [
	"//sbcman/services",
	"//tests:test_utils",
	"@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_game_list_entry",
    srcs = ["test_game_list_entry.py"],
    deps = [
	"//sbcman/services",
	"//tests:test_utils",
	"@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_install_settings_state",
    srcs = ["test_install_settings_state.py"],
    deps = [
	"//sbcman/states",
	"//tests:test_utils",
	"@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

# New unit tests for missing modules
py_test(
    name = "test_device",
    srcs = ["test_device.py"],
    deps = [
        "//sbcman/path:path",
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_archive_extractor",
    srcs = ["test_archive_extractor.py"],
    deps = [
        "//sbcman/services",
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_game_launcher",
    srcs = ["test_game_launcher.py"],
    deps = [
        "//sbcman/services",
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_network",
    srcs = ["test_network.py"],
    deps = [
        "//sbcman/services",
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_portmaster",
    srcs = ["test_portmaster.py"],
    deps = [
        "//sbcman/path:path",
        "//sbcman/services",
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_scrollable_icon_list",
    srcs = ["test_scrollable_icon_list.py"],
    deps = [
        "//sbcman/views/widgets:widgets",
        "//tests:test_utils",
        "@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_version_overlay",
    srcs = ["test_version_overlay.py"],
    deps = [
        "//sbcman/views/widgets:widgets",
        "//tests:test_utils",
        "@sbc_man_pip_deps//pygame_ce",
    ],
    size = "small",
)
