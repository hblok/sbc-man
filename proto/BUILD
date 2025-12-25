load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@com_google_protobuf//bazel:py_proto_library.bzl", "py_proto_library")
load("@rules_python//python:py_test.bzl", "py_test")

# Define the proto library
proto_library(
    name = "person_proto",
    srcs = ["person.proto"],
    visibility = ["//visibility:public"],
)

# Generate Python bindings using rules_python's py_proto_library
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
