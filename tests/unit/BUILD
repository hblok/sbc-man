package(default_visibility = ["//visibility:public"])

# Unit tests
py_test(
    name = "test_config_loader",
    srcs = ["test_config_loader.py"],
    deps = [
        "//src/hardware:hardware",    
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_download_manager",
    srcs = ["test_download_manager.py"],
    deps = [
        "//src/models:models",
        "//src/services:services",
        "//tests:test_utils",
    ],
    size = "medium",
)

py_test(
    name = "test_download_state",
    srcs = ["test_download_state.py"],
    deps = [
        "//src/models:models",
        "//src/states:states",
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_hardware_detection",
    srcs = ["test_hardware_detection.py"],
    deps = [
        "//src/hardware:hardware",
        "//tests:test_utils",
        "@pip_deps//pygame_ce",	
    ],
    size = "small",
)

py_test(
    name = "test_input_handler",
    srcs = ["test_input_handler.py"],
    deps = [
        "//src/models",
        "//src/services",	
        "//tests:test_utils",
        "@pip_deps//pygame_ce",
    ],
    size = "small",
)

py_test(
    name = "test_models",
    srcs = ["test_models.py"],
    deps = [
        "//src/hardware:hardware",
        "//src/models:models",
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_network_service",
    srcs = ["test_network_service.py"],
    deps = [
        "//src/models",    
        "//src/services",
        "//tests:test_utils",
    ],
    size = "small",
)

py_test(
    name = "test_states",
    srcs = ["test_states.py"],
    deps = [
        "//src/models:models",
        "//src/services:services",
        "//src/states:states",
        "//tests:test_utils",
        "@pip_deps//pygame_ce",
    ],
    size = "small",
)