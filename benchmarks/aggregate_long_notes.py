#!/usr/bin/env python3
"""Publish sanitized long-note results, retaining every measured completed trial."""
import json
import re

try:
    from .aggregate_tokens import FIELDS, normalize, reduction, statuses, strings
    from .long_notes import SCENARIOS, expected
    from .run_tokens import read_events, write_json
except ImportError:
    from aggregate_tokens import FIELDS, normalize, reduction, statuses, strings
    from long_notes import SCENARIOS, expected
    from run_tokens import read_events, write_json


def tool_outputs(client, events):
    """Text bodies only: no duplicated Cursor interleavedOutput or event wrappers."""
    for event in events:
        if client == 'codex' and event.get('type') == 'item.completed':
            item = event.get('item', {})
            if item.get('type') == 'command_execution':
                yield item.get('aggregated_output', '')
        elif client == 'claude' and event.get('type') == 'user':
            for block in event.get('message', {}).get('content', []):
                if isinstance(block, dict) and block.get('type') == 'tool_result':
                    yield '\n'.join(strings(block.get('content', '')))
        elif client == 'cursor' and event.get('type') == 'tool_call' and event.get('subtype') == 'completed':
            call = event.get('tool_call', {})
            for key, value in call.items():
                if not key.endswith('ToolCall') or not isinstance(value, dict):
                    continue
                result = value.get('result', {})
                success = result.get('success', {})
                if key == 'shellToolCall':
                    yield success.get('stdout', '') + success.get('stderr', '')
                elif key == 'readToolCall':
                    # Cursor versions may use content or contents for a read body.
                    field = next((k for k in ['content', 'contents', 'text'] if k in success), None)
                    if field is None:
                        raise ValueError('Unrecognized Cursor Read result; inspect local evidence')
                    yield '\n'.join(strings(success[field]))
                elif key == 'grepToolCall':
                    for workspace in success.get('workspaceResults', {}).values():
                        for match in workspace.get('content', {}).get('matches', []):
                            yield '\n'.join(line['content'] for line in match.get('matches', []))
                elif success:
                    raise ValueError('Unexpected tool in benchmark: ' + key)


def quality(answer, scenario, stage):
    strict = True
    try:
        parsed = json.loads(answer)
    except ValueError:
        strict = False
        # Some CLIs include commentary in result. Check facts separately from format.
        try:
            parsed, _ = json.JSONDecoder().raw_decode(answer[answer.index('{'):])
        except (ValueError, json.JSONDecodeError):
            return {'exact_facts': False, 'exact_facts_and_format': False, 'reason': 'no JSON object'}
    correct = parsed == expected(scenario, stage)
    return {'exact_facts': correct, 'exact_facts_and_format': strict and correct}


def action_summaries(client, calls):
    """Publish behavior evidence without commands, user paths or tool/account IDs."""
    summaries = []
    for call in calls:
        if client == 'codex':
            tool, args = call.get('type', ''), {'command': call.get('command', '')}
        elif client == 'claude':
            tool, args = call.get('name', ''), call.get('input', {})
        else:
            tool = next((k for k in call if k.endswith('ToolCall')), '')
            args = call.get(tool, {}).get('args', {})
        command = args.get('command', '')
        path = args.get('path', args.get('file_path', ''))
        relevant_text = command + ' ' + path
        files = sorted(set(re.findall(r'Projects/[A-Za-z]+\.md|Policies/Knowledge policy\.md', relevant_text)))
        if 'obsidian_context.py' in command:
            mode = 'helper-check' if '--check' in command else 'helper-read'
        elif any(word in command for word in ['awk ', 'grep ', 'sed ']):
            mode = 'filtered-shell-read'
        elif 'cat ' in command:
            mode = 'full-shell-read'
        elif 'wc ' in command:
            mode = 'size-check'
        elif 'grep' in tool.lower():
            mode = 'search'
        elif 'read' in tool.lower():
            mode = 'partial-file-read' if args.get('limit') or args.get('offset') else 'file-read'
        else:
            mode = 'other'
        item = {'tool': tool, 'mode': mode, 'notes': files}
        if path.rstrip('/').endswith('/vault/Projects'):
            item['target'] = 'all-projects-directory'
        elif '/agent-tools/' in path:
            item['target'] = 'current-tool-output'
        summaries.append(item)
    return summaries
