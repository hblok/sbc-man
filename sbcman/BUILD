# See:
# https://github.com/bazel-contrib/rules_python/blob/main/python/packaging.bzl
# https://rules-python.readthedocs.io/en/0.32.0/api/packaging.html
# https://buildkite.com/resources/blog/building-and-packaging-a-python-library-with-bazel/
# https://realpython.com/python-wheels/

load("@rules_python//python:packaging.bzl", "py_wheel", "py_package")

package(default_visibility = ["//visibility:public"])

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
    name = "sbc_man",
    srcs = ["main.py"],
    deps = [
        "//sbcman/core:core",
    ],    
)

py_package(
    name = "sbc_man_package",
    packages = ["sbcman.core", "google"],
    deps = [
      "//sbcman/core:core",
      "//google",
    ]
)

py_wheel(
    name = "sbc_man_wheel",
    distribution = "sbc_man",
    version = "0.1.0",
    deps = [
    	 ":sbc_man_package"
	 ],
)
