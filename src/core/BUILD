package(default_visibility = ["//visibility:public"])

py_library(
    name = "core",
    srcs = [
        "__init__.py",
        "application.py",
        "game_loop.py",
        "state_manager.py",
    ],
    deps = [
        "//src/hardware:hardware",
        "//src/models:models",
        "//src/services:services",
        "@pip_deps//pygame_ce",
    ],
)