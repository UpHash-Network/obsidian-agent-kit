#!/usr/bin/env python3
"""Export token counters and fictional answers, never raw logs or account IDs."""
import json
import re

FIELDS = ['regular_input', 'cache_write', 'cache_read', 'output']


def normalize(client, usage, previous=None):
    if usage is None:
        raise ValueError('Missing usage is not zero')
    if client == 'codex':
        keys = ['input_tokens', 'cached_input_tokens', 'output_tokens']
        previous = previous or dict.fromkeys(keys, 0)
        delta = {k: usage[k] - previous[k] for k in keys}
        if any(v < 0 for v in delta.values()):
            raise ValueError('Non-monotone cumulative Codex usage')
        result = {'regular_input': delta['input_tokens'] - delta['cached_input_tokens'],
                  'cache_write': 0, 'cache_read': delta['cached_input_tokens'],
                  'output': delta['output_tokens']}
    elif client == 'claude':
        names = ['inputTokens', 'cacheCreationInputTokens', 'cacheReadInputTokens', 'outputTokens']
        result = {field: sum(model[key] for model in usage.values()) for field, key in zip(FIELDS, names)}
    elif client == 'cursor':
        names = ['inputTokens', 'cacheWriteTokens', 'cacheReadTokens', 'outputTokens']
        result = {field: usage[key] for field, key in zip(FIELDS, names)}
    else:
        raise ValueError(client)
    if any(v < 0 for v in result.values()):
        raise ValueError('Negative counter')
    return dict(result, total=sum(result.values()))


def reduction(before, after):
    return 100 * (before - after) / before


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from strings(v)


def statuses(events):
    found = {}
    for text in strings(events):
        for line in text.splitlines():
            if not line.startswith('{'):
                continue
            try:
                item = json.loads(line)
            except ValueError:
                continue
            if isinstance(item, dict) and item.get('status') in ['CONTENT', 'UNCHANGED'] and 'sha256' in item:
                found[item['path']] = {k: item[k] for k in ['path', 'sha256', 'status']}
    return list(found.values())
