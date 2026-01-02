# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@com_google_protobuf//bazel:py_proto_library.bzl", "py_proto_library")
load("@rules_python//python:py_test.bzl", "py_test")

# Define the proto library for person
proto_library(
    name = "person_proto",
    srcs = ["person.proto"],
    visibility = ["//visibility:public"],
)

# Generate Python bindings for person
py_proto_library(
    name = "person_py_pb2",
    deps = [":person_proto"],
    visibility = ["//visibility:public"],
)

# Define the proto library for game
proto_library(
    name = "game_proto",
    srcs = ["game.proto"],
    visibility = ["//visibility:public"],
)

# Generate Python bindings for game
py_proto_library(
    name = "game_py_pb2",
    deps = [":game_proto"],
    visibility = ["//visibility:public"],
)

# Define the proto library for device config
proto_library(
    name = "device_config_proto",
    srcs = ["device_config.proto"],
    visibility = ["//visibility:public"],
)

# Generate Python bindings for device config
py_proto_library(
    name = "device_config_py_pb2",
    deps = [":device_config_proto"],
    visibility = ["//visibility:public"],
)

# Define the proto library for input mappings
proto_library(
    name = "input_mappings_proto",
    srcs = ["input_mappings.proto"],
    visibility = ["//visibility:public"],
)

# Generate Python bindings for input mappings
py_proto_library(
    name = "input_mappings_py_pb2",
    deps = [":input_mappings_proto"],
    visibility = ["//visibility:public"],
)

# Define the proto library for OS config
proto_library(
    name = "os_config_proto",
    srcs = ["os_config.proto"],
    visibility = ["//visibility:public"],
)

# Generate Python bindings for OS config
py_proto_library(
    name = "os_config_py_pb2",
    deps = [":os_config_proto"],
    visibility = ["//visibility:public"],
)

# Combined proto library that includes all configurations
proto_library(
    name = "config_proto",
    deps = [
        ":device_config_proto",
        ":input_mappings_proto",
        ":os_config_proto",
    ],
    visibility = ["//visibility:public"],
)

# Combined Python bindings for all configurations
py_proto_library(
    name = "config_py_pb2",
    deps = [":config_proto"],
    visibility = ["//visibility:public"],
)

# Python test for person (existing)
py_test(
    name = "person_test",
    srcs = ["person_test.py"],
    deps = [
        ":person_py_pb2",
    ],
)