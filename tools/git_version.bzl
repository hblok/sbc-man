# Extracts the git tag version.

def _git_tag_version_impl(ctx):
    """Extract git version from tags"""
    result = ctx.execute(["git", "describe", "--tags", "--always"])
    
    if result.return_code != 0:
        version = "0.0.0-dev"
    else:
        version = result.stdout.strip()
        # Remove 'v' prefix if present (v1.0.0 -> 1.0.0)
        if version.startswith("v"):
            version = version[1:]
    
    ctx.file("version.txt", version)

git_tag_version = repository_rule(
    implementation = _git_tag_version_impl,
    local = True,
)
