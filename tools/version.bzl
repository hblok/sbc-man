def _version_file_impl(ctx):
    """Generate a Python file with version info"""
    version = ctx.attr.version
    
    content = '''"""Auto-generated version file"""
__version__ = "{}"
'''.format(version)
    
    # Create the output file
    output_file = ctx.actions.declare_file("version.py")
    ctx.actions.write(
        output = output_file,
        content = content,
    )
    
    return [
        DefaultInfo(files = depset([output_file])),
    ]

version_file = rule(
    implementation = _version_file_impl,
    attrs = {
        "version": attr.string(mandatory = True),
    },
    outputs = {
        "out": "version.py",
    },
)
