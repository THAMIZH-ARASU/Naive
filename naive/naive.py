import math
from string_with_arrows import string_with_arrows
import string

#Helper constants
DIGITS = "0123456789"
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Token Types
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#data types
T_INT = 'INT'
T_FLOAT = 'FLOAT'
T_STRING = 'STRING'

#Arithmetic
T_PLUS = 'PLUS'
T_MINUS = 'MINUS'
T_MUL = 'MUL'
T_DIV = 'DIV'
T_POW = 'POW'
T_LPAREN = 'LPAREN'
T_RPAREN = 'RPAREN'
T_EQ = 'EQUALS'

#List and Indexing
T_LSQUARE = 'LSQUARE'
T_RSQUARE = 'RSQUARE'
T_LCURLY = 'LCURLY'
T_RCURLY = 'RCURLY'

#Logical
T_EE = 'EE'
T_NE = 'NE'
T_LT = 'LT'
T_GT = 'GT'
T_LTE = 'LTE'
T_GTE = 'GTE'
T_AND = 'And'
T_OR = 'Or'
T_NOT = 'Not'

#For Functions
T_COMMA = 'COMMA'
T_ARROW = 'ARROW'

#Essentials
T_EOF = 'EOF'
T_IDENTIFIER = 'IDENTIFIER'
T_STRING = 'STRING'
T_KEYWORD = 'KEYWORD'
T_NEWLINE = 'NEWLINE'
T_ERROR = 'ERROR'
T_COMMENT = 'COMMENT'
T_WHITESPACE = 'WHITESPACE'
T_SEMICOLON = 'SEMICOLON'

KEYWORDS = [
    'Elem',
    'And',
    'Or',
    'Not',
    'If',
    'Else',
    'Elif',
    'Then',
    'For',
    'While',
    'Step',
    'To',
    'Define',
    'Ends'
]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Error Class
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Error:
    def __init__(self, start_pos, end_pos, error_name, details):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.error_name = error_name
        self.details = details
    def as_string(self):
        result = f'{self.error_name}: {self.details}\n'
        result += f'File {self.start_pos.file_name}, line {self.start_pos.line + 1}'
        result += '\n\n' + string_with_arrows(self.start_pos.file_text, self.start_pos, self.end_pos)
        return result

class IllegalCharError(Error):
    def __init__(self, start_pos, end_pos, details):
        super().__init__(start_pos, end_pos, 'Illegal Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, start_pos, end_pos, details=''):
        super().__init__(start_pos, end_pos, 'Invalid Syntax', details)

class ExpectedCharError(Error):
    def __init__(self, start_pos, end_pos, details):
        super().__init__(start_pos, end_pos, 'Expected Character', details)

class RunTimeError(Error):
    def __init__(self, start_pos, end_pos, details, context):
        super().__init__(start_pos, end_pos, 'Run Time Error', details)
        self.context = context

    def as_string(self):
        result  = self.generate_traceback()
        result += f'{self.error_name}: {self.details}'
        result += '\n\n' + string_with_arrows(self.start_pos.file_text, self.start_pos, self.end_pos)
        return result
    
    def generate_traceback(self):
        result = ''
        pos = self.start_pos
        con = self.context
        
        while con:
            result = f'  File {pos.file_name}, line {str(pos.line + 1)}, in {con.display_name}\n' + result
            pos = con.parent_entry_pos
            con = con.parent
        
        return 'Traceback (most recent call last):\n' + result

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Position class to keep track of the line and column numbers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Position:
    def __init__(self, index, line, column, file_name=None, file_text=None):
        self.index = index
        self.line = line
        self.column = column
        self.file_name = file_name
        self.file_text = file_text
    def advance(self, current_char=None):
        self.index += 1
        self.column += 1
        if current_char == '\n':
            self.line += 1
            self.column = 0
        return self
    def copy(self):
        return Position(self.index, self.line, self.column, self.file_name, self.file_text)

class Token:
    def __init__(self, type_, value=None, start_pos=None, end_pos=None):
        self.type = type_
        self.value = value
        if start_pos:
            self.start_pos = start_pos.copy()
            self.end_pos = start_pos.copy()
            self.end_pos.advance()
        if end_pos:
            self.end_pos = end_pos.copy()
    
    def matches(self, type_, value):
        return self.type == type_ and self.value == value
    
    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        else:
            return f'{self.type}'

class Lexer:
    def __init__(self, file_name, text):
        self.text = text
        self.file_name = file_name
        self.pos = Position(-1, 0, -1, self.file_name, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None
    
    def generate_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char.isspace():
                self.advance()
            elif self.current_char in '$\n':
                tokens.append(Token(T_NEWLINE, start_pos=self.pos))
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char == '"':
                tokens.append(self.make_string())
            elif self.current_char == '+':
                tokens.append(Token(T_PLUS, start_pos=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(T_MINUS, start_pos=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(T_MUL, start_pos=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(T_DIV, start_pos=self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(T_POW, start_pos=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(T_LPAREN, start_pos=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(T_RPAREN, start_pos=self.pos))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(T_LSQUARE, start_pos=self.pos))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(T_RSQUARE, start_pos=self.pos))
                self.advance()
            elif self.current_char == '!':
                token, error = self.make_not_equals()
                if error: return [], error
                tokens.append(token)
            elif self.current_char == '=':
                tokens.append(self.make_equals_or_arrow())
                #tokens.append(self.make_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            elif self.current_char == ',':
                tokens.append(Token(T_COMMA, start_pos=self.pos))
                self.advance()
            
            else:
                start_pos = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(start_pos, self.pos, " '" + char + "'")
        
        tokens.append(Token(T_EOF, start_pos=self.pos))
        return tokens, None
    
    def make_number(self):
        num_str = ''
        dot_count = 0
        start_pos = self.pos.copy()
        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += self.current_char
            else:
                num_str += self.current_char
            self.advance()
        end_pos = self.pos.copy()
        if dot_count == 0:
            return Token(T_INT, int(num_str), start_pos, end_pos)
        else:
            return Token(T_FLOAT, float(num_str), start_pos, end_pos)
    
    def make_string(self):
        string = ''
        start_pos = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {
            'n': '\n',
            't': '\t'
        }
        while self.current_char != None and (self.current_char != '"' or escape_character):
            if escape_character:
                string += self.escape_chars.get(self.current_char, self.current_char)
            else:
                if self.current_char == '\\':
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()
            escape_character = False

        
        self.advance()
        return Token(T_STRING, string, start_pos, self.pos)
    
    def make_identifier(self):
        id_str = ''
        start_pos = self.pos.copy()
        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()
        
        token_type = T_KEYWORD if id_str in KEYWORDS else T_IDENTIFIER
        return Token(token_type, id_str, start_pos, self.pos)
    
    def make_not_equals(self):
        start_pos = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(T_NE, start_pos, self.pos), None
        self.advance()
        return None, ExpectedCharError(start_pos, self.pos, "'=' (after '!') ")
    
    def make_equals_or_arrow(self):
        token_type = T_EQ
        start_pos = self.pos.copy()
        self.advance()

        if self.current_char == '>':
            token_type = T_ARROW
        
        elif self.current_char == '=':
            token_type = T_EE
        self.advance()     

        return Token(token_type, start_pos, self.pos)

#    def make_equals(self):
#        token_type = T_EQ
#        start_pos = self.pos.copy()
#        self.advance()
#        if self.current_char == '=':
#            self.advance()
#            token_type = T_EE
#        return Token(token_type, start_pos, self.pos)
    
    def make_less_than(self):
        token_type = T_LT
        start_pos = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            token_type = T_LTE
        return Token(token_type, start_pos, self.pos)
    
    def make_greater_than(self):
        token_type = T_GT
        start_pos = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            token_type = T_GTE
        return Token(token_type, start_pos, self.pos)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Nodes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NumberNode:
    def __init__(self, token):
        self.token = token
        self.start_pos = self.token.start_pos
        self.end_pos = self.token.end_pos
    def __repr__(self):
        return f'{self.token}'
    

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#String Node
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class StringNode:
    def __init__(self, token):
        self.token = token
        self.start_pos = self.token.start_pos
        self.end_pos = self.token.end_pos
    def __repr__(self):
        return f'{self.token}'

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#List Node
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ListNode:
    def __init__(self, element_nodes, start_pos, end_pos):
        self.element_nodes = element_nodes
        self.start_pos = start_pos
        self.end_pos = end_pos

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#ElementAccessNode
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ElementAccessNode:
    def __init__(self, elem_name_token):
        self.elem_name_token = elem_name_token
        self.start_pos = self.elem_name_token.start_pos
        self.end_pos = self.elem_name_token.end_pos

    def __repr__(self):
        return f'{self.left_node} {self.right_node}'
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#ElemAssignNode
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ElemAssignNode:
    def __init__(self, elem_name_token, value_node):
        self.elem_name_token = elem_name_token
        self.value_node = value_node
        self.start_pos = self.elem_name_token.start_pos
        self.end_pos = self.value_node.end_pos


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#BinaryOperationNode
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BinaryOperationNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node
        self.start_pos = self.left_node.start_pos
        self.end_pos = self.right_node.end_pos


    def __repr__(self):
        return f'({self.left_node}, {self.op_token}, {self.right_node})'


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#UnaryOperationNode
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class UnaryOperationNode:
    def __init__(self, op_token, node):
        self.op_token = op_token
        self.node = node
        self.start_pos = self.op_token.start_pos
        self.end_pos = self.node.end_pos
    def __repr__(self):
        return f'({self.op_token}, {self.node})'
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#If Node
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.start_pos = self.cases[0][0].start_pos
        self.end_pos = (self.else_case or self.cases[len(self.cases) - 1])[0].end_pos
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#For Node
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ForNode:
    def __init__(self, var_name_token, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
        self.elem_name_token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.start_pos = self.elem_name_token.start_pos
        self.end_pos = self.body_node.end_pos

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#While Node
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class WhileNode:
    def __init__(self, condition_node, body_node, should_return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.start_pos = self.condition_node.start_pos
        self.end_pos = self.body_node.end_pos

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#FunctionDefinition Node
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class FunctionDefinitionNode:
    def __init__(self, func_name_token, func_params, func_body_node, should_return_null):
        self.func_name_token = func_name_token
        self.func_params = func_params
        self.func_body_node = func_body_node
        self.should_return_null = should_return_null

        if self.func_name_token:
            self.start_pos = self.func_name_token.start_pos
        elif len(self.func_params) > 0:
            self.start_pos = self.func_params[0].start_pos
        else:
            self.start_pos = self.func_body_node.start_pos

        self.end_pos = self.func_body_node.end_pos


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Call Node
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class CallNode:
    def __init__(self, node_to_call, func_params):
        self.node_to_call = node_to_call
        self.func_params = func_params

        self.start_pos = self.node_to_call.start_pos

        if len(self.func_params) > 0:
            self.end_pos = self.func_params[len(self.func_params) - 1].end_pos
        else:
            self.end_pos = self.node_to_call.end_pos


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Parse Result
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0
    
    def register_advancement(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1

    def register(self, res):
        self.last_registered_advance_count = res.advance_count
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node
    
    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Parser
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        self.update_current_token()
        return self.current_token
    
    def reverse(self, amount = 1):
        self.tok_idx -= amount
        self.update_current_token()
        return self.current_token
    
    def update_current_token(self):
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_token = self.tokens[self.tok_idx]

    def parse(self):
        res = self.statements()
        if not res.error and self.current_token.type != T_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_token.start_pos, self.current_token.end_pos,
                "Expected '+', '-', '*' or '/'"
            ))
        return res
    
    def statements(self):
        res = ParseResult()
        statements = []
        start_pos = self.current_token.start_pos.copy()

        while self.current_token.type == T_NEWLINE:
            res.register_advancement()
            self.advance()

        statement = res.register(self.expression())
        if res.error: return res
        statements.append(statement)

        more_statements = True
        while True:
            newline_count = 0
            while self.current_token.type == T_NEWLINE:
                res.register_advancement()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False
            if not more_statements: break
            statement = res.try_register(self.expression())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)
        return res.success(
            ListNode(
                statements, 
                start_pos,
                self.current_token.end_pos.copy()
            )
        )
    def list_expression(self):
        res = ParseResult()
        element_nodes = []
        start_pos = self.current_token.start_pos.copy()

        if self.current_token.type != T_LSQUARE:
            return res.failure(InvalidSyntaxError(
                self.current_token.start_pos, self.current_token.end_pos,
                "Expected '['"
            ))
        res.register_advancement()
        self.advance()
        if self.current_token.type == T_RSQUARE:
            res.register_advancement()
            self.advance()
        else:
            element_nodes.append(res.register(self.expression()))
            if res.error:
                return res.failure(InvalidSyntaxError(
                    self.current_token.start_pos, self.current_token.end_pos,
                        f"Expected ']', 'KEYWORD' ,'[' or 'Number'"
                ))
               
            while self.current_token.type == T_COMMA:
                res.register_advancement()
                self.advance()

                element_nodes.append(res.register(self.expression()))
                if res.error: return res
                
            if self.current_token.type != T_RSQUARE:
                return res.failure(InvalidSyntaxError(
                    self.current_token.start_pos, self.current_token.end_pos,
                    f"Expected ',' or ']'"
                ))
            res.register_advancement()
            self.advance()
        return res.success(
            ListNode(
                element_nodes, 
                start_pos, 
                self.current_token.end_pos.copy()
            )
        )

    
    def if_expression(self):
        res = ParseResult()
        all_cases  = res.register(self.if_expression_cases('If'))
        if res.error: return res
        cases, else_case = all_cases
        return res.success(IfNode(cases, else_case))
    
    def if_expression_b(self):
        return self.if_expression_cases('Elif')
    
    def if_expression_c(self):
        res = ParseResult()
        else_case = None

        if self.current_token.matches(T_KEYWORD, 'Else'):
            res.register_advancement()
            self.advance()

            if self.current_token.type == T_NEWLINE:
                res.register_advancement()
                self.advance()

                statements = res.register(self.statements())
                if res.error: return res
                else_case = (statements, True)

                if self.current_token.matches(T_KEYWORD, 'Ends'):
                    res.register_advancement()
                    self.advance()
                else:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.start_pos, self.current_token.end_pos,
                        f"Expected 'Ends'"
                        ))
            else:
                expression = res.register(self.expression())
                if res.error: return res
                else_case = (expression, False)
        return res.success(else_case)


    def if_expression_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_token.matches(T_KEYWORD, 'Elif'):
            all_cases = res.register(self.if_expression_b())
            if res.error: return res
            cases, else_case = all_cases
        else:
            all_cases = res.register(self.if_expression_c())
            if res.error: return res
        
        return res.success((cases, else_case))
    
    def if_expression_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None
        if not self.current_token.matches(T_KEYWORD, case_keyword):
            return res.failure(InvalidSyntaxError(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected '{case_keyword}'"
                ))
        
        res.register_advancement()
        self.advance()

        condition = res.register(self.expression())
        if res.error: return res

        if not self.current_token.matches(T_KEYWORD, 'Then'):
            return res.failure(InvalidSyntaxError(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected 'Then'"
                ))
        
        res.register_advancement()
        self.advance()

        if self.current_token.type == T_NEWLINE:
            res.register_advancement()
            self.advance()

            statements = res.register(self.statements())
            if res.error: return res
            cases.append((condition, statements, True))

            if self.current_token.matches(T_KEYWORD, 'Ends'):
                res.register_advancement()
                self.advance()
            else:
                all_cases = res.register(self.if_expression_b_or_c())
                if res.error: return res
                new_cases , else_case = all_cases
                cases.extend(new_cases)
        else:
            expression = res.register(self.expression())
            if res.error: return res
            cases.append((condition, expression, False))

            all_cases = res.register(self.if_expression_b_or_c())
            if res.error: return res
            new_cases , else_case = all_cases
            cases.extend(new_cases)
        return res.success((cases, else_case))
    
    def for_expression(self):
        res = ParseResult()

        if not self.current_token.matches(T_KEYWORD, 'For'):
            return res.failure(InvalidSyntaxError(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected 'For'"
            ))
        
        res.register_advancement()
        self.advance()

        if self.current_token.type != T_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected identifier"
            ))
        
        elem_name = self.current_token
        res.register_advancement()
        self.advance()

        if self.current_token.type != T_EQ:
            return res.failure(InvalidSyntaxError(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected '='"
            ))
        res.register_advancement()
        self.advance()

        start_value = res.register(self.expression())
        if res.error: return res

        if not self.current_token.matches(T_KEYWORD, 'To'):
            return res.failure(InvalidSyntaxError(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected 'To'"
            ))
        
        res.register_advancement()
        self.advance()

        end_value = res.register(self.expression())
        if res.error: return res

        if self.current_token.matches(T_KEYWORD, 'Step'):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expression())
            if res.error: return res
        else:
            step_value = None
        
        if not self.current_token.matches(T_KEYWORD, 'Then'):
            return res.failure(InvalidSyntaxError(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected 'Then'"
            ))
        
        res.register_advancement()
        self.advance()

        if self.current_token.type == T_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_token.matches(T_KEYWORD, 'Ends'):
                return res.failure(InvalidSyntaxError(
                    self.current_token.start_pos, self.current_token.end_pos,
                    f"Expected 'Ends'"
                ))
            
            res.register_advancement()
            self.advance()

            return res.success(
                ForNode(
                    elem_name, 
                    start_value, 
                    end_value, 
                    step_value, 
                    body, 
                    True
                )
            )
        body_expression = res.register(self.expression())
        if res.error: return res

        return res.success(
            ForNode(
                elem_name, 
                start_value, 
                end_value, 
                step_value, 
                body_expression, 
                False
            )
        )

    def while_expression(self):
        res = ParseResult()

        if not self.current_token.matches(T_KEYWORD, 'While'):
            return res.failure(InvalidSyntaxError(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected 'While'"
            ))
        
        res.register_advancement()
        self.advance()

        condition = res.register(self.expression())
        if res.error: return res

        if not self.current_token.matches(T_KEYWORD, 'Then'):
            return res.failure(InvalidSyntaxError(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected 'Then'"
            ))
        
        res.register_advancement()
        self.advance()

        if self.current_token.type == T_NEWLINE:
            res.register_advancement()
            self.advance()
            body = res.register(self.statements())
            if res.error: return res

            if not self.current_token.matches(T_KEYWORD, 'Ends'):
                return res.failure(InvalidSyntaxError(
                    self.current_token.start_pos, self.current_token.end_pos,
                    f"Expected 'Ends'"
                ))
        
            res.register_advancement()
            self.advance()

            return res.success(
                WhileNode(condition, body, True)
            )
        body_expression = res.register(self.expression())
        if res.error: return res

        return res.success(WhileNode(condition, body_expression, False))
    

    def call(self):
        res = ParseResult()
        molecule = res.register(self.molecule())
        if res.error: return res

        if self.current_token.type == T_LPAREN:
            
            res.register_advancement()
            self.advance()
            
            arg_node = []
            
            if self.current_token.type == T_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_node.append(res.register(self.expression()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.start_pos, self.current_token.end_pos,
                        f"Expected ')', 'KEYWORD' or 'Number'"
                    ))
               
                while self.current_token.type == T_COMMA:
                    res.register_advancement()
                    self.advance()
                    arg_node.append(res.register(self.expression()))
                    if res.error:
                        return res
                
                if self.current_token.type != T_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.start_pos, self.current_token.end_pos,
                        f"Expected ',', '[', KEYWORD, IDENTIFIER, Number or ')'"
                        ))
                res.register_advancement()
                self.advance()
            
            return res.success(CallNode(molecule, arg_node))
        
        return res.success(molecule)

    def molecule(self):
        res = ParseResult()
        token = self.current_token

        if token.type in (T_INT, T_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(token))
        
        if token.type == T_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(token))
        
        elif token.type == T_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(ElementAccessNode(token))
        
        elif token.type == T_LPAREN:
            res.register_advancement()
            self.advance()
            expression = res.register(self.expression())
            if res.error: return res
            if self.current_token.type == T_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expression)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_token.start_pos, self.current_token.end_pos,
                    "Expected ')'"
                    ))
        
        elif token.type == T_LSQUARE:
            list_expr = res.register(self.list_expression())
            if res.error: return res
            return res.success(list_expr)
        
        elif token.matches(T_KEYWORD, 'If'):
            if_expr = res.register(self.if_expression())
            if res.error: return res
            return res.success(if_expr)
        
        elif token.matches(T_KEYWORD, 'For'):
            for_expr = res.register(self.for_expression())
            if res.error: return res
            return res.success(for_expr)
        
        elif token.matches(T_KEYWORD, 'While'):
            while_expr = res.register(self.while_expression())
            if res.error: return res
            return res.success(while_expr)
        
        elif token.matches(T_KEYWORD, 'Define'):
            func_def = res.register(self.func_def())
            if res.error: return res
            return res.success(func_def)
            
        return res.failure(InvalidSyntaxError(
            token.start_pos, token.end_pos,
            "Expected int, float, identifier, '+', '-', '(','[', If, For, While, Define"
        ))
    
    def power(self):
        return self.BinaryOperation(self.call, (T_POW, ), self.factor)
    
    def factor(self):
        res = ParseResult()
        token = self.current_token

        if token.type in (T_PLUS, T_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOperationNode(token, factor))
        
        return self.power()
    
    def term(self):
        return self.BinaryOperation(self.factor, (T_MUL, T_DIV))
    
    def arithmetic_expression(self):
        return self.BinaryOperation(self.term, (T_PLUS, T_MINUS))
    
    def logical_expression(self):
        res = ParseResult()

        if self.current_token.matches(T_KEYWORD, 'Not'):
            op_token = self.current_token
            res.register_advancement()
            self.advance()
            node = res.register(self.logical_expression())
            if res.error: return res
            return res.success(UnaryOperationNode(op_token, node))
    
        node = res.register(self.BinaryOperation(self.arithmetic_expression, (T_EE, T_NE, T_LT, T_GT, T_LTE, T_GTE)))
        if res.error: 
            res.failure(InvalidSyntaxError(
                self.current_token.start_pos, self.current_token.end_pos,
                "Expected int, float, identifier, '+', '-', '(, '[' or 'Not'"
            ))
        return res.success(node)

    def expression(self):
        res = ParseResult()

        if self.current_token.matches(T_KEYWORD, 'Elem'):
            res.register_advancement()
            self.advance()

            if self.current_token.type != T_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_token.start_pos, self.current_token.end_pos,
                    "Expected identifier"
                ))
            elem_name = self.current_token
            res.register_advancement()
            self.advance()

            if self.current_token.type != T_EQ:
                return res.failure(InvalidSyntaxError(
                    self.current_token.start_pos, self.current_token.end_pos,
                    "Expected '='"
                ))
            res.register_advancement()
            self.advance()

            expression = res.register(self.expression())
            if res.error: return res
            return res.success(ElemAssignNode(elem_name, expression))
            
        node = res.register(self.BinaryOperation(self.logical_expression, ((T_KEYWORD, "And"),(T_KEYWORD, "Or"))))
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_token.start_pos, self.current_token.end_pos,
                "Expected 'Elem', If, For, While, Define, int, float, identifier, '+', '-', '(', '[' or NOT"
            ))
        return res.success(node)
    
    def func_def(self):
        res = ParseResult() 

        if not self.current_token.matches(T_KEYWORD, 'Define'):
            return res.failure(InvalidSyntaxError(
                self.current_token.start_pos, self.current_token.end_pos,
                "Expected 'Define'"
            ))
        res.register_advancement()
        self.advance()

        if self.current_token.type == T_IDENTIFIER:
            var_name_token = self.current_token
            res.register_advancement()
            self.advance()
            if self.current_token.type != T_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.start_pos, self.current_token.end_pos,
                    "Expected '('"
                ))
        else:
            var_name_token = None
            if self.current_token.type != T_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.start_pos, self.current_token.end_pos,
                    "Expected IDENTIFIER or '('"
                ))
        res.register_advancement()
        self.advance()

        fun_params = []
        if self.current_token.type == T_IDENTIFIER:
            fun_params.append(self.current_token)
            res.register_advancement()
            self.advance()
            while self.current_token.type == T_COMMA:
                res.register_advancement()
                self.advance()

                if self.current_token.type != T_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.start_pos, self.current_token.end_pos,
                        "Expected IDENTIFIER"
                    ))
                fun_params.append(self.current_token)
                res.register_advancement()
                self.advance()
            if self.current_token.type != T_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.start_pos, self.current_token.end_pos,
                    "Expected ',' or ')'"
                ))
            res.register_advancement()
            self.advance()
        else:
            if self.current_token.type != T_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.start_pos, self.current_token.end_pos,
                    "Expected IDENTIFIER or ')'"
                    ))
            res.register_advancement()
            self.advance()


        if self.current_token.type == T_ARROW:    
            res.register_advancement()
            self.advance()
            node_to_return = res.register(self.expression())
            if res.error:
                return res
            
            return res.success(FunctionDefinitionNode(
                var_name_token, 
                fun_params,
                node_to_return,
                False
            ))
        
        if self.current_token.type != T_NEWLINE:
            return res.failure(InvalidSyntaxError(
                self.current_token.start_pos, self.current_token.end_pos,
                "Expected '->' or NEWLINE"
                ))
        
        res.register_advancement()
        self.advance()

        body = res.register(self.statements())
        if res.error:
            return res
        
        if not self.current_token.matches(T_KEYWORD, 'Ends'):
            return res.failure(InvalidSyntaxError(
                self.current_token.start_pos, self.current_token.end_pos,
                "Expected 'Ends'"
                ))
        res.register_advancement()
        self.advance()

        return res.success(
            FunctionDefinitionNode(
                var_name_token,
                fun_params,
                body,
                True
                )
        )




        
    def BinaryOperation(self, function_a, operations, function_b=None):
        if not function_b: function_b = function_a
        res = ParseResult()
        left_node = res.register(function_a())
        if res.error: return res
        while self.current_token.type in operations or (self.current_token.type, self.current_token.value) in operations:
            op_token = self.current_token
            res.register_advancement()
            self.advance()
            right_node = res.register(function_b())
            if res.error: return res
            left_node = BinaryOperationNode(left_node, op_token, right_node)
        return res.success(left_node)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Runtime Result
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class RTResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error: self.error = res.error
        return res.value
    
    def success(self, value):
        self.value = value
        return self
    
    def failure(self, value):
        self.error = value
        return self

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Value Class
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, start_pos = None, end_pos = None):
        self.start_pos = start_pos
        self.end_pos = end_pos
        return self
    
    def set_context(self, context = None):
        self.context = context
        return self
    
    def getting(self, other):
        return None, self.illegal_operation(other)
    def added_to(self, other):
        return None, self.illegal_operation(other)
    def subtracted_by(self, other):
        return None, self.illegal_operation(other)
    def multiplied_by(self, other):
        return None, self.illegal_operation(other)
    def divided_by(self, other):
        return None, self.illegal_operation(other)
    def powered_by(self, other):
        return None, self.illegal_operation(other)
    def get_comparison_eq(self, other):
        return None, self.illegal_operation(other)
    def get_comparison_ne(self, other):
        return None, self.illegal_operation(other)
    def get_comparison_lt(self, other):
        return None, self.illegal_operation(other)
    def get_comparison_gt(self, other):
        return None, self.illegal_operation(other)
    def get_comparison_lte(self, other):
        return None, self.illegal_operation(other)
    def get_comparison_gte(self, other):
        return None, self.illegal_operation(other)
    def anded_by(self, other):
        return None, self.illegal_operation(other)
    def ored_by(self, other):
        return None, self.illegal_operation(other)
    def notted(self):
        return None, self.illegal_operation()
    def execute(self, args):
        return self.illegal_operation()
    def is_true(self):
        return False
    
    def illegal_operation(self, other = None):
        if not other: other = self
        return RunTimeError(
            self.start_pos, other.end_pos,
            "Illegal operation {0} {1}".format(self, other),
            self.context
        )

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Number Class
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()
    
    def set_pos(self, start_pos=None, end_pos=None):
        self.start_pos, self.end_pos = start_pos, end_pos
        return self
    
    def set_context(self, context=None):
        self.context = context
        return self
    
    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, other.end_pos)
    
    def subtracted_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, other.end_pos)
        
    def multiplied_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, other.end_pos)
        
    def divided_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RunTimeError(
                    other.start_pos, other.end_pos, 'Division by Zero', self.context
                )
            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, other.end_pos)
    
    def powered_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None

    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, other.end_pos)
        
    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, other.end_pos)
        
    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, other.end_pos)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, other.end_pos)
        
    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, other.end_pos)
        
    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, other.end_pos)
        
    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, other.end_pos)
    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, other.end_pos)
    def notted(self):
        return Number(int(not self.value)).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.start_pos, self.end_pos)
        copy.set_context(self.context)
        return copy
    
    def is_true(self):
        return self.value != 0
    
    def __repr__(self):
        return str(self.value)
    
Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)
Number.PI = Number(math.pi)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#List Value Class
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def added_to(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None
    
    def subtracted_by(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except IndexError:
                return None, RunTimeError(
                    other.start_pos, other.end_pos, 
                    "Element at index {} does not exist!".format(other),
                    self.context
                )
        else:
            return None, Value.illegal_operation(self, other)
    
    def multiplied_by(self, other):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, Value.illegal_operation(self, other)
        
    def divided_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RunTimeError(
                    other.start_pos, other.end_pos,
                    "Element at index {} does not exist!".format(other),
                    self.context
                )
        else:
            return None, Value.illegal_operation(self, other)
        
    def copy(self):
        copy = List(self.elements)
        copy.set_context(self.context)
        copy.set_pos(self.start_pos, self.end_pos)
        return copy
    
    def __repr__(self) :
        return f'[{", ".join([str(x) for x in self.elements])}]'
    
    def __str__(self) :
        return ", ".join([str(x) for x in self.elements])
            
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#String Value Class
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
    
    def multiplied_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
    
    def is_true(self):
        return len(self.value) > 0
    
    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.start_pos, self.end_pos)
        copy.set_context(self.context)
        return copy
    
    def __repr__(self) :
        return f'"{self.value}"'
    
    def __str__(self) :
        return self.value

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#BaseFunction Class
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or '<anonymous>'

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.start_pos)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context
    
    def check_args(self, arg_names, args):
        res = RTResult()
        if len(args) > len(arg_names):
            return res.failure(RunTimeError(
                self.start_pos, self.end_pos,
                f"{len(args) - len(arg_names)} too many args passed into {self.name}",
                self.context
            ))
        if len(args) < len(arg_names):
            return res.failure(RunTimeError(
                self.start_pos, self.end_pos,
                f"{len(arg_names) - len(args)} too few args passed into {self.name}",
                self.context
            ))
        return res.success(None)
    
    def populate_args(self, arg_names, args, exec_ctx):    
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, args_names, args, exec_ctx):
        res = RTResult()
        res.register(self.check_args(args_names, args))
        if res.error: return res
        self.populate_args(args_names, args, exec_ctx)
        return res.success(None)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Function Class
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, should_return_null):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_return_null = should_return_null

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.error: return res


        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.error:
            return res
        return res.success(value)
    
    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names, self.should_return_null)
        copy.set_context(self.context)
        copy.set_pos(self.start_pos, self.end_pos)
        return copy
    
    def __repr__(self):
        return f"<function {self.name} at {hex(id(self))}>"

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#BuiltInFunction Class
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)
    
    def execute(self, args):
        res = RTResult()
        exec_ctx = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)
        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.error: return res

        return_value = res.register(method(exec_ctx))
        if res.error:
            return res
        
        return res.success(return_value)
    
    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.start_pos, self.end_pos)
        return copy
    
    def __repr__(self) :
        return f"<built-in function {self.name} at {hex(id(self))}>"
    
    def execute_show(self, exec_ctx):
        print(str(exec_ctx.symbol_table.get('value')))
        return RTResult().success(Number.null)
    execute_show.arg_names = ['value']

    def execute_show_ret(self, exec_ctx):
        return RTResult().success(String(str(exec_ctx.symbol_table.get('value'))))
    execute_show_ret.arg_names = ['value']

    def execute_get(self, exec_ctx):
        text = input()
        return RTResult().success(String(text))
    execute_get.arg_names = []

    def execute_get_int(self, exec_ctx):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again! ")
        return RTResult().success(Number(number))
    execute_get_int.arg_names = []

    def execute_is_number(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RTResult().success(Number.true if is_number else Number.false)
    execute_is_number.arg_names = ['value']

    def execute_is_string(self, exec_ctx):
        is_string = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RTResult().success(Number.true if is_string else Number.false)
    execute_is_string.arg_names = ['value']

    def execute_is_list(self, exec_ctx):
        is_list = isinstance(exec_ctx.symbol_table.get("value"), List)
        return RTResult().success(Number.true if is_list else Number.false)
    execute_is_list.arg_names = ['value']

    def execute_is_function(self, exec_ctx):
        is_function = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
        return RTResult().success(Number.true if is_function else Number.false)
    execute_is_function.arg_names = ['value']

    def execute_append(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")
        if not isinstance(list_, List):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
                ))
        if not isinstance(value, (Number, String, List)):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "Second argument must be a string, number or list",
                exec_ctx
                ))
        
        list_.elements.append(value)
        return RTResult().success(Number.null)
    execute_append.arg_names = ['list', 'value']

    def execute_pop(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        index = exec_ctx.symbol_table.get("index")
        if not isinstance(list_, List):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
                ))
        try:
            element = list_.elements.pop(index.value)
        except:
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "List index out of range",
                exec_ctx
                ))
        return RTResult().success(Number.null if element is None else element)
    execute_pop.arg_names = ['list', 'index']

    def execute_extend(self, exec_ctx):
        listA = exec_ctx.symbol_table.get("listA")
        listB = exec_ctx.symbol_table.get("listB")
        if not isinstance(listA, List):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
                ))
        if not isinstance(listB, List):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "Second argument must be list",
                exec_ctx
                ))
        listA.elements.extend(listB.elements)
        return RTResult().success(Number.null)
    execute_extend.arg_names = ['listA', 'listB']

BuiltInFunction.show = BuiltInFunction("show")
BuiltInFunction.show_ret = BuiltInFunction("show_ret")
BuiltInFunction.get = BuiltInFunction("get")
BuiltInFunction.get_int = BuiltInFunction("get_int")
BuiltInFunction.is_number = BuiltInFunction("is_number")
BuiltInFunction.is_string = BuiltInFunction("is_string")
BuiltInFunction.is_list = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append = BuiltInFunction("append")
BuiltInFunction.pop = BuiltInFunction("pop")
BuiltInFunction.extend = BuiltInFunction("extend")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Context Class
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Context:
    def __init__(self, display_name, parent = None, parent_entry_pos = None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Symbol Table
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class SymbolTable:
    def __init__(self, parent = None):
        self.symbols = {}
        self.parent = parent
    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value
    
    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Interpreter
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)
    
    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    
    def visit_NumberNode(self, node, context):
        return RTResult().success(Number(node.token.value).set_context(context).set_pos(node.start_pos, node.end_pos))

    def visit_ElementAccessNode(self, node, context):
        res = RTResult()
        elem_name = node.elem_name_token.value
        value = context.symbol_table.get(elem_name)

        if not value:
            return res.failure(RunTimeError(
                node.start_pos, node.end_pos,
                f"'{elem_name}' is not defined", context
                ))
        value = value.copy().set_pos(node.start_pos, node.end_pos).set_context(context)
        return res.success(value)
    
    def visit_ElemAssignNode(self, node, context):
        res = RTResult()
        elem_name = node.elem_name_token.value
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res
        context.symbol_table.set(elem_name, value)

        if not value:
            return res.failure(RunTimeError(
                node.start_pos, node.end_pos,
                f"'{elem_name}' is not defined", context
                ))
        return res.success(value)
        
    def visit_BinaryOperationNode(self, node, context):
        res = RTResult()

        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res

        if node.op_token.type == T_PLUS:
            result, error = left.added_to(right)
        elif node.op_token.type == T_MINUS:
            result, error = left.subtracted_by(right)
        elif node.op_token.type == T_MUL:
            result, error = left.multiplied_by(right)
        elif node.op_token.type == T_DIV:
            result, error = left.divided_by(right)
        elif node.op_token.type == T_POW:
            result, error = left.powered_by(right)
        elif node.op_token.type == T_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_token.type == T_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_token.type == T_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_token.type == T_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_token.type == T_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_token.type == T_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_token.matches(T_KEYWORD, "And"):
            result, error = left.anded_by(right)
        elif node.op_token.matches(T_KEYWORD, "Or"):
            result, error = left.ored_by(right)
            
        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.start_pos, node.end_pos))
        
    def visit_UnaryOperationNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res
        error = None

        if node.op_token.type == T_MINUS:
            number, error = number.multiplied_by(Number(-1))
        elif node.op_token.matches(T_KEYWORD, 'Not'):
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.start_pos, node.end_pos))
        
    def visit_IfNode(self, node, context):
        res = RTResult()
        for condition, expr, should_return_null in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error: return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.error: return res
                return res.success(Number.null if should_return_null else expr_value)
            
        if node.else_case:
            expression, should_return_null = node.else_case
            else_value = res.register(self.visit(expression, context))
            if res.error: return res
            return res.success(Number.null if should_return_null else else_value)
            
        return res.success(Number.null)
    
    def visit_ForNode(self, node, context):
        res = RTResult()
        elements = []

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error: return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error: return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.error: return res
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.elem_name_token.value, Number(i))
            i += step_value.value
            elements.append(res.register(self.visit(node.body_node, context)))
            if res.error: return res
        
        return res.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_pos(node.start_pos, node.end_pos)
        )

    def visit_WhileNode(self, node, context):
        res = RTResult()
        elements = []
        while True:
            condition_value = res.register(self.visit(node.condition_node, context))
            if res.error: return res
            if not condition_value.is_true():
                break
            elements.append(res.register(self.visit(node.body_node, context)))
            if res.error: return res

        return res.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_pos(node.start_pos, node.end_pos)
        )
    
    def visit_StringNode(self, node, context):
        return RTResult().success(
            String(node.token.value).set_context(context).set_pos(node.start_pos, node.end_pos)
        )
    
    def visit_ListNode(self ,node, context):
        res = RTResult()
        element_values = []
        for element_node in node.element_nodes:
            element_values.append(res.register(self.visit(element_node, context)))
            if res.error: return res
        
        return res.success(
            List(element_values).set_context(context).set_pos(node.start_pos, node.end_pos)
        )
        
    
    def visit_FunctionDefinitionNode(self, node, context):
        res = RTResult()

        func_name = node.func_name_token.value if node.func_name_token else None
        body_node = node.func_body_node
        arg_names = [arg_name.value for arg_name in node.func_params]

        func_value = Function(func_name, body_node, arg_names, node.should_return_null).set_context(context).set_pos()

        if node.func_name_token:
            context.symbol_table.set(func_name, func_value)
        
        return res.success(func_value)
    
    def visit_CallNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.error: return res
        value_to_call = value_to_call.copy().set_pos(node.start_pos, node.end_pos)

        for arg_node in node.func_params:
            args.append(res.register(self.visit(arg_node, context)))
            if res.error: return res

        return_value = res.register(value_to_call.execute(args))
        if res.error: return res
        return_value = return_value.copy().set_pos(node.start_pos, node.end_pos).set_context(context)

        return res.success(return_value)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Run
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number.null)
global_symbol_table.set("true", Number.true)
global_symbol_table.set("false", Number.false)
global_symbol_table.set("PI", Number.PI)
global_symbol_table.set("Show", BuiltInFunction.show)
global_symbol_table.set("ShowRet", BuiltInFunction.show_ret)
global_symbol_table.set("Get", BuiltInFunction.get)
global_symbol_table.set("GetInt", BuiltInFunction.get_int)
global_symbol_table.set("IsNumber", BuiltInFunction.is_number)
global_symbol_table.set("IsString", BuiltInFunction.is_string)
global_symbol_table.set("IsList", BuiltInFunction.is_list)
global_symbol_table.set("IsFunction", BuiltInFunction.is_function)
global_symbol_table.set("Append", BuiltInFunction.append)
global_symbol_table.set("Pop", BuiltInFunction.pop)
global_symbol_table.set("Extend", BuiltInFunction.extend)



def run(file_name, text):
    # Generate the tokens
    lexer = Lexer(file_name, text)
    tokens, error = lexer.generate_tokens()
    if error:
        return None, error

    # Generate abstract syntax tree
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    #interpreting
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
