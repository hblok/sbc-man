# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

load("@rules_python//python:py_library.bzl", "py_library")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "models",
    srcs = glob(["*.py"]),
    deps = [
        "//sbcman/path",
	"//sbcman/services",
	"//sbcman/proto:game_py_pb2"
    ],

)