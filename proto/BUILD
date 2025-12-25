load("@rules_proto//proto:defs.bzl", "proto_library")
load("@rules_python//python:proto.bzl", "py_proto_library")

# Define the proto library
proto_library(
    name = "person_proto",
    srcs = ["person.proto"],
    visibility = ["//visibility:public"],
)

# Generate Python bindings using rules_python's py_proto_library
# This provides the proper PyInfo provider
py_proto_library(
    name = "person_py_pb2",
    deps = [":person_proto"],
    visibility = ["//visibility:public"],
)

# Python test
py_test(
    name = "person_test",
    srcs = ["person_test.py"],
    deps = [
        ":person_py_pb2",
    ],
)