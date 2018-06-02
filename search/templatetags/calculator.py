import math


# expression computation
class Stack:
    def __init__(self):
        self.item = []

    def isEmpty(self):
        return self.item == []

    def push(self, T):
        self.item.insert(0, T)

    def pop(self):
        return self.item.pop(0)

    def peek(self):
        return self.item[0]

    def size(self):
        return len(self.item)


def isMathExpression(expr, op_math):
    token = []
    i = 0
    while i < len(expr):
        if expr[i] == ' ':
            i += 1
        elif expr[i] == '+' and ((len(token) > 0 and token[-1] == '(') or i == 0):
            token.append('u+')
            i += 1
        elif expr[i] == '-' and ((len(token) > 0 and token[-1] == '(') or i == 0):
            token.append('u-')
            i += 1

        elif expr[i].isdigit() or expr[i] == '.':
            j = i
            flot = 0
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                if expr[j] == '.':
                    if flot == 0:
                        flot = 1
                    else:
                        return False
                j += 1
            try:
                val = int(expr[i:j])
            except ValueError:
                val = float(expr[i:j])
            token.append(val)
            i = j

        elif expr[i] == '(' and len(token) > 0 and \
                (str(token[-1]).isdigit() or isinstance(token[-1], float) or token[-1] == ')'):
            token.append('*')

        elif expr[i] == '(' or expr[i] == ')' or expr[i] == '+' or \
                expr[i] == '*' or expr[i] == '-' or expr[i] == '/' or \
                expr[i] == '%' or expr[i] == '^':
            token.append(expr[i])
            i += 1

        elif expr[i] == 'x' or expr[i] == 'X':
            token.append('*')
            i += 1

        elif expr[i:i + 5].lower() in op_math:
            token.append(expr[i:i + 5].lower())
            if i + 5 >= len(expr):
                return False
            elif expr[i + 5] != '(':
                return False
            i += 5

        elif expr[i:i + 4].lower() in op_math:
            token.append(expr[i:i + 4].lower())
            if i + 4 >= len(expr):
                return False
            elif expr[i + 4] != '(':
                return False
            i += 4

        elif expr[i:i + 3].lower() in op_math:
            token.append(expr[i:i + 3].lower())
            if i + 3 >= len(expr):
                return False
            elif expr[i + 3] != '(':
                return False
            i += 3

        else:
            return False
    return token


def calculate(val1, val2, op):
    if op == 'u-':
        return -val1
    if op == 'u+':
        return val1
    if op == '^':
        return math.pow(val1, val2)
    if op == '+':
        return val1 + val2
    if op == '-':
        return val1 - val2
    if op == '*':
        return val1 * val2
    if op == '/':
        return val1 / val2
    if op == '%':
        return val1 % val2
    if op == 'sin':
        return math.sin(val1)
    if op == 'cos':
        return math.cos(val1)
    if op == 'tan':
        return math.tan(val1)
    if op == 'cot':
        return 1 / math.tan(val1)
    if op == 'cosec':
        return 1 / math.sin(val1)
    if op == 'sec':
        return 1 / math.cos(val1)
    if op == 'exp':
        return math.exp(val1)
    if op == 'sqrt':
        return math.sqrt(val1)
    if op == 'log':
        return math.sqrt(val1)


def check_precedence(opr, i, op_precdn, op_math):
    if opr in op_precdn and i in op_math:
        return True
    if op_precdn.index(opr) <= 2:
        return True
    if op_precdn.index(opr) <= 5:
        return op_precdn.index(i) > 2
    else:
        return op_precdn.index(i) > 5


def evaluate(tokens, op_precdn, op_math):
    value = Stack()
    operator = Stack()
    open_bracket = 0
    for i in tokens:
        if i == '(':
            open_bracket = open_bracket + 1
            operator.push(i)
        elif i == ')':
            if open_bracket > 0:
                while operator.peek() != '(':
                    opr = operator.pop()
                    if opr in op_math or opr == 'u+' or opr == 'u-':
                        try:
                            val = value.pop()
                            value.push(calculate(val, -1, opr))
                        except IndexError:
                            return False
                    elif opr in op_precdn:
                        try:
                            val2 = value.pop()
                            val1 = value.pop()
                            value.push(calculate(val1, val2, opr))
                        except IndexError:
                            return False
                operator.pop()
                open_bracket -= 1
            else:
                return False
        elif i not in op_math and i not in op_precdn:
            value.push(i)
        else:
            if operator.isEmpty():
                operator.push(i)
            else:
                opr = operator.peek()
                if opr == '(':
                    operator.push(i)
                elif opr in op_math or opr == 'u+' or opr == 'u-':
                    if not value.isEmpty():
                        try:
                            val = value.pop()
                            operator.pop()
                            operator.push(i)
                            value.push(calculate(val, -1, opr))
                        except IndexError:
                            return False
                elif opr in op_precdn:
                    if value.size() > 1:
                        if check_precedence(opr, i, op_precdn, op_math) and \
                                not ((i == '^' or i in op_math) and opr == '^'):
                            try:
                                val2 = value.pop()
                                val1 = value.pop()
                                operator.pop()
                                value.push(calculate(val1, val2, opr))
                            except IndexError:
                                return False
                            operator.push(i)
                        else:
                            operator.push(i)
                    else:
                        operator.push(i)
                else:
                    return False

    while value.size() != 0 and operator.size() != 0:
        opr = operator.peek()
        if opr in op_math or opr == 'u+' or opr == 'u-':
            val = value.pop()
            operator.pop()
            try:
                value.push(calculate(val, -1, opr))
            except IndexError:
                return False
        else:
            if value.size() > 1:
                try:
                    val2 = value.pop()
                    val1 = value.pop()
                    operator.pop()
                    value.push(calculate(val1, val2, opr))
                except IndexError:
                    return False
            else:
                break

    if value.size() == 1 and operator.size() == 0:
        return value.peek()
    else:
        return False


def getResult(expr):
    op_precdn = ['u+', 'u-', '^', '/', '*', '%', '+', '-']
    op_math = ['sin', 'cos', 'cosec', 'tan', 'sec', 'cot', 'exp', 'sqrt', 'log']
    tokens = isMathExpression(expr, op_math)
    if tokens:
        return round(evaluate(tokens, op_precdn, op_math), 3)
    else:
        return None
