# Author: Mason Palma
# File: obfuscator.py
# Date: 30MAY2021
# Purpose: Obfuscate your code while maintaining its functionality.
# Supported Languages: Python, Java(future), Powershell(future)

import re
import random
import sys
import os
import time
import py_compile

target_file = 'fib.py'
target_language = 'Python'

#python reg patterns
defined_function_re = '(\w*def\w*.*\(.*\)\:)'
defined_variable_re = '([a-zA-Z0-9_.]+\s\=)'
#avoid overwriting names that start with _ or __, allows _ in middle of name
good_name = '([a-zA-Z0-9][a-zA-Z0-9_]*[a-zA-Z0-9])+'

file_in_memory = ''
new_file = ''
new_file2 = ''

potential_function_names = []
potential_variables_names = []
function_symbol_table = []
variable_symbol_table = []

#for wordlists to control variable naming, else names will be randomized ascii
function_wordlist = []
variable_wordlist = []

#new names for functions and variables
new_function_names = []
new_variable_names = []

#names to not change
names_dont_change = []
bad_names_iter = ''

def import_file():
   global file_in_memory

   #import file
   with open(target_file) as file:
      file_in_memory = file.read()

#Start Python
def identify_def_functions(line):
   for words in line:
      x = re.findall(defined_function_re, line)
      for match in x:
         if '__' not in str(match):
            if str(match) not in potential_function_names:
               potential_function_names.append(str(match))

def identify_def_variables(line):
   for words in line:
      x = re.findall(defined_variable_re, line)
      for match in x:
         if str(match) not in potential_variables_names:
            potential_variables_names.append(str(match))
#End Python

def find_defined_functions():
   global file_in_memory
   global function_symbol_table
   global potential_function_names

   #cut file into lines
   for line in file_in_memory.splitlines():
      identify_def_functions(line)
   #find function names from lines
   for name in potential_function_names:
      first = name.split()
      second = first[1].split('(')
      function_symbol_table.append(second[0])


def identify_variables():
   global potential_function_names
   global variable_symbol_table
   global file_in_memory

   # cut file into lines
   for line in file_in_memory.splitlines():
      identify_def_variables(line)

   #clean variables list
   for variable in potential_variables_names:
      if '.' not in variable:
            variable_symbol_table.append(variable.split()[0])


def random_name_generator():
   name_generated = ''
   for rand in range(5, random.randint(8, 20)):
      name_generated += chr(random.randint(97, 119))

   return name_generated


def populate_names():
   global function_symbol_table
   global variable_symbol_table
   global new_function_names
   global new_variable_names

   for number in range(len(function_symbol_table)):
      new_function_names.append(random_name_generator())

   for number in range(len(variable_symbol_table)):
      new_variable_names.append(random_name_generator())


def replace_function_names():
   global file_in_memory
   global new_file
   global new_file2

   new_file = file_in_memory

   for line in new_file.splitlines():
      if 'import ' not in line:
         if '#' not in line:
            for function in range(0, len(function_symbol_table)):
               if (function_symbol_table[function]+'(') in line:
                  line = line.replace((function_symbol_table[function]+'('), (new_function_names[function]+'('))
               if ('.' + function_symbol_table[function]+'(') in line:
                  line = line.replace('.' + (function_symbol_table[function]+'('), ('.' + new_function_names[function]+'('))

      line += '\n'
      new_file2 += line

   new_file = ''


def replace_variable_names():
   global file_in_memory
   global new_file
   global new_file2

   for line in new_file2.splitlines():
      if 'import ' not in line:
         if '#' not in line:
            for variable in range(0, len(variable_symbol_table)):

               if (' ' + variable_symbol_table[variable]) in line:
                  line = line.replace((' ' + variable_symbol_table[variable]), (' ' + new_variable_names[variable]))
               if (variable_symbol_table[variable] + ')') in line:
                  line = line.replace((variable_symbol_table[variable] + ')'), (new_variable_names[variable] + ')'))
               if (variable_symbol_table[variable] + ' =') in line:
                  line = line.replace((variable_symbol_table[variable] + ' ='), (new_variable_names[variable] + ' ='))
               if (variable_symbol_table[variable] + ':') in line:
                  line = line.replace((variable_symbol_table[variable] + ':'), (new_variable_names[variable] + ':'))
               if ('[' + variable_symbol_table[variable] + ']') in line:
                  line = line.replace(('[' + variable_symbol_table[variable] + ']'), ('[' + new_variable_names[variable] + ']'))
               if ('as '+variable_symbol_table[variable] + ':') in line:
                  line = line.replace(('as ' + variable_symbol_table[variable] + ':'), ('as ' + new_variable_names[variable] + ':'))
               if (',' + variable_symbol_table[variable]) in line:
                  line = line.replace((',' + variable_symbol_table[variable]), (',' + new_variable_names[variable]))
               if ('(' + variable_symbol_table[variable] + ',') in line:
                  line = line.replace(('(' + variable_symbol_table[variable] + ','), ('(' + new_variable_names[variable] + ','))

      line += '\n'
      new_file += line


def populate_dont_change():
   global names_dont_change
   global file_in_memory

   for line in file_in_memory.splitlines():
      if 'import ' in line:
         for term in line.split():
            if '*' not in term:
               if term not in names_dont_change:
                  names_dont_change.append(term)


def main():
   global bad_names_iter
   #basic logic start
   import_file()

   #prevent library function changes
   populate_dont_change()
   bad_names_iter = iter(names_dont_change)

   #Python Syntax Dependent
   find_defined_functions()
   identify_variables()

   #Make new names
   populate_names()

   #replace functions in this order
   replace_function_names()
   replace_variable_names()

   function_symbol_table.sort()
   variable_symbol_table.sort()
   new_function_names.sort()
   new_variable_names.sort()

   file_works = False
   period = 0
   while file_works is False:

      if period > 2 or period < 0:
         period = 0

      periods = ['.', '..', '...']
      please_wait = 'Testing'

      output = (please_wait + periods[period])
      print(('\r' * len(output)) + str(output), end='')
      time.sleep(.1337)

      try:
         period += 1
         compile(new_file, 'test', 'exec')


      except (Exception, SyntaxError, NameError, ValueError) as problem:
         print(str(('\r' * len(str(problem))) + str(problem)), end='')
         main()

      else:
         file_works = True
         print()
         print("# Identified functions : %s" % function_symbol_table)
         print("# Identified variables : %s" % variable_symbol_table)
         print("# New function names : %s" % new_function_names)
         print("# New variable names : %s" % new_variable_names)
         print("# Words that wont change : %s" % names_dont_change)
         print('\n\n' + new_file)

main()

