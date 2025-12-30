load("@rules_python//python:packaging.bzl", "py_wheel", "py_package")

def _py_wheel_stamped_impl(ctx):
    """Create a py_wheel and rename it with the stamped version"""

    # Debug: Print all available variables
    print("$(STABLE_VERSION)")
    print("=== Available Variables ===")
    for key in sorted(ctx.var.keys()):
        print("  {}: {}".format(key, ctx.var[key]))
#    print("===========================")
#    for key in sorted(ctx.expand_make_variables()):
#        print("  {}: {}".format(key, ctx.var[key]))
    print("===========================")

    # Get the base wheel from the py_wheel target
    base_wheel = ctx.attr.wheel[DefaultInfo].files.to_list()[0]
    
    # Get version from workspace status
    version = ctx.var.get("STABLE_VERSION", "0.0.0-dev")
    
    # Create output filename
    output_name = "{}-{}-py3-none-any.whl".format(
        ctx.attr.distribution,
        version
    )
    output_file = ctx.actions.declare_file(output_name)
    
    # Copy the wheel with the new name
    ctx.actions.run_shell(
        inputs = [base_wheel],
        outputs = [output_file],
        command = "cp {} {}".format(base_wheel.path, output_file.path),
    )
    
    return [
        DefaultInfo(files = depset([output_file])),
    ]

py_wheel_stamped = rule(
    implementation = _py_wheel_stamped_impl,
    attrs = {
        "wheel": attr.label(mandatory = True),
        "distribution": attr.string(mandatory = True),
    },
)
