package(default_visibility = ["//visibility:public"])

# Integration tests
py_test(
    name = "test_download_install_flow",
    srcs = ["test_download_install_flow.py"],
    deps = [
        "//src/core:core",
        "//src/models:models",
        "//src/services:services",
        "//tests:test_utils",
        "@pip_dev_deps//:pytest",
    ],
    size = "large",
    python_version = "3.11",
)

py_test(
    name = "test_game_launch_flow",
    srcs = ["test_game_launch_flow.py"],
    deps = [
        "//src/core:core",
        "//src/models:models",
        "//src/services:services",
        "//src/states:states",
        "//tests:test_utils",
        "@pip_dev_deps//:pytest",
    ],
    size = "large",
    python_version = "3.11",
)

py_test(
    name = "test_startup_flow",
    srcs = ["test_startup_flow.py"],
    deps = [
        "//src/core:core",
        "//src/hardware:hardware",
        "//src/models:models",
        "//src/services:services",
        "//tests:test_utils",
        "@pip_dev_deps//:pytest",
    ],
    size = "medium",
    python_version = "3.11",
)

py_test(
    name = "test_state_transition_flow",
    srcs = ["test_state_transition_flow.py"],
    deps = [
        "//src/core:core",
        "//src/models:models",
        "//src/services:services",
        "//src/states:states",
        "//tests:test_utils",
        "@pip_dev_deps//:pytest",
        "@pip_deps//:pygame_ce",
    ],
    size = "medium",
    python_version = "3.11",
)