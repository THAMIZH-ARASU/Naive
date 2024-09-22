import sys
import naive
import os

while (True):
    text = input("Naive >> ")
    if text.strip() == "":
        continue

    if text == "exit":
        exit(0)
    elif text == 'clear' or text == 'cls':
        os.system('cls')
    
    else:
        result, error = naive.run('sys.stdin', text)
        if (error): print(error.as_string())
        elif result:
            if len(result.elements) == 1:
                print(repr(result.elements[0]))
            else:
                print(repr(result))