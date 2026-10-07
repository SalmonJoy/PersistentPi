"""Trusted built-in registry; generated and arbitrary execution tools are absent."""
TOOLS = {
    'read_file': {'arguments': ('path',), 'permission': 'read_task'},
    'edit_file': {'arguments': ('path', 'old', 'new'), 'permission': 'edit_declared_source'},
    'run_public_tests': {'arguments': (), 'permission': 'public_verify'},
}
TOOLSET_VERSION = '0.1'


def authorize(action):
    if action.tool not in TOOLS:
        raise ValueError('Undeclared tool: ' + action.tool)
    if set(action.arguments) != set(TOOLS[action.tool]['arguments']):
        raise ValueError('Invalid tool arguments')
    if any(not isinstance(value, str) for value in action.arguments.values()):
        raise ValueError('Tool arguments must be strings')
