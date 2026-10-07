"""Deterministic harness fixtures, never an experimental model treatment."""
from ..adapters.ollama import ModelReply
from ..contracts import ActionRequest
from .feedback import prompt


class ScriptedWindowModel:
    usage_kind = 'simulated'
    request_receipts = True

    def __init__(self, config, controller, mode, actions):
        self.config,self.controller,self.mode = config,controller,mode
        self.actions = iter(actions)
        self.requests = []

    def admission(self, task, observations, state):
        return 512

    def generate(self, task, observations, state, record_request=None):
        messages,metadata = prompt(task,observations,state,self.config,self.controller,self.mode)
        self.requests.append(messages)
        if record_request:
            record_request({'payload':{'messages':messages},'context':metadata,'usage_kind':'simulated'})
        action = next(self.actions,ActionRequest('finish',{}))
        if action is None:
            return ModelReply(None,100,20,{'request_sent':True},'{malformed','invalid','malformed_model_output','simulated')
        return ModelReply(action,100,20,{'request_sent':True},'',usage_kind='simulated')


def repair_factory(plan, requests=None):
    def factory(task,arm,index,controller,mode):
        # Deliberately incomplete initial repair leaves another known component.
        if arm=='I':
            old,new = task.mutations[0]
            actions = [ActionRequest('read_file',{'path':'src/solution.py'}),
                       ActionRequest('edit_file',{'path':'src/solution.py','old':new,'new':old})]
        elif arm=='D':
            previous = task.mutant.replace(task.mutations[0][1],task.mutations[0][0],1)
            actions = [ActionRequest('edit_file',{'path':'src/solution.py','old':previous,'new':task.reference})]
        elif arm=='O':
            actions = [ActionRequest('finish',{})]
        else:
            actions = [ActionRequest('read_file',{'path':'src/solution.py'}),task.repair()]
        model = ScriptedWindowModel(plan['model'],controller,mode,actions)
        if requests is not None:
            requests.append((arm,index,model))
        return model
    return factory
