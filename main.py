import sys
import time
import random

stack=[]
fun_stack=[]
if_stack=[]
variables={}
fun_list={}
main_edit = False
current_edit = None

def True_or_False(arg1, arg2, arg3):
    if arg3 == '>':
        return arg1 > arg2
    elif arg3 == '<':
        return arg1 < arg2
    elif arg3 == '==':
        return arg1 == arg2
    elif arg3 == '!=':
        return arg1 != arg2
    elif arg3 == '>=':
        return arg1 >= arg2
    elif arg3 == '<=':
        return arg1 <= arg2

def print_err(*args, **kwargs): print('', *args, **kwargs)
def check_for_var(arg):
    return variables.get(arg, arg)

def execute(arg):
    global main_edit, current_edit, fun_stack, if_stack, variables
    if main_edit == False:
        if arg == '+':
            b = check_for_var(stack.pop())
            a = check_for_var(stack.pop())
            try: stack.append(int(a) + int(b))
            except: print_err('f')
        elif arg == '-':
            b = check_for_var(stack.pop())
            a = check_for_var(stack.pop())
            try: stack.append(int(a) - int(b))
            except: print_err('f')
        elif arg == '*':
            b = check_for_var(stack.pop())
            a = check_for_var(stack.pop())
            try: stack.append(int(a) * int(b))
            except: print_err('f')
        elif arg == '/':
            b = stack.pop()
            a = stack.pop()
            try: stack.append(int(a) / int(b))
            except: print_err('f')
        elif arg == '=':
            value = stack.pop()
            name = stack.pop()
            try: value = int(value)
            except: pass
            variables[name] = value
            stack.append(check_for_var(value))
        elif arg == 'abs':
            stack.append(abs(check_for_var(int(stack.pop()))))
        elif arg == 'aiter':
            stack.append(aiter(stack.pop()))
        elif arg == 'print':
            print(check_for_var(stack.pop()))
        elif arg == 'get_inp':
            stack.append(input(stack.pop()))
        elif arg == 'list':
            list1 = stack.copy()
            stack.clear()
            stack.append(list1)
        elif arg == 'duplicate':
            stack.append(stack[-1])
        elif arg == 'hit':
            stack.pop()
        elif arg == 'time':
            stack.append(time.time())
        elif arg == 'wait':
            time.sleep(check_for_var(stack.pop()))
        elif arg == 'randint':
            stack.append(random.randint(1, 100))
        elif arg == 'fun':
            main_edit = True
            current_edit = 'fun'
        elif arg == 'if':
            main_edit = True
            current_edit = 'if'
        elif arg in fun_list:
            for fun_cmd in fun_list[arg].split():
                execute(fun_cmd)
        else:
            try:
                stack.append(int(arg))
            except:
                try:
                    stack.append(arg.replace('|',' '))
                except:
                    stack.append(arg)
    else:
        if arg == 'fun_end' and current_edit == 'fun':
            new_fun_name = fun_stack[0]
            fun_stack.remove(new_fun_name)
            new_fun_body = ' '.join(fun_stack)
            fun_list[new_fun_name] = new_fun_body
            fun_stack = []; main_edit = False; current_edit = None
        elif arg == 'if_end' and current_edit == 'if':
            new_if_body = if_stack[3:]
            try: arg1 = check_for_var(int(if_stack[0]))
            except: arg1 = check_for_var(if_stack[0])
            try: arg2 = check_for_var(int(if_stack[1]))
            except: arg2 = check_for_var(if_stack[1])
            op = if_stack[2]
            condition = True_or_False(arg1, arg2, op)
            if_stack = []; main_edit = False; current_edit = None
            if condition == True:
                for cmd in new_if_body:
                    execute(cmd)
        else:
            if current_edit == 'fun':
                fun_stack.append(arg)
            elif current_edit == 'if':
                if_stack.append(arg)

def process_line(line):
    line = line.strip()
    if line and not line.startswith('//'):
        commands = line.split()
        for cmd in commands:
            execute(cmd)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage')
        sys.exit(1)
    with open(sys.argv[1], 'r') as file:
        for line in file:
            process_line(line)
