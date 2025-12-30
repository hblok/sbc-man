def _version_file_impl(ctx):
    """Generate a Python file with version info"""
    version = ctx.attr.version
    
    content = '''"""Auto-generated version file"""
__version__ = "{}"
'''.format(version)
    
    ctx.file("__init__.py", content)
    
    return [
        DefaultInfo(files = depset([ctx.outputs.out])),
    ]

version_file = rule(
    implementation = _version_file_impl,
    attrs = {
        "version": attr.string(mandatory = True),
    },
    outputs = {
        "out": "%{name}.py",
    },
)
