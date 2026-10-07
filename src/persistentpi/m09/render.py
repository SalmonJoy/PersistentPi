"""Model-visible rendering; reference wrappers introduce no prompt metadata."""
import json

from ..contracts import canonical, digest
from ..control import Controller
from ..interfaces import action_schema
from ..m08.primitive_runtime import PrimitiveController, primitive_prompt
from ..prompts import build_prompt
from .spec import references


def reference_name(configuration):
    return next((name for name, spec in references().items() if spec == configuration.spec), None)


def controller_for(configuration, sources):
    s = configuration.spec
    edit = s.interface.split(':')[0]
    if reference_name(configuration):
        return PrimitiveController(sources, edit)

    class ConfiguredController(Controller):
        def actions(self):
            values = super().actions()
            return tuple('replace_file' if v == 'edit_file' and edit == 'E1' else v for v in values
                         if v != 'run_public_tests' and (v != 'read_file' or self.reads < s.read_allowance))

        def observe(self, action, successful):
            from ..contracts import ActionRequest
            if action.tool == 'replace_file':
                action = ActionRequest('edit_file', action.arguments)
            return super().observe(action, successful)

    return ConfiguredController(s.controller, sources, max(1, s.read_allowance))


def render(configuration, task, observations, state, controller, base_config, source=None, cases=None):
    s = configuration.spec
    edit, protocol = s.interface.split(':', 1)
    config = {**base_config, 'edit_primitive': edit, 'output_protocol': protocol,
              'context': {'max_bytes': 7000, 'field_bytes': 1800, 'recent_observations': s.recent_observations}}
    if (s.controller == 'C3' and s.read_allowance == 2 and not s.source_preload
            and s.recent_observations == 4 and s.rejection_feedback == 'generic'
            and s.context_fields == references()['B0'].context_fields):
        messages, metadata = primitive_prompt(task, observations, state, config, controller)
        messages[0]['content'] = s.system_text
        if s.tool_descriptions:
            public = json.loads(messages[1]['content'])
            for name, description in s.tool_descriptions:
                if name == 'finish' and name in controller.actions():
                    public['tools'].setdefault(name, {'arguments': [], 'permission': 'finish'})
                if name in public['tools']:
                    public['tools'][name] = {**public['tools'][name], 'description':description}
            messages[1]['content'] = canonical(public).decode()
        if len(canonical(messages)) > 7000:
            raise ValueError('Authored reference-layout prompt exceeds byte cap')
        metadata.update(prompt_hash=digest(messages),prompt_bytes=len(canonical(messages)),renderer=configuration.renderer)
        return messages, metadata
    observed = observations[-s.recent_observations:] if s.recent_observations else ()
    messages, metadata = build_prompt(task, observed, state, {**config['context'], 'max_bytes': 1000000}, protocol, edit)
    data = json.loads(messages[1]['content'])
    data['budget'].pop('remaining_attempts', None)
    from ..control import VERSIONS
    data['control'] = {'policy': s.controller, 'version': VERSIONS[s.controller], 'phase': controller.phase or 'ACT',
                       'successful_reads': controller.reads, 'inspection_budget': s.read_allowance,
                       'available_actions': list(controller.actions())}
    data['tools'] = {k: v for k, v in data['tools'].items() if k in controller.actions()}
    for name, description in s.tool_descriptions:
        if name == 'finish' and name in controller.actions():
            data['tools'].setdefault(name, {'arguments': [], 'permission': 'finish'})
        if name in data['tools']:
            data['tools'][name] = {**data['tools'][name], 'description': description}
    if 'source' in s.context_fields:
        data['source'] = source
    if 'public_cases' in s.context_fields:
        data['public_cases'] = cases
    messages[0]['content'] = s.system_text
    while True:
        selected = {k: data[k] for k in s.context_fields if k in data}
        messages[1]['content'] = json.dumps(selected, separators=(',', ':'), ensure_ascii=True, allow_nan=False)
        if len(canonical(messages)) <= 7000:
            break
        if data.get('observations'):
            data['observations'].pop(0)
        else:
            raise ValueError('Mandatory context exceeds byte cap')
    metadata.update(prompt_hash=digest(messages), prompt_bytes=len(canonical(messages)), renderer=configuration.renderer)
    controller.context(selected.get('observations', []))
    if selected.get('source') is not None:
        controller.visible.add('src/solution.py')
    return messages, metadata


def wire_request(configuration, task, observations, state, controller, base_config, source=None, cases=None):
    messages, metadata = render(configuration, task, observations, state, controller, base_config, source, cases)
    s = configuration.spec
    edit, protocol = s.interface.split(':', 1)
    output = s.inspect_output if controller.phase == 'INSPECT' else s.act_output
    payload = {'model': base_config['model'], 'messages': messages, 'stream': False,
               'options': {'temperature': 0, 'seed': 42, 'num_ctx': 4096,
                           'num_predict': min(output, max(1, state.remaining_tokens))},
               'keep_alive': '5m', 'think': False}
    if protocol == 'runner-json-schema-1':
        schema = action_schema(edit)
        schema['anyOf'] = [b for b in schema['anyOf'] if b['properties']['tool']['enum'][0] in controller.actions()]
        payload['format'] = schema
    elif protocol == 'runner-json-1':
        payload['format'] = 'json'
    return payload, metadata
