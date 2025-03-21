# BUILD file for generating Python protobuf code

load("@rules_proto//proto:defs.bzl", "proto_library")
load("@rules_python//python:defs.bzl", "py_binary", "py_library")
load("@com_google_protobuf//bazel:py_proto_library.bzl", "py_proto_library")
load("@rules_python//python:py_test.bzl", "py_test")

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

py_library(
    name = "family_tree_lib",
    srcs = ["src/family_tree_handler.py"],
    imports = ["src"], 
    deps = [
        ":family_tree_py_proto",
        "@local_pypi_for_family_tree//networkx",
        "@local_pypi_for_family_tree//pyvis",
    ],
)

py_binary(
    name = "family_tree_main",
    srcs = ["src/family_tree_app.py"],
    deps = [
        ":family_tree_py_proto",
        ":family_tree_lib",
        "@local_pypi_for_family_tree//networkx",
        "@local_pypi_for_family_tree//pyvis",
        ],
    main = "family_tree_app.py"
)

"""
py_test(
    name = "test_family_tree_handler",
    srcs = ["tests/test_family_tree_handler.py"],
    deps = [
        ":family_tree_lib",
        ":family_tree_py_proto",
        "@local_pypi_for_family_tree//pytest",
        "@local_pypi_for_family_tree//networkx",
        "@local_pypi_for_family_tree//protobuf",
    ],
    args = ["--", "-v","-s"]
)
"""

load("@rules_python_pytest//python_pytest:defs.bzl", "py_pytest_test")

py_pytest_test(
    name = "test_family_tree_handler",
    srcs = ["tests/test_family_tree_handler.py"],
    deps = [
        ":family_tree_lib",
        ":family_tree_py_proto",
        "@local_pypi_for_family_tree//pytest",
        "@local_pypi_for_family_tree//networkx",
        "@local_pypi_for_family_tree//protobuf",
    ]
)