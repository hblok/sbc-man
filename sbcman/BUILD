# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

# See:
# https://github.com/bazel-contrib/rules_python/blob/main/python/packaging.bzl
# https://rules-python.readthedocs.io/en/0.32.0/api/packaging.html
# https://buildkite.com/resources/blog/building-and-packaging-a-python-library-with-bazel/
# https://realpython.com/python-wheels/

load("@rules_python//python:packaging.bzl", "py_wheel", "py_package")
load("//tools:version_gen.bzl", "gen_version")
load("//tools:py_wheel_stamped.bzl", "py_wheel_stamped")

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
        "//sbcman/core:core",
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
	"//sbcman/models",
	"//sbcman/services",
	"//sbcman/states",
	"//sbcman/views",
	"//sbcman/views/widgets",
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
      "//google",
    ]
)

#py_wheel_stamped(
#    name = "sbc_man_wheel",
#    distribution = "sbcman",
#    deps = [
#    	 ":sbc_man_package"#
#	 ],
#)

# Create the base wheel
py_wheel(
    name = "sbc_man_wheel_base",
    distribution = "sbc_man",
    version = "$(STABLE_VERSION)",  # Placeholder
    deps = [
        ":sbc_man_package",
    ],
)

# Rename it with the stamped version
py_wheel_stamped(
    name = "sbc_man_wheel",
    wheel = ":sbc_man_wheel_base",
    distribution = "sbc_man",
)

genrule(
    name = "sbc_man_wheel_versioned",
    srcs = [":sbc_man_wheel_base"],
    outs = ["sbc_man-$(STABLE_VERSION)-py3-none-any.whl"],
    cmd = "cp $< $@",
)
