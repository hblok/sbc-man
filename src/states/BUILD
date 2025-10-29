package(default_visibility = ["//visibility:public"])

py_library(
    name = "states",
    srcs = [
        "__init__.py",
        "base_state.py",
        "download_state.py",
        "game_list_state.py",
        "menu_state.py",
        "playing_state.py",
        "settings_state.py",
    ],
    deps = [
        "//src/models:models",
        "//src/services:services",
        "@pip_deps//pygame_ce",
    ],
)