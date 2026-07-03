import sys

stack = []
ret_stack = []
memory = [0]
variables = {}
fun_dict = {}
content = []

pointer = 0

builtins_ops = {
    # Math
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b if b != 0 else 0,
    '%': lambda a, b: a % b if b != 0 else 0,
    '<': lambda a, b: a < b,
    '>': lambda a, b: a > b,
    '==': lambda a, b: a == b,
    '!=': lambda a, b: a != b,
    '>=': lambda a, b: a >= b,
    '<=': lambda a, b: a <= b
}
builtins = {
    '!': lambda: memory.__setitem__(stack.pop(), stack.pop()),
    '@': lambda: stack.append(memory[stack.pop()]),
    # I/O
    '.': lambda: print(stack.pop(), end=' '),
    'print': lambda: print(stack.pop()),
    'input': lambda: stack.append(input(stack.pop())),
    # Stack
    'dup': lambda: stack.append(stack[-1]),
    'swap': lambda: stack.append(stack.pop(-2)),
    'over': lambda: stack.append(stack[-2]),
    'drop': lambda: stack.pop(),
    'depth': lambda: stack.append(len(stack)),
    'clear': lambda: stack.clear(),
    '=': lambda: _var(),
    # Types
    'int': lambda: stack.append(int(stack.pop())),
    'str': lambda: stack.append(str(stack.pop())),
    # Return stack
    '>ret': lambda: ret_stack.append(stack.pop()),
    'ret>': lambda: stack.append(ret_stack.pop()),
    'ret@': lambda: stack.append(ret_stack[-1]),
    #!
    'fun': lambda: _fun(),
    'if': lambda: _if(),
    'for': lambda: _for(),
    # Py things
    'init_mem': lambda: globals().__setitem__('memory', [0] * stack.pop()),
    'import': lambda: _import(),
}

def _var():
    global content, pointer, variables
    value, name = stack.pop(), stack.pop()
    variables[name] = value

def _fun():
    global content, pointer, fun_dict
    name, body = content[pointer + 1], content[pointer + 2]
    fun_dict[name] = body
    pointer += 1

def _if():
    global stack, content, pointer
    cond = stack.pop()
    if cond:
        run(content[pointer + 1], True)
    pointer += 1

def _for():
    global stack, content, pointer
    num = stack.pop()
    for _ in range(num):
        run(content[pointer + 1], True)
    pointer += 1

def _import():
    global content, pointer
    lib_name = content[pointer + 1]
    with open(lib_name, 'r') as f:
        run(parse(f.read()), True)
    pointer += 1

def run(parsed_code,r=False):
    "Main interpreter"
    global stack, memory, pointer

    if r:
        s_p, pointer = pointer, 0

    while pointer < len(parsed_code):

        obj = parsed_code[pointer]

        if isinstance(obj, (str, int)):
            if obj in builtins_ops:
                b = stack.pop()
                a = stack.pop()
                stack.append(builtins_ops[obj](a, b))
            elif obj in builtins:
                builtins[obj]()
            elif obj in variables:
                stack.append(variables[obj])
            elif obj in fun_dict:
                run(fun_dict[obj],True)
            else:
                stack.append(obj)
        
        pointer += 1

    if r:
        pointer = s_p

def parse(text):
    text = text.split()
    collecting = False
    temp_list = []
    result = []
    for obj in text:
        if collecting:
            if obj == '}':
                collecting = False
                result.append(temp_list.copy())
                temp_list = []
            elif obj == '/"':
                collecting = False
                result.append(' '.join(temp_list.copy()))
                temp_list = []
            elif obj == '*/':
                collecting = False
                temp_list = []
            else:
                if obj.isdigit():
                    temp_list.append(int(obj))
                else:
                    temp_list.append(obj)
        else:
            if obj.isdigit():
                result.append(int(obj))
            elif obj == '{': collecting = True
            elif obj == '"/': collecting = True
            elif obj == '/*': collecting = True
            else:
                result.append(obj)
    global content
    content = result.copy()
    return result

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage:\n    python3 {__file__} <your .oshd file>')
        sys.exit()
    with open(sys.argv[-1], 'r') as f:
        run(parse(f.read()))
