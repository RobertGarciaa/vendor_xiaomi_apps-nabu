"""Parse aapt2 xmltree structure without borrowing attributes from sibling nodes."""
import re

def parse_xmltree(text):
    roots, stack = [], []
    for line in text.splitlines():
        match = re.match(r'^(\s*)E:\s+(\S+)', line)
        if match:
            indent = len(match[1])
            node = {'tag': match[2], 'attrs': {}, 'children': []}
            while stack and stack[-1][0] >= indent:
                stack.pop()
            (stack[-1][1]['children'] if stack else roots).append(node)
            stack.append((indent, node))
            continue
        match = re.match(r'^\s*A:\s+([^=]+)=(.*)$', line)
        if match and stack:
            key = match[1].split('(')[0].rsplit(':', 1)[-1]
            value = match[2].strip()
            quoted = re.search(r'\(Raw: "(.*)"\)', value) or re.match(r'"(.*?)"', value)
            stack[-1][1]['attrs'][key] = quoted[1] if quoted else value
    if len(roots) != 1 or roots[0]['tag'] != 'manifest':
        raise ValueError('aapt2 did not produce one manifest root')
    return roots[0]

def components(root):
    package = root['attrs'].get('package', '')
    result = {}
    for app in root['children']:
        if app['tag'] != 'application':
            continue
        for node in app['children']:
            if node['tag'] not in ('activity', 'activity-alias', 'service', 'receiver', 'provider'):
                continue
            name = node['attrs'].get('name', '')
            if name.startswith('.'):
                name = package + name
            elif name and '.' not in name:
                name = package + '.' + name
            if name:
                result[name] = node
    return result

def disabled(node):
    value = node['attrs'].get('enabled', '').lower()
    return value == 'false' or bool(re.fullmatch(r'(?:\(type 0x12\))?0x0+', value))

def permissions(root):
    return {node['attrs'].get('name', '') for node in root['children']
            if node['tag'] in ('uses-permission', 'uses-permission-sdk-23', 'uses-permission-sdk-m')}

def active_permissions(root, sdk):
    """Honor maxSdkVersion; obsolete stock declarations are not current grants."""
    result = set()
    for node in root['children']:
        if node['tag'] not in ('uses-permission', 'uses-permission-sdk-23', 'uses-permission-sdk-m'):
            continue
        maximum = node['attrs'].get('maxSdkVersion')
        if maximum is not None:
            # aapt2 prints typed integers as '(type 0x10)0x1c'.
            match = re.search(r'(0x[0-9a-fA-F]+|\d+)$', maximum)
            if not match:
                raise ValueError('Unrecognized maxSdkVersion: ' + maximum)
            if int(match[1], 16 if match[1].startswith('0x') else 10) < sdk:
                continue
        result.add(node['attrs'].get('name', ''))
    return result
