#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lime
# @Date:   2014-05-28 09:56:28
# @Last Modified by:   lime
# @Last Modified time: 2014-05-28 10:00:25

'''
Compiler for C language with python

Usage: python compiler.py -s [file] [options]

Options:
    -h, --h         show help
    -s file         import the source file, required!
    -l              lexer
    -p              parser
    -a              assembler, the assembler file is in the same path with compiler.py

Examples:
    python compiler.py -h
    python compiler.py -s source.c -a

Enjoy ^_^.
'''

import re
import sys
import getopt

TOKEN_STYLE = [
    'KEY_WORD', 'IDENTIFIER', 'DIGIT_CONSTANT',
    'OPERATOR', 'SEPARATOR', 'STRING_CONSTANT'
]

DETAIL_TOKEN_STYLE = {
    'include': 'INCLUDE',
    'int': 'INT',
    'float': 'FLOAT',
    'char': 'CHAR',
    'double': 'DOUBLE',
    'for': 'FOR',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'do': 'DO',
    'return': 'RETURN',
    '=': 'ASSIGN',
    '&': 'ADDRESS',
    '<': 'LT',
    '>': 'GT',
    '++': 'SELF_PLUS',
    '--': 'SELF_MINUS',
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'MUL',
    '/': 'DIV',
    '>=': 'GET',
    '<=': 'LET',
    '(': 'LL_BRACKET',
    ')': 'RL_BRACKET',
    '{': 'LB_BRACKET',
    '}': 'RB_BRACKET',
    '[': 'LM_BRACKET',
    ']': 'RM_BRACKET',
    ',': 'COMMA',
    '"': 'DOUBLE_QUOTE',
    ';': 'SEMICOLON',
    '#': 'SHARP',
}

keywords = [
    ['int', 'float', 'double', 'char', 'void'],
    ['if', 'for', 'while', 'do', 'else'], ['include', 'return'],
]

operators = [
    '=', '&', '<', '>', '++', '--', '+', '-', '*', '/', '>=', '<=', '!='
]

delimiters = ['(', ')', '{', '}', '[', ']', ',', '\"', ';']

file_name = None

content = None


class Token(object):

    def __init__(self, type_index, value):
        self.type = DETAIL_TOKEN_STYLE[value] if (
            type_index == 0 or type_index == 3 or type_index == 4
        ) else TOKEN_STYLE[type_index]
        self.value = value


class Lexer(object):

    def __init__(self):
        self.tokens = []

    def is_blank(self, index):
        return (
            content[index] == ' ' or
            content[index] == '\t' or
            content[index] == '\n' or
            content[index] == '\r'
        )

    def skip_blank(self, index):
        while index < len(content) and self.is_blank(index):
            index += 1
        return index

    def print_log(self, style, value):
        print '(%s, %s)' % (style, value)

    def is_keyword(self, value):
        for item in keywords:
            if value in item:
                return True
        return False

    def main(self):
        i = 0
        while i < len(content):
            i = self.skip_blank(i)
            if content[i] == '#':
                self.tokens.append(Token(4, content[i]))
                i = self.skip_blank(i + 1)
                while i < len(content):
                    if re.match('include', content[i:]):
                        self.tokens.append(Token(0, 'include'))
                        i = self.skip_blank(i + 7)
                    elif content[i] == '\"' or content[i] == '<':
                        self.tokens.append(Token(4, content[i]))
                        i = self.skip_blank(i + 1)
                        close_flag = '\"' if content[i] == '\"' else '>'
                        lib = ''
                        while content[i] != close_flag:
                            lib += content[i]
                            i += 1

                        self.tokens.append(Token(1, lib))
                        self.tokens.append(Token(4, close_flag))
                        i = self.skip_blank(i + 1)
                        break
                    else:
                        print 'include error!'
                        exit()
            elif content[i].isalpha() or content[i] == '_':
                temp = ''
                while i < len(content) and (
                        content[i].isalpha() or
                        content[i] == '_' or
                        content[i].isdigit()):
                    temp += content[i]
                    i += 1
                if self.is_keyword(temp):
                    self.tokens.append(Token(0, temp))
                else:
                    self.tokens.append(Token(1, temp))
                i = self.skip_blank(i)
            elif content[i].isdigit():
                temp = ''
                while i < len(content):
                    if content[i].isdigit() or (
                            content[i] == '.' and content[i + 1].isdigit()):
                        temp += content[i]
                        i += 1
                    elif not content[i].isdigit():
                        if content[i] == '.':
                            print 'float number error!'
                            exit()
                        else:
                            break
                self.tokens.append(Token(2, temp))
                i = self.skip_blank(i)
            elif content[i] in delimiters:
                self.tokens.append(Token(4, content[i]))
                if content[i] == '\"':
                    i += 1
                    temp = ''
                    while i < len(content):
                        if content[i] != '\"':
                            temp += content[i]
                            i += 1
                        else:
                            break
                    else:
                        print 'error:lack of \"'
                        exit()
                    self.tokens.append(Token(5, temp))
                    self.tokens.append(Token(4, '\"'))
                i = self.skip_blank(i + 1)
            elif content[i] in operators:
                if (content[i] == '+' or content[i] == '-') and (
                        content[i + 1] == content[i]):
                    self.tokens.append(Token(3, content[i] * 2))
                    i = self.skip_blank(i + 2)
                elif (content[i] == '>' or content[i] == '<') and content[i + 1] == '=':
                    self.tokens.append(Token(3, content[i] + '='))
                    i = self.skip_blank(i + 2)
                else:
                    self.tokens.append(Token(3, content[i]))
                    i = self.skip_blank(i + 1)


class SyntaxTreeNode(object):

    def __init__(self, value=None, _type=None, extra_info=None):
        self.value = value
        self.type = _type
        self.extra_info = extra_info
        self.father = None
        self.left = None
        self.right = None
        self.first_son = None
    # value

    def set_value(self, value):
        self.value = value
    # type

    def set_type(self, _type):
        self.type = _type
    # extra_info

    def set_extra_info(self, extra_info):
        self.extra_info = extra_info


class SyntaxTree(object):

    def __init__(self):
        self.root = None
        self.current = None

    def add_child_node(self, new_node, father=None):
        if not father:
            father = self.current
        new_node.father = father
        if not father.first_son:
            father.first_son = new_node
        else:
            current_node = father.first_son
            while current_node.right:
                current_node = current_node.right
            current_node.right = new_node
            new_node.left = current_node
        self.current = new_node

    def switch(self, left, right):
        left_left = left.left
        right_right = right.right
        left.left = right
        left.right = right_right
        right.left = left_left
        right.right = left
        if left_left:
            left_left.right = right
        if right_right:
            right_right.left = left


class Parser(object):

    def __init__(self):
        lexer = Lexer()
        lexer.main()
        # tokens
        self.tokens = lexer.tokens
        # tokens
        self.index = 0
        self.tree = SyntaxTree()

    def _block(self, father_tree):
        self.index += 1
        sentence_tree = SyntaxTree()
        sentence_tree.current = sentence_tree.root = SyntaxTreeNode('Sentence')
        father_tree.add_child_node(sentence_tree.root, father_tree.root)
        while True:
            sentence_pattern = self._judge_sentence_pattern()
            if sentence_pattern == 'STATEMENT':
                self._statement(sentence_tree.root)
            elif sentence_pattern == 'ASSIGNMENT':
                self._assignment(sentence_tree.root)
            elif sentence_pattern == 'FUNCTION_CALL':
                self._function_call(sentence_tree.root)
            elif sentence_pattern == 'CONTROL':
                self._control(sentence_tree.root)
            # return
            elif sentence_pattern == 'RETURN':
                self._return(sentence_tree.root)
            elif sentence_pattern == 'RB_BRACKET':
                break
            else:
                print 'block error!'
                exit()

    # include
    def _include(self, father=None):
        if not father:
            father = self.tree.root
        include_tree = SyntaxTree()
        include_tree.current = include_tree.root = SyntaxTreeNode('Include')
        self.tree.add_child_node(include_tree.root, father)
        cnt = 0
        flag = True
        while flag:
            if self.tokens[self.index] == '\"':
                cnt += 1
            if self.index >= len(self.tokens) or cnt >= 2 or self.tokens[self.index].value == '>':
                flag = False
            include_tree.add_child_node(
                SyntaxTreeNode(self.tokens[self.index].value), include_tree.root)
            self.index += 1

    def _function_statement(self, father=None):
        if not father:
            father = self.tree.root
        func_statement_tree = SyntaxTree()
        func_statement_tree.current = func_statement_tree.root = SyntaxTreeNode(
            'FunctionStatement')
        self.tree.add_child_node(func_statement_tree.root, father)
        flag = True
        while flag and self.index < len(self.tokens):
            if self.tokens[self.index].value in keywords[0]:
                return_type = SyntaxTreeNode('Type')
                func_statement_tree.add_child_node(return_type)
                func_statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}))
                self.index += 1
            elif self.tokens[self.index].type == 'IDENTIFIER':
                func_name = SyntaxTreeNode('FunctionName')
                func_statement_tree.add_child_node(
                    func_name, func_statement_tree.root)
                # extra_info
                func_statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER', {'type': 'FUNCTION_NAME'}))
                self.index += 1
            elif self.tokens[self.index].type == 'LL_BRACKET':
                params_list = SyntaxTreeNode('StateParameterList')
                func_statement_tree.add_child_node(
                    params_list, func_statement_tree.root)
                self.index += 1
                while self.tokens[self.index].type != 'RL_BRACKET':
                    if self.tokens[self.index].value in keywords[0]:
                        param = SyntaxTreeNode('Parameter')
                        func_statement_tree.add_child_node(param, params_list)
                        # extra_info
                        func_statement_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}), param)
                        if self.tokens[self.index + 1].type == 'IDENTIFIER':
                            # extra_info
                            func_statement_tree.add_child_node(SyntaxTreeNode(self.tokens[self.index + 1].value, 'IDENTIFIER', {
                                                               'type': 'VARIABLE', 'variable_type': self.tokens[self.index].value}), param)
                        else:
                            print '函数定义参数错误！'
                            exit()
                        self.index += 1
                    self.index += 1
                self.index += 1
            elif self.tokens[self.index].type == 'LB_BRACKET':
                self._block(func_statement_tree)

    def _statement(self, father=None):
        if not father:
            father = self.tree.root
        statement_tree = SyntaxTree()
        statement_tree.current = statement_tree.root = SyntaxTreeNode(
            'Statement')
        self.tree.add_child_node(statement_tree.root, father)
        tmp_variable_type = None
        while self.tokens[self.index].type != 'SEMICOLON':
            if self.tokens[self.index].value in keywords[0]:
                tmp_variable_type = self.tokens[self.index].value
                variable_type = SyntaxTreeNode('Type')
                statement_tree.add_child_node(variable_type)
                # extra_info
                statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}))
            elif self.tokens[self.index].type == 'IDENTIFIER':
                # extra_info
                statement_tree.add_child_node(SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER', {
                                              'type': 'VARIABLE', 'variable_type': tmp_variable_type}), statement_tree.root)
            elif self.tokens[self.index].type == 'DIGIT_CONSTANT':
                statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'DIGIT_CONSTANT'), statement_tree.root)
                statement_tree.current.left.set_extra_info(
                    {'type': 'LIST', 'list_type': tmp_variable_type})
            elif self.tokens[self.index].type == 'LB_BRACKET':
                self.index += 1
                constant_list = SyntaxTreeNode('ConstantList')
                statement_tree.add_child_node(
                    constant_list, statement_tree.root)
                while self.tokens[self.index].type != 'RB_BRACKET':
                    if self.tokens[self.index].type == 'DIGIT_CONSTANT':
                        statement_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, 'DIGIT_CONSTANT'), constant_list)
                    self.index += 1
            elif self.tokens[self.index].type == 'COMMA':
                while self.tokens[self.index].type != 'SEMICOLON':
                    if self.tokens[self.index].type == 'IDENTIFIER':
                        tree = SyntaxTree()
                        tree.current = tree.root = SyntaxTreeNode('Statement')
                        self.tree.add_child_node(tree.root, father)
                        variable_type = SyntaxTreeNode('Type')
                        tree.add_child_node(variable_type)
                        # extra_info
                        tree.add_child_node(
                            SyntaxTreeNode(tmp_variable_type, 'FIELD_TYPE', {'type': tmp_variable_type}))
                        tree.add_child_node(SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER', {
                                            'type': 'VARIABLE', 'variable_type': tmp_variable_type}), tree.root)
                    self.index += 1
                break
            self.index += 1
        self.index += 1

    def _assignment(self, father=None):
        if not father:
            father = self.tree.root
        assign_tree = SyntaxTree()
        assign_tree.current = assign_tree.root = SyntaxTreeNode('Assignment')
        self.tree.add_child_node(assign_tree.root, father)
        while self.tokens[self.index].type != 'SEMICOLON':
            if self.tokens[self.index].type == 'IDENTIFIER':
                assign_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER'))
                self.index += 1
            elif self.tokens[self.index].type == 'ASSIGN':
                self.index += 1
                self._expression(assign_tree.root)
        self.index += 1

    # while
    def _while(self, father=None):
        while_tree = SyntaxTree()
        while_tree.current = while_tree.root = SyntaxTreeNode(
            'Control', 'WhileControl')
        self.tree.add_child_node(while_tree.root, father)

        self.index += 1
        if self.tokens[self.index].type == 'LL_BRACKET':
            tmp_index = self.index
            while self.tokens[tmp_index].type != 'RL_BRACKET':
                tmp_index += 1
            self._expression(while_tree.root, tmp_index)

            if self.tokens[self.index].type == 'LB_BRACKET':
                self._block(while_tree)

    # for
    def _for(self, father=None):
        for_tree = SyntaxTree()
        for_tree.current = for_tree.root = SyntaxTreeNode(
            'Control', 'ForControl')
        self.tree.add_child_node(for_tree.root, father)
        while True:
            token_type = self.tokens[self.index].type
            if token_type == 'FOR':
                self.index += 1
            elif token_type == 'LL_BRACKET':
                self.index += 1
                tmp_index = self.index
                while self.tokens[tmp_index].type != 'RL_BRACKET':
                    tmp_index += 1
                self._assignment(for_tree.root)
                self._expression(for_tree.root)
                self.index += 1
                self._expression(for_tree.root, tmp_index)
                self.index += 1
            elif token_type == 'LB_BRACKET':
                self._block(for_tree)
                break
        current_node = for_tree.root.first_son.right.right
        next_node = current_node.right
        for_tree.switch(current_node, next_node)

    def _if_else(self, father=None):
        if_else_tree = SyntaxTree()
        if_else_tree.current = if_else_tree.root = SyntaxTreeNode(
            'Control', 'IfElseControl')
        self.tree.add_child_node(if_else_tree.root, father)

        if_tree = SyntaxTree()
        if_tree.current = if_tree.root = SyntaxTreeNode('IfControl')
        if_else_tree.add_child_node(if_tree.root)

        if self.tokens[self.index].type == 'IF':
            self.index += 1
            if self.tokens[self.index].type == 'LL_BRACKET':
                self.index += 1
                tmp_index = self.index
                while self.tokens[tmp_index].type != 'RL_BRACKET':
                    tmp_index += 1
                self._expression(if_tree.root, tmp_index)
                self.index += 1
            else:
                print 'error: lack of left bracket!'
                exit()

            if self.tokens[self.index].type == 'LB_BRACKET':
                self._block(if_tree)

        if self.tokens[self.index].type == 'ELSE':
            self.index += 1
            else_tree = SyntaxTree()
            else_tree.current = else_tree.root = SyntaxTreeNode('ElseControl')
            if_else_tree.add_child_node(else_tree.root, if_else_tree.root)

            if self.tokens[self.index].type == 'LB_BRACKET':
                self._block(else_tree)

    def _control(self, father=None):
        token_type = self.tokens[self.index].type
        if token_type == 'WHILE' or token_type == 'DO':
            self._while(father)
        elif token_type == 'IF':
            self._if_else(father)
        elif token_type == 'FOR':
            self._for(father)
        else:
            print 'error: control style not supported!'
            exit()

    def _expression(self, father=None, index=None):
        if not father:
            father = self.tree.root
        operator_priority = {'>': 0, '<': 0, '>=': 0, '<=': 0,
                             '+': 1, '-': 1, '*': 2, '/': 2, '++': 3, '--': 3, '!': 3}
        operator_stack = []
        reverse_polish_expression = []
        while self.tokens[self.index].type != 'SEMICOLON':
            if index and self.index >= index:
                break
            if self.tokens[self.index].type == 'DIGIT_CONSTANT':
                tree = SyntaxTree()
                tree.current = tree.root = SyntaxTreeNode(
                    'Expression', 'Constant')
                tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, '_Constant'))
                reverse_polish_expression.append(tree)
            elif self.tokens[self.index].type == 'IDENTIFIER':
                if self.tokens[self.index + 1].value in operators or self.tokens[self.index + 1].type == 'SEMICOLON':
                    tree = SyntaxTree()
                    tree.current = tree.root = SyntaxTreeNode(
                        'Expression', 'Variable')
                    tree.add_child_node(
                        SyntaxTreeNode(self.tokens[self.index].value, '_Variable'))
                    reverse_polish_expression.append(tree)
                # ID[i]
                elif self.tokens[self.index + 1].type == 'LM_BRACKET':
                    tree = SyntaxTree()
                    tree.current = tree.root = SyntaxTreeNode(
                        'Expression', 'ArrayItem')
                    tree.add_child_node(
                        SyntaxTreeNode(self.tokens[self.index].value, '_ArrayName'))
                    self.index += 2
                    if self.tokens[self.index].type != 'DIGIT_CONSTANT' and self.tokens[self.index].type != 'IDENTIFIER':
                        print 'error: 数组下表必须为常量或标识符'
                        print self.tokens[self.index].type
                        exit()
                    else:
                        tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, '_ArrayIndex'), tree.root)
                        reverse_polish_expression.append(tree)
            elif self.tokens[self.index].value in operators or self.tokens[self.index].type == 'LL_BRACKET' or self.tokens[self.index].type == 'RL_BRACKET':
                tree = SyntaxTree()
                tree.current = tree.root = SyntaxTreeNode(
                    'Operator', 'Operator')
                tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, '_Operator'))
                if self.tokens[self.index].type == 'LL_BRACKET':
                    operator_stack.append(tree.root)
                elif self.tokens[self.index].type == 'RL_BRACKET':
                    while operator_stack and operator_stack[-1].current.type != 'LL_BRACKET':
                        reverse_polish_expression.append(operator_stack.pop())
                    if operator_stack:
                        operator_stack.pop()
                else:
                    while operator_stack and operator_priority[tree.current.value] < operator_priority[operator_stack[-1].current.value]:
                        reverse_polish_expression.append(operator_stack.pop())
                    operator_stack.append(tree)
            self.index += 1
        # reverse_polish_expression
        while operator_stack:
            reverse_polish_expression.append(operator_stack.pop())

        # for item in reverse_polish_expression:
        #   print item.current.value,
        # print

        operand_stack = []
        child_operators = [['!', '++', '--'], [
            '+', '-', '*', '/', '>', '<', '>=', '<=']]
        for item in reverse_polish_expression:
            if item.root.type != 'Operator':
                operand_stack.append(item)
            else:
                if item.current.value in child_operators[0]:
                    a = operand_stack.pop()
                    new_tree = SyntaxTree()
                    new_tree.current = new_tree.root = SyntaxTreeNode(
                        'Expression', 'SingleOperand')
                    new_tree.add_child_node(item.root)
                    new_tree.add_child_node(a.root, new_tree.root)
                    operand_stack.append(new_tree)
                elif item.current.value in child_operators[1]:
                    b = operand_stack.pop()
                    a = operand_stack.pop()
                    new_tree = SyntaxTree()
                    new_tree.current = new_tree.root = SyntaxTreeNode(
                        'Expression', 'DoubleOperand')
                    new_tree.add_child_node(a.root)
                    new_tree.add_child_node(item.root, new_tree.root)
                    new_tree.add_child_node(b.root, new_tree.root)
                    operand_stack.append(new_tree)
                else:
                    print 'operator %s not supported!' % item.current.value
                    exit()
        self.tree.add_child_node(operand_stack[0].root, father)

    def _function_call(self, father=None):
        if not father:
            father = self.tree.root
        func_call_tree = SyntaxTree()
        func_call_tree.current = func_call_tree.root = SyntaxTreeNode(
            'FunctionCall')
        self.tree.add_child_node(func_call_tree.root, father)

        while self.tokens[self.index].type != 'SEMICOLON':
            if self.tokens[self.index].type == 'IDENTIFIER':
                func_call_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'FUNCTION_NAME'))
            elif self.tokens[self.index].type == 'LL_BRACKET':
                self.index += 1
                params_list = SyntaxTreeNode('CallParameterList')
                func_call_tree.add_child_node(params_list, func_call_tree.root)
                while self.tokens[self.index].type != 'RL_BRACKET':
                    if self.tokens[self.index].type == 'IDENTIFIER' or self.tokens[self.index].type == 'DIGIT_CONSTANT' or self.tokens[self.index].type == 'STRING_CONSTANT':
                        func_call_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, self.tokens[self.index].type), params_list)
                    elif self.tokens[self.index].type == 'DOUBLE_QUOTE':
                        self.index += 1
                        func_call_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, self.tokens[self.index].type), params_list)
                        self.index += 1
                    elif self.tokens[self.index].type == 'ADDRESS':
                        func_call_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, 'ADDRESS'), params_list)
                    self.index += 1
            else:
                print 'function call error!'
                exit()
            self.index += 1
        self.index += 1

    # return -->TODO
    def _return(self, father=None):
        if not father:
            father = self.tree.root
        return_tree = SyntaxTree()
        return_tree.current = return_tree.root = SyntaxTreeNode('Return')
        self.tree.add_child_node(return_tree.root, father)
        while self.tokens[self.index].type != 'SEMICOLON':
            if self.tokens[self.index].type == 'RETURN':
                return_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value))
                self.index += 1
            else:
                self._expression(return_tree.root)
        self.index += 1

    def _judge_sentence_pattern(self):
        token_value = self.tokens[self.index].value
        token_type = self.tokens[self.index].type
        # include
        if token_type == 'SHARP' and self.tokens[self.index + 1].type == 'INCLUDE':
            return 'INCLUDE'
        elif token_value in keywords[1]:
            return 'CONTROL'
        elif token_value in keywords[0] and self.tokens[self.index + 1].type == 'IDENTIFIER':
            index_2_token_type = self.tokens[self.index + 2].type
            if index_2_token_type == 'LL_BRACKET':
                return 'FUNCTION_STATEMENT'
            elif index_2_token_type == 'SEMICOLON' or index_2_token_type == 'LM_BRACKET' or index_2_token_type == 'COMMA':
                return 'STATEMENT'
            else:
                return 'ERROR'
        elif token_type == 'IDENTIFIER':
            index_1_token_type = self.tokens[self.index + 1].type
            if index_1_token_type == 'LL_BRACKET':
                return 'FUNCTION_CALL'
            elif index_1_token_type == 'ASSIGN':
                return 'ASSIGNMENT'
            else:
                return 'ERROR'
        # return
        elif token_type == 'RETURN':
            return 'RETURN'
        elif token_type == 'RB_BRACKET':
            self.index += 1
            return 'RB_BRACKET'
        else:
            return 'ERROR'

    def main(self):
        self.tree.current = self.tree.root = SyntaxTreeNode('Sentence')
        while self.index < len(self.tokens):
            sentence_pattern = self._judge_sentence_pattern()
            # include
            if sentence_pattern == 'INCLUDE':
                self._include()
            elif sentence_pattern == 'FUNCTION_STATEMENT':
                self._function_statement()
                break
            elif sentence_pattern == 'STATEMENT':
                self._statement()
            elif sentence_pattern == 'FUNCTION_CALL':
                self._function_call()
            else:
                print 'main error!'
                exit()

    # DFS
    def display(self, node):
        if not node:
            return
        print '( self: %s %s, father: %s, left: %s, right: %s )' % (node.value, node.type, node.father.value if node.father else None, node.left.value if node.left else None, node.right.value if node.right else None)
        child = node.first_son
        while child:
            self.display(child)
            child = child.right


class AssemblerFileHandler(object):

    def __init__(self):
        self.result = ['.data', '.bss', '.lcomm bss_tmp, 4', '.text']
        self.data_pointer = 1
        self.bss_pointer = 3
        self.text_pointer = 4

    def insert(self, value, _type):
        if _type == 'DATA':
            self.result.insert(self.data_pointer, value)
            self.data_pointer += 1
            self.bss_pointer += 1
            self.text_pointer += 1
        elif _type == 'BSS':
            self.result.insert(self.bss_pointer, value)
            self.bss_pointer += 1
            self.text_pointer += 1
        elif _type == 'TEXT':
            self.result.insert(self.text_pointer, value)
            self.text_pointer += 1
        else:
            print 'error!'
            exit()

    def generate_ass_file(self):
        self.file = open(file_name + '.S', 'w+')
        self.file.write('\n'.join(self.result) + '\n')
        self.file.close()


class Assembler(object):

    def __init__(self):
        self.parser = Parser()
        self.parser.main()
        self.tree = self.parser.tree
        self.ass_file_handler = AssemblerFileHandler()
        self.symbol_table = {}
        self.sentence_type = ['Sentence', 'Include', 'FunctionStatement',
                              'Statement', 'FunctionCall', 'Assignment', 'Control', 'Expression', 'Return']
        self.operator_stack = []
        self.operand_stack = []
        # label
        self.label_cnt = 0
        self.labels_ifelse = {}

    # include
    def _include(self, node=None):
        pass

    def _function_statement(self, node=None):
        current_node = node.first_son
        while current_node:
            if current_node.value == 'FunctionName':
                if current_node.first_son.value != 'main':
                    print 'other function statement except for main is not supported!'
                    exit()
                else:
                    self.ass_file_handler.insert('.globl main', 'TEXT')
                    self.ass_file_handler.insert('main:', 'TEXT')
                    self.ass_file_handler.insert('finit', 'TEXT')
            elif current_node.value == 'Sentence':
                self.traverse(current_node.first_son)
            current_node = current_node.right

    # sizeof
    def _sizeof(self, _type):
        size = -1
        if _type == 'int' or _type == 'float' or _type == 'long':
            size = 4
        elif _type == 'char':
            size = 1
        elif _type == 'double':
            size = 8
        return str(size)

    def _statement(self, node=None):
        line = None
        flag = 0
        variable_field_type = None
        variable_type = None
        variable_name = None
        current_node = node.first_son
        while current_node:
            if current_node.value == 'Type':
                variable_field_type = current_node.first_son.value
            elif current_node.type == 'IDENTIFIER':
                variable_name = current_node.value
                variable_type = current_node.extra_info['type']
                line = '.lcomm ' + variable_name + \
                    ', ' + self._sizeof(variable_field_type)
            elif current_node.value == 'ConstantList':
                line = variable_name + ': .' + variable_field_type + ' '
                tmp_node = current_node.first_son
                array = []
                while tmp_node:
                    array.append(tmp_node.value)
                    tmp_node = tmp_node.right
                line += ', '.join(array)
            current_node = current_node.right
        self.ass_file_handler.insert(
            line, 'BSS' if variable_type == 'VARIABLE' else 'DATA')
        self.symbol_table[variable_name] = {
            'type': variable_type, 'field_type': variable_field_type}

    def _function_call(self, node=None):
        current_node = node.first_son
        func_name = None
        parameter_list = []
        while current_node:
            if current_node.type == 'FUNCTION_NAME':
                func_name = current_node.value
                if func_name != 'scanf' and func_name != 'printf':
                    print 'function call except scanf and printf not supported yet!'
                    exit()
            elif current_node.value == 'CallParameterList':
                tmp_node = current_node.first_son
                while tmp_node:
                    if tmp_node.type == 'DIGIT_CONSTANT' or tmp_node.type == 'STRING_CONSTANT':
                        label = 'label_' + str(self.label_cnt)
                        self.label_cnt += 1
                        if tmp_node.type == 'STRING_CONSTANT':
                            line = label + ': .asciz "' + tmp_node.value + '"'
                            self.ass_file_handler.insert(line, 'DATA')
                        else:
                            print 'in functionc_call digital constant parameter is not supported yet!'
                            exit()
                        self.symbol_table[label] = {
                            'type': 'STRING_CONSTANT', 'value': tmp_node.value}
                        parameter_list.append(label)
                    elif tmp_node.type == 'IDENTIFIER':
                        parameter_list.append(tmp_node.value)
                    elif tmp_node.type == 'ADDRESS':
                        pass
                    else:
                        print tmp_node.value
                        print tmp_node.type
                        print 'parameter type is not supported yet!'
                        exit()
                    tmp_node = tmp_node.right
            current_node = current_node.right
        if func_name == 'printf':
            num = 0
            for parameter in parameter_list[::-1]:
                if self.symbol_table[parameter]['type'] == 'STRING_CONSTANT':
                    line = 'pushl $' + parameter
                    self.ass_file_handler.insert(line, 'TEXT')
                    num += 1
                elif self.symbol_table[parameter]['type'] == 'VARIABLE':
                    field_type = self.symbol_table[parameter]['field_type']
                    if field_type == 'int':
                        line = 'pushl ' + parameter
                        self.ass_file_handler.insert(line, 'TEXT')
                        num += 1
                    elif field_type == 'float':
                        line = 'flds ' + parameter
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = r'subl $8, %esp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = r'fstpl (%esp)'
                        self.ass_file_handler.insert(line, 'TEXT')
                        num += 2
                    else:
                        print 'field type except int and float is not supported yet!'
                        exit()
                else:
                    print 'parameter type not supported in printf yet!'
                    exit()
            line = 'call printf'
            self.ass_file_handler.insert(line, 'TEXT')
            line = 'add $' + str(num * 4) + ', %esp'
            self.ass_file_handler.insert(line, 'TEXT')
        elif func_name == 'scanf':
            num = 0
            for parameter in parameter_list[::-1]:
                parameter_type = self.symbol_table[parameter]['type']
                if parameter_type == 'STRING_CONSTANT' or parameter_type == 'VARIABLE':
                    num += 1
                    line = 'pushl $' + parameter
                    self.ass_file_handler.insert(line, 'TEXT')
                else:
                    print 'parameter type not supported in scanf!'
                    exit()
            line = 'call scanf'
            self.ass_file_handler.insert(line, 'TEXT')
            line = 'add $' + str(num * 4) + ', %esp'
            self.ass_file_handler.insert(line, 'TEXT')

    def _assignment(self, node=None):
        current_node = node.first_son
        if current_node.type == 'IDENTIFIER' and current_node.right.value == 'Expression':
            expres = self._expression(current_node.right)
            field_type = self.symbol_table[current_node.value]['field_type']
            if field_type == 'int':
                if expres['type'] == 'CONSTANT':
                    line = 'movl $' + \
                        expres['value'] + ', ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                elif expres['type'] == 'VARIABLE':
                    line = 'movl ' + expres['value'] + ', ' + '%edi'
                    self.ass_file_handler.insert(line, 'TEXT')
                    line = 'movl %edi, ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                else:
                    pass
            elif field_type == 'float':
                if expres['type'] == 'CONSTANT':
                    line = 'movl $' + \
                        expres['value'] + ', ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                    line = 'filds ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                    line = 'fstps ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                else:
                    line = 'fstps ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
            else:
                print 'field type except int and float not supported!'
                exit()
        else:
            print 'assignment wrong.'
            exit()

    # for
    def _control_for(self, node=None):
        current_node = node.first_son
        cnt = 2
        while current_node:
            # for
            if current_node.value == 'Assignment':
                self._assignment(current_node)
            # for
            elif current_node.value == 'Expression':
                if cnt == 2:
                    cnt += 1
                    line = 'label_' + str(self.label_cnt) + ':'
                    self.ass_file_handler.insert(line, 'TEXT')
                    self.label_cnt += 1
                    self._expression(current_node)
                else:
                    self._expression(current_node)
            # for
            elif current_node.value == 'Sentence':
                self.traverse(current_node.first_son)
            current_node = current_node.right
        line = 'jmp label_' + str(self.label_cnt - 1)
        self.ass_file_handler.insert(line, 'TEXT')
        line = 'label_' + str(self.label_cnt) + ':'
        self.ass_file_handler.insert(line, 'TEXT')
        self.label_cnt += 1

    # if else
    def _control_if(self, node=None):
        current_node = node.first_son
        self.labels_ifelse['label_else'] = 'label_' + str(self.label_cnt)
        self.label_cnt += 1
        self.labels_ifelse['label_end'] = 'label_' + str(self.label_cnt)
        self.label_cnt += 1
        while current_node:
            if current_node.value == 'IfControl':
                if current_node.first_son.value != 'Expression' or current_node.first_son.right.value != 'Sentence':
                    print 'control_if error!'
                    exit()
                self._expression(current_node.first_son)
                self.traverse(current_node.first_son.right.first_son)
                line = 'jmp ' + self.labels_ifelse['label_end']
                self.ass_file_handler.insert(line, 'TEXT')
                line = self.labels_ifelse['label_else'] + ':'
                self.ass_file_handler.insert(line, 'TEXT')
            elif current_node.value == 'ElseControl':
                self.traverse(current_node.first_son)
                line = self.labels_ifelse['label_end'] + ':'
                self.ass_file_handler.insert(line, 'TEXT')
            current_node = current_node.right

    # while
    def _control_while(self, node=None):
        print 'while not supported yet!'

    # return
    def _return(self, node=None):
        current_node = node.first_son
        if current_node.value != 'return' or current_node.right.value != 'Expression':
            print 'return error!'
            exit()
        else:
            current_node = current_node.right
            expres = self._expression(current_node)
            if expres['type'] == 'CONSTANT':
                line = 'pushl $' + expres['value']
                self.ass_file_handler.insert(line, 'TEXT')
                line = 'call exit'
                self.ass_file_handler.insert(line, 'TEXT')
            else:
                print 'return type not supported!'
                exit()

    def _traverse_expression(self, node=None):
        if not node:
            return
        if node.type == '_Variable':
            self.operand_stack.append(
                {'type': 'VARIABLE', 'operand': node.value})
        elif node.type == '_Constant':
            self.operand_stack.append(
                {'type': 'CONSTANT', 'operand': node.value})
        elif node.type == '_Operator':
            self.operator_stack.append(node.value)
        elif node.type == '_ArrayName':
            self.operand_stack.append(
                {'type': 'ARRAY_ITEM', 'operand': [node.value, node.right.value]})
            return
        current_node = node.first_son
        while current_node:
            self._traverse_expression(current_node)
            current_node = current_node.right

    def _is_float(self, operand):
        return operand['type'] == 'VARIABLE' and self.symbol_table[operand['operand']]['field_type'] == 'float'

    def _contain_float(self, operand_a, operand_b):
        return self._is_float(operand_a) or self._is_float(operand_b)

    def _expression(self, node=None):
        if node.type == 'Constant':
            return {'type': 'CONSTANT', 'value': node.first_son.value}
        self.operator_priority = []
        self.operand_stack = []
        self._traverse_expression(node)

        double_operators = ['+', '-', '*', '/', '>', '<', '>=', '<=']
        single_operators = ['++', '--']
        operator_map = {'>': 'jbe', '<': 'jae', '>=': 'jb', '<=': 'ja'}
        while self.operator_stack:
            operator = self.operator_stack.pop()
            if operator in double_operators:
                operand_b = self.operand_stack.pop()
                operand_a = self.operand_stack.pop()
                contain_float = self._contain_float(operand_a, operand_b)
                if operator == '+':
                    if contain_float:
                        line = 'flds ' if self._is_float(
                            operand_a) else 'filds '
                        line += operand_a['operand']
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'fadd ' if self._is_float(
                            operand_b) else 'fiadd '
                        line += operand_b['operand']
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = 'fstps bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'flds bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        self.operand_stack.append(
                            {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                        self.symbol_table['bss_tmp'] = {
                            'type': 'IDENTIFIER', 'field_type': 'float'}
                    else:
                        if operand_a['type'] == 'ARRAY_ITEM':
                            line = 'movl ' + \
                                operand_a['operand'][1] + r', %edi'
                            self.ass_file_handler.insert(line, 'TEXT')
                            line = 'movl ' + \
                                operand_a['operand'][0] + r'(, %edi, 4), %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        elif operand_a['type'] == 'VARIABLE':
                            line = 'movl ' + operand_a['operand'] + r', %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        elif operand_a['type'] == 'CONSTANT':
                            line = 'movl $' + operand_a['operand'] + r', %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        if operand_b['type'] == 'ARRAY_ITEM':
                            line = 'movl ' + \
                                operand_b['operand'][1] + r', %edi'
                            self.ass_file_handler.insert(line, 'TEXT')
                            line = 'addl ' + \
                                operand_b['operand'][0] + r'(, %edi, 4), %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        elif operand_b['type'] == 'VARIABLE':
                            line = 'addl ' + operand_b['operand'] + r', %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        elif operand_b['type'] == 'CONSTANT':
                            line = 'addl $' + operand_b['operand'] + r', %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        line = 'movl %eax, bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        self.operand_stack.append(
                            {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                        self.symbol_table['bss_tmp'] = {
                            'type': 'IDENTIFIER', 'field_type': 'int'}

                elif operator == '-':
                    if contain_float:
                        if self._is_float(operand_a):
                            if operand_a['type'] == 'VARIABLE':
                                line = 'flds ' if self._is_float(
                                    operand_a) else 'filds '
                                line += operand_a['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                pass
                        else:
                            if operand_a['type'] == 'CONSTANT':
                                line = 'movl $' + \
                                    operand_a['operand'] + ', bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                pass
                        if self._is_float(operand_b):
                            if operand_b['type'] == 'VARIABLE':
                                line = 'flds ' if self._is_float(
                                    operand_b) else 'filds '
                                line += operand_b['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                                line = 'fsub ' + operand_b['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                pass
                        else:
                            if operand_b['type'] == 'CONSTANT':
                                line = 'movl $' + \
                                    operand_b['operand'] + ', bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                                line = 'fisub bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                pass
                        line = 'fstps bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'flds bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        self.operand_stack.append(
                            {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                        self.symbol_table['bss_tmp'] = {
                            'type': 'IDENTIFIER', 'field_type': 'float'}
                    else:
                        print 'not supported yet!'
                        exit()
                elif operator == '*':
                    if operand_a['type'] == 'ARRAY_ITEM':
                        line = 'movl ' + operand_a['operand'][1] + r', %edi'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'movl ' + \
                            operand_a['operand'][0] + r'(, %edi, 4), %eax'
                        self.ass_file_handler.insert(line, 'TEXT')
                    else:
                        print 'other MUL not supported yet!'
                        exit()

                    if operand_b['type'] == 'ARRAY_ITEM':
                        line = 'movl ' + operand_b['operand'][1] + r', %edi'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'mull ' + \
                            operand_b['operand'][0] + '(, %edi, 4)'
                        self.ass_file_handler.insert(line, 'TEXT')
                    else:
                        print 'other MUL not supported yet!'
                        exit()
                    line = r'movl %eax, bss_tmp'
                    self.ass_file_handler.insert(line, 'TEXT')
                    self.operand_stack.append(
                        {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                    self.symbol_table['bss_tmp'] = {
                        'type': 'IDENTIFIER', 'field_type': 'int'}
                elif operator == '/':
                    if contain_float:
                        line = 'flds ' if self._is_float(
                            operand_a) else 'filds '
                        line += operand_a['operand']
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = 'fdiv ' if self._is_float(
                            operand_b) else 'fidiv '
                        line += operand_b['operand']
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = 'fstps bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'flds bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        self.operand_stack.append(
                            {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                        self.symbol_table['bss_tmp'] = {
                            'type': 'IDENTIFIER', 'field_type': 'float'}
                    else:
                        pass
                elif operator == '>=':
                    if contain_float:
                        if self._is_float(operand_a):
                            if operand_a['type'] == 'VARIABLE':
                                line = 'flds ' if self._is_float(
                                    operand_a) else 'filds '
                                line += operand_a['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                print 'array item not supported when >='
                                exit()
                        else:
                            pass

                        if self._is_float(operand_b):
                            if operand_b['type'] == 'VARIABLE':
                                line = 'fcom ' + operand_b['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                print 'array item not supported when >='
                                exit()
                        else:
                            if operand_b['type'] == 'CONSTANT':
                                line = 'movl $' + \
                                    operand_b['operand'] + ', bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                                line = 'fcom bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                                line = operator_map[
                                    '>='] + ' ' + self.labels_ifelse['label_else']
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                pass
                    else:
                        pass
                elif operator == '<':
                    if contain_float:
                        pass
                    else:
                        line = 'movl $' if operand_a[
                            'type'] == 'CONSTANT' else 'movl '
                        line += operand_a['operand'] + ', %edi'
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = 'movl $' if operand_b[
                            'type'] == 'CONSTANT' else 'movl '
                        line += operand_b['operand'] + ', %esi'
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = r'cmpl %esi, %edi'
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = operator_map[
                            '<'] + ' ' + 'label_' + str(self.label_cnt)
                        self.ass_file_handler.insert(line, 'TEXT')

            elif operator in single_operators:
                operand = self.operand_stack.pop()
                if operator == '++':
                    line = 'incl ' + operand['operand']
                    self.ass_file_handler.insert(line, 'TEXT')
                elif operator == '--':
                    pass
            else:
                print 'operator not supported!'
                exit()
        result = {'type': self.operand_stack[0]['type'], 'value': self.operand_stack[
            0]['operand']} if self.operand_stack else {'type': '', 'value': ''}
        return result

    def _handler_block(self, node=None):
        if not node:
            return
        if node.value in self.sentence_type:
            if node.value == 'Sentence':
                self.traverse(node.first_son)
            # include
            elif node.value == 'Include':
                self._include(node)
            elif node.value == 'FunctionStatement':
                self._function_statement(node)
            elif node.value == 'Statement':
                self._statement(node)
            elif node.value == 'FunctionCall':
                self._function_call(node)
            elif node.value == 'Assignment':
                self._assignment(node)
            elif node.value == 'Control':
                if node.type == 'IfElseControl':
                    self._control_if(node)
                elif node.type == 'ForControl':
                    self._control_for(node)
                elif node.type == 'WhileControl':
                    self._control_while()
                else:
                    print 'control type not supported!'
                    exit()
            elif node.value == 'Expression':
                self._expression(node)
            # return
            elif node.value == 'Return':
                self._return(node)
            else:
                print 'sentenct type not supported yet！'
                exit()

    def traverse(self, node=None):
        self._handler_block(node)
        next_node = node.right
        while next_node:
            self._handler_block(next_node)
            next_node = next_node.right


def lexer():
    lexer = Lexer()
    lexer.main()
    for token in lexer.tokens:
        print '(%s, %s)' % (token.type, token.value)


def parser():
    parser = Parser()
    parser.main()
    parser.display(parser.tree.root)


def assembler():
    assem = Assembler()
    assem.traverse(assem.tree.root)
    assem.ass_file_handler.generate_ass_file()

if __name__ == '__main__':
    try:
        opts, argvs = getopt.getopt(sys.argv[1:], 's:lpah', ['help'])
    except:
        print __doc__
        exit()

    for opt, argv in opts:
        if opt in ['-h', '--h', '--help']:
            print __doc__
            exit()
        elif opt == '-s':
            file_name = argv.split('.')[0]
            source_file = open(argv, 'r')
            content = source_file.read()
        elif opt == '-l':
            lexer()
        elif opt == '-p':
            parser()
        elif opt == '-a':
            assembler()
