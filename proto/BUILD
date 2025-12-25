load("@rules_proto//proto:defs.bzl", "proto_library")

# Define the proto library
proto_library(
    name = "person_proto",
    srcs = ["person.proto"],
)

# Generate Python bindings using protobuf's rule directly
load("@protobuf//bazel:py_proto_library.bzl", "py_proto_library")

py_proto_library(
    name = "person_py_pb2",
    deps = [":person_proto"],
)

# Python test
py_test(
    name = "person_test",
    srcs = ["person_test.py"],
    deps = [
        ":person_py_pb2",
    ],
)
