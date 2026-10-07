"""Data-only interpreter for M0.2 smoke functions. Never eval/exec model code."""
import ast
import math
import operator
import types

POLICY_VERSION = 'bounded-python-1'
MAX_ITEMS = 128
MAX_STRING = 4096
MAX_STEPS = 10000
BINOPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
          ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod}
COMPARE = {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
           ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge,
           ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b,
           ast.Is: operator.is_, ast.IsNot: operator.is_not}
BUILTINS = {'len': len, 'abs': abs, 'min': min, 'max': max, 'sum': sum,
            'int': int, 'float': float, 'str': str, 'bool': bool, 'sorted': sorted,
            'list': list, 'tuple': tuple, 'all': all, 'any': any}
METHODS = {'strip', 'lstrip', 'rstrip', 'split', 'lower', 'upper', 'startswith', 'endswith', 'join'}
ALLOWED = (ast.Module, ast.FunctionDef, ast.arguments, ast.arg, ast.Return, ast.Assign,
           ast.AugAssign, ast.If, ast.For, ast.Break, ast.Continue, ast.Pass, ast.Expr,
           ast.Name, ast.Load, ast.Store, ast.Constant, ast.List, ast.Tuple, ast.Dict,
           ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare, ast.IfExp, ast.Call,
           ast.Attribute, ast.Subscript, ast.Slice, ast.ListComp, ast.comprehension,
           ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,
           ast.UAdd, ast.USub, ast.Not, ast.And, ast.Or, *COMPARE)


class PolicyError(ValueError):
    pass


def checked(value, depth=0, budget=None):
    budget = budget if budget is not None else [4096]
    budget[0] -= 1
    if budget[0] < 0:
        raise PolicyError('Value traversal limit exceeded')
    if depth > 16:
        raise PolicyError('Value nesting limit exceeded')
    if value is None or type(value) is bool:
        return value
    if type(value) is int and value.bit_length() <= 128:
        return value
    if type(value) is float and math.isfinite(value) and abs(value) <= 1e30:
        return value
    if type(value) is str and len(value) <= MAX_STRING:
        return value
    if type(value) in (list, tuple, dict) and len(value) <= MAX_ITEMS:
        for item in (list(value.keys()) + list(value.values()) if type(value) is dict else value):
            checked(item, depth + 1, budget)
        return value
    raise PolicyError('Value type or size limit exceeded')


def parse(source):
    if len(source.encode('utf-8')) > 16384:
        raise PolicyError('Source size limit exceeded')
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise PolicyError('Invalid Python syntax') from exc
    nodes = list(ast.walk(tree))
    if len(nodes) > 1000 or not tree.body:
        raise PolicyError('AST size limit exceeded or empty module')
    if any(not isinstance(node, ast.FunctionDef) for node in tree.body):
        raise PolicyError('Only pure function definitions are allowed at module scope')
    callable_names = {node.name for node in tree.body} | set(BUILTINS) | {'range'}
    for node in nodes:
        if not isinstance(node, ALLOWED):
            raise PolicyError('Unsupported syntax: ' + type(node).__name__)
        if isinstance(node, (ast.Name, ast.arg)) and getattr(node, 'id', getattr(node, 'arg', '')).startswith('_'):
            raise PolicyError('Private names are forbidden')
        if isinstance(node, ast.FunctionDef):
            if node not in tree.body or node.name.startswith('_') or node.decorator_list or node.returns:
                raise PolicyError('Nested/decorated/annotated functions are forbidden')
            args = node.args
            if args.defaults or args.kw_defaults or args.kwonlyargs or args.vararg or args.kwarg or args.posonlyargs:
                raise PolicyError('Only positional function parameters are supported')
            if any(a.annotation for a in args.args):
                raise PolicyError('Annotations are not supported')
        if isinstance(node, ast.Attribute) and node.attr not in METHODS:
            raise PolicyError('Unsupported attribute/method')
        if isinstance(node, ast.Call) and (node.keywords or not isinstance(node.func, (ast.Name, ast.Attribute))):
            raise PolicyError('Only direct calls with positional arguments are allowed')
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id not in callable_names:
            raise PolicyError('Call is not allowed: ' + node.func.id)
        if isinstance(node, ast.Constant):
            checked(node.value)
        if isinstance(node, (ast.Assign, ast.AugAssign, ast.For, ast.comprehension)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(not isinstance(target, ast.Name) for target in targets):
                raise PolicyError('Assignment targets must be local names')
        if isinstance(node, ast.comprehension) and node.is_async:
            raise PolicyError('Async comprehensions are forbidden')
    names = [node.name for node in tree.body]
    if len(set(names)) != len(names):
        raise PolicyError('Duplicate function definitions')
    return tree


class Returned(Exception):
    def __init__(self, value):
        self.value = value


class LoopBreak(Exception):
    pass


class LoopContinue(Exception):
    pass


class Interpreter:
    def __init__(self, source):
        self.functions = {node.name: node for node in parse(source).body}

    def call(self, name, args, fuel=None, depth=0):
        if depth >= 16:
            raise PolicyError('Call depth exceeded')
        node = self.functions[name]
        if len(args) != len(node.args.args):
            raise TypeError('Incorrect argument count')
        env = {p.arg: checked(v) for p, v in zip(node.args.args, args)}
        fuel = fuel if fuel is not None else [MAX_STEPS]
        try:
            self.block(node.body, env, fuel, depth)
        except Returned as result:
            return checked(result.value)
        return None

    def tick(self, fuel):
        fuel[0] -= 1
        if fuel[0] < 0:
            raise PolicyError('Execution step limit exceeded')

    def binary(self, op, left, right):
        if isinstance(op, ast.Mult) and (type(left) in (list, tuple, str) or type(right) in (list, tuple, str)):
            sequence, count = (left, right) if type(left) in (list, tuple, str) else (right, left)
            limit = MAX_STRING if type(sequence) is str else MAX_ITEMS
            if type(count) is not int or len(sequence) * max(0, count) > limit:
                raise PolicyError('Sequence multiplication exceeds limit')
        if isinstance(op, ast.Mod) and (type(left) not in (int, float) or type(right) not in (int, float)):
            raise PolicyError('Only numeric remainder is supported')
        return checked(BINOPS[type(op)](left, right))

    def expression(self, node, env, fuel, depth):
        self.tick(fuel)
        evaluate = lambda item: self.expression(item, env, fuel, depth)
        if isinstance(node, ast.Constant):
            result = node.value
        elif isinstance(node, ast.Name):
            if node.id not in env:
                raise NameError('Unknown local name: ' + node.id)
            result = env[node.id]
        elif isinstance(node, (ast.List, ast.Tuple)):
            result = [evaluate(item) for item in node.elts]
            if isinstance(node, ast.Tuple):
                result = tuple(result)
        elif isinstance(node, ast.Dict):
            result = {evaluate(k): evaluate(v) for k, v in zip(node.keys, node.values)}
        elif isinstance(node, ast.BinOp):
            result = self.binary(node.op, evaluate(node.left), evaluate(node.right))
        elif isinstance(node, ast.UnaryOp):
            result = {ast.Not: operator.not_, ast.USub: operator.neg, ast.UAdd: operator.pos}[type(node.op)](evaluate(node.operand))
        elif isinstance(node, ast.BoolOp):
            result = evaluate(node.values[0])
            for value in node.values[1:]:
                if (isinstance(node.op, ast.And) and not result) or (isinstance(node.op, ast.Or) and result):
                    break
                result = evaluate(value)
        elif isinstance(node, ast.Compare):
            left, result = evaluate(node.left), True
            for op, comparison in zip(node.ops, node.comparators):
                right = evaluate(comparison)
                if not COMPARE[type(op)](left, right):
                    result = False
                    break
                left = right
        elif isinstance(node, ast.IfExp):
            result = evaluate(node.body if evaluate(node.test) else node.orelse)
        elif isinstance(node, ast.Subscript):
            value = evaluate(node.value)
            if isinstance(node.slice, ast.Slice):
                index = slice(*(evaluate(part) if part is not None else None for part in
                                (node.slice.lower, node.slice.upper, node.slice.step)))
            else:
                index = evaluate(node.slice)
            result = value[index]
        elif isinstance(node, ast.Call):
            args = [evaluate(arg) for arg in node.args]
            if isinstance(node.func, ast.Name):
                name = node.func.id
                if name in self.functions:
                    result = self.call(name, args, fuel, depth + 1)
                elif name == 'range':
                    sequence = range(*args)
                    if len(sequence) > MAX_ITEMS:
                        raise PolicyError('Range exceeds iteration limit')
                    result = list(sequence)
                elif name in BUILTINS:
                    if name == 'str' and args:
                        # Avoid recursive formatting amplification of nested containers.
                        if type(args[0]) not in (str, int, float, bool, type(None)):
                            raise PolicyError('str accepts scalars only')
                    result = BUILTINS[name](*args)
                else:
                    raise PolicyError('Call is not allowed: ' + name)
            else:
                value = evaluate(node.func.value)
                if type(value) is not str:
                    raise PolicyError('Methods are allowed only on strings')
                if node.func.attr == 'join':
                    if len(args) != 1 or type(args[0]) not in (list, tuple) or any(type(v) is not str for v in args[0]):
                        raise PolicyError('join requires a bounded string sequence')
                    if sum(map(len, args[0])) + len(value) * len(args[0]) > MAX_STRING:
                        raise PolicyError('join size exceeded')
                result = getattr(value, node.func.attr)(*args)
        elif isinstance(node, ast.ListComp):
            if len(node.generators) != 1:
                raise PolicyError('Only a single bounded comprehension is supported')
            generator = node.generators[0]
            values = evaluate(generator.iter)
            if len(values) > MAX_ITEMS:
                raise PolicyError('Comprehension limit exceeded')
            result = []
            for value in values:
                local = {**env, generator.target.id: value}
                if all(self.expression(test, local, fuel, depth) for test in generator.ifs):
                    result.append(self.expression(node.elt, local, fuel, depth))
        else:
            raise PolicyError('Unsupported expression: ' + type(node).__name__)
        return checked(result)

    def block(self, statements, env, fuel, depth):
        evaluate = lambda item: self.expression(item, env, fuel, depth)
        for node in statements:
            self.tick(fuel)
            if isinstance(node, ast.Return):
                raise Returned(evaluate(node.value) if node.value else None)
            if isinstance(node, ast.Assign):
                value = evaluate(node.value)
                for target in node.targets:
                    env[target.id] = value
            elif isinstance(node, ast.AugAssign):
                env[node.target.id] = self.binary(node.op, env[node.target.id], evaluate(node.value))
            elif isinstance(node, ast.If):
                self.block(node.body if evaluate(node.test) else node.orelse, env, fuel, depth)
            elif isinstance(node, ast.For):
                values = evaluate(node.iter)
                if len(values) > MAX_ITEMS:
                    raise PolicyError('Loop iteration limit exceeded')
                for value in values:
                    env[node.target.id] = value
                    try:
                        self.block(node.body, env, fuel, depth)
                    except LoopContinue:
                        continue
                    except LoopBreak:
                        break
                else:
                    self.block(node.orelse, env, fuel, depth)
            elif isinstance(node, ast.Break):
                raise LoopBreak()
            elif isinstance(node, ast.Continue):
                raise LoopContinue()
            elif isinstance(node, ast.Expr):
                evaluate(node.value)
            elif not isinstance(node, ast.Pass):
                raise PolicyError('Unsupported statement')


def module(name, source):
    interpreter = Interpreter(source)
    result = types.ModuleType(name)
    for function in interpreter.functions:
        def call(*args, _function=function):
            return interpreter.call(_function, args)
        setattr(result, function, call)
    return result
