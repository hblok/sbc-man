# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@com_google_protobuf//bazel:py_proto_library.bzl", "py_proto_library")

# Define the proto library
proto_library(
    name = "game_proto",
    srcs = ["game.proto"],
    visibility = ["//visibility:public"],
)

# Generate Python bindings using rules_python's py_proto_library
py_proto_library(
    name = "game_py_pb2",
    deps = [":game_proto"],
    visibility = ["//visibility:public"],
)
