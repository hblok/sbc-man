# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

# See:
# https://github.com/bazel-contrib/rules_python/blob/main/python/packaging.bzl
# https://rules-python.readthedocs.io/en/0.32.0/api/packaging.html
# https://buildkite.com/resources/blog/building-and-packaging-a-python-library-with-bazel/
# https://realpython.com/python-wheels/

load("@rules_python//python:packaging.bzl", "py_wheel", "py_package")
load("//tools:version_gen.bzl", "gen_version")

package(default_visibility = ["//visibility:public"])

# Generate version file
gen_version(
    name = "gen_version",
)

# Main entry point
py_binary(
    name = "main",
    srcs = ["main.py"],
    main = "main.py",
    deps = [
        "//sbcman/core",
        "//sbcman/path",	
    ],
)

# Configuration files
filegroup(
    name = "config_files",
    srcs = glob([
        "config/**/*",
        "data/**/*",
    ]),
    visibility = ["//visibility:public"],
)

py_library(
    name = "sbcman",
    srcs = ["main.py"],
    deps = [
        ":gen_version",
        "//sbcman/core",
	"//sbcman/hardware",
	"//sbcman/path",
	"//sbcman/services",
	"//sbcman/states",
	"//sbcman/views",
	"//sbcman/views/widgets",
#	"//google",
    ],
    data = [
    	 "//sbcman:config_files"
    ]
)

py_package(
    name = "sbc_man_package",
    packages = ["sbcman", "google"],
    deps = [
      "//sbcman",
#      "//google",
    ]
)

py_wheel(
    name = "sbcman_wheel",
    distribution = "sbcman",
    version = "$(SBCMAN_VERSION)",
    deps = [
        ":sbc_man_package",
    ],
)
