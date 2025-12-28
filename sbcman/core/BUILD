package(default_visibility = ["//visibility:public"])

py_library(
    name = "core",
    srcs = glob(["*.py"]),
    deps = [
        "//sbcman/hardware:hardware",
        "//sbcman/models:models",
        "//sbcman/services:services",
        "@sbc_man_pip_deps//pygame_ce",
    ],
)