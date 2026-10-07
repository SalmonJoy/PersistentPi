"""Public snapshot boundary: private benchmark assets are intentionally absent."""
from dataclasses import dataclass
from ..contracts import TaskView, digest
from ..m08.benchmark import FAMILIES
from persistentpi.private_assets import PrivateAssetUnavailable

def _unavailable(*args, **kwargs):
    raise PrivateAssetUnavailable("Private benchmark payload/constructor is not distributed.")


@dataclass(frozen=True)
class PublicTask:
    task_id: str
    family: str
    template: str
    source: str
    cases: tuple
    view: TaskView
    task_hash: str
    parameter: int

    def to_dict(self):
        return {'task_id': self.task_id, 'family': self.family, 'template': self.template,
                'source': self.source, 'cases': list(self.cases), 'view': self.view.to_dict(),
                'task_hash': self.task_hash, 'parameter': self.parameter}

    @classmethod
    def from_dict(cls, row):
        view = dict(row['view'])
        view.pop('contract_version', None)
        view['editable_paths'], view['readable_paths'] = tuple(view['editable_paths']), tuple(view['readable_paths'])
        return cls(row['task_id'], row['family'], row['template'], row['source'], tuple(row['cases']),
                   TaskView(**view), row['task_hash'], row['parameter'])

def manifest(tasks, name):
    rows = [{'task_id': t.task_id, 'task_hash': t.task_hash, 'public_hash': digest(t.to_dict()),
             'family': t.family, 'template': t.template, 'parameter': t.parameter}
            for t in sorted(tasks, key=lambda t: t.task_id)]
    return {'cohort': name, 'rows': rows, 'hash': digest({'cohort': name, 'rows': rows})}

def split_search(tasks):
    screen = tuple(min((t for t in tasks if t.family == f),
                       key=lambda t: digest([9001, t.task_id])) for f in FAMILIES)
    remaining = tuple(t for t in tasks if t.task_id not in {s.task_id for s in screen})
    if (len(screen) != 8 or len(remaining) != 24
            or {t.task_id for t in screen} & {t.task_id for t in remaining}):
        raise ValueError('Search partition invalid')
    return screen, remaining

class CohortAccess:
    def __init__(self, search, qualification_tasks):
        self._search, self._qualification = tuple(search), tuple(qualification_tasks)

    def request(self, name, phase, frozen=False):
        if name in ('final', 'hidden'):
            raise PermissionError('Final/hidden cohort access denied')
        if name == 'qualification':
            if phase != 'qualification' or not frozen:
                raise PermissionError('Qualification requires durable finalist barrier')
            return self._qualification
        if name == 'search':
            return self._search
        if name in ('screen', 'remaining'):
            screen, remaining = split_search(self._search)
            return screen if name == 'screen' else remaining
        raise PermissionError('Unknown cohort')

exposed_search = _unavailable
qualification = _unavailable
