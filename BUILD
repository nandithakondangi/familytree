# BUILD file for generating Python protobuf code

load("@rules_proto//proto:defs.bzl", "proto_library")
load("@rules_python//python:defs.bzl", "py_binary")
load("@com_google_protobuf//bazel:py_proto_library.bzl", "py_proto_library")

proto_library(
    name = "utils_proto",
    srcs = ["utils.proto"],
    visibility = ["//visibility:public"],
)

proto_library(
    name = "family_tree_proto",
    srcs = ["family_tree.proto"],
    deps = [":utils_proto"],
    visibility = ["//visibility:public"]
)

py_proto_library(
    name = "utils_py_proto",
    deps = [":utils_proto"],
    visibility = ["//visibility:public"],
)

py_proto_library(
    name = "family_tree_py_proto",
    deps = [":family_tree_proto"],
    visibility = ["//visibility:public"]
)

py_binary(
    name = "family_tree_main",
    srcs = ["family_tree.py"],
    deps = [
        ":family_tree_py_proto",
        "@local_pypi_for_family_tree//networkx",
        "@local_pypi_for_family_tree//pyvis",
        ],
    main = "family_tree.py"
)
