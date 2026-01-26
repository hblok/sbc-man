# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

load("@rules_python//python:py_library.bzl", "py_library")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "services",
    srcs = glob(["*.py"]),
    deps = [
    	"//sbcman:version",    
    	"//sbcman/path",
	"//sbcman/proto:game_py_pb2",
        "@sbc_man_pip_deps//pygame_ce",
        "@sbc_man_pip_deps//requests",
    ],
)