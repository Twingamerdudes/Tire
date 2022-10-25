variables = {}
functions = {}
skipElseStatment = False
returnValue = ""
returnType = ""
lineNum = 1
line = ""
from msilib.schema import ControlCondition
from os import system
import os
import temp as tmp

from Util import isfloat, print_error_msg
def print_error(message):
    print_error_msg(message + ". Found at line " + str(lineNum))
def handleMath(tokens, pos, offset=3):
    num1 = 0
    operator = ""
    num2 = 0
    result = None
    try:
        if tokens[pos+offset+1]["type"] != "math" and tokens[pos+offset+1] == "operator":
            exit(1)
        if tokens[pos+offset]["value"] in variables:
            num1 = int(variables[tokens[pos+offset]["value"]])
        else:
            num1 = int(tokens[pos+offset]["value"])
        if tokens[pos+offset+2]["value"] in variables:
            num2 = int(variables[tokens[pos+offset+2]["value"]])
        else:
            num2 = int(tokens[pos+offset+2]["value"])
        operator = tokens[pos+offset+1]["value"]
    except:
        if tokens[pos+offset+1]["type"] != "math" and tokens[pos+offset+1] == "operator":
            print_error("Error: Invalid operator: " + tokens[pos+offset+1]["value"])
    if operator == "+":
        result = str(num1 + num2)
    elif operator == "-":
        result = str(num1 - num2)
    elif operator == "*":
        result = str(num1 * num2)
    elif operator == "/":
        result = str(num1 / num2)
    elif operator == "%":
        result = str(num1 % num2)
    elif operator == "**":
        result = str(num1 ** num2)
    return result
def handleDots(tokens, pos, offset=0):
    item = tokens[pos + 1 + offset]["value"].split(".")[1]
    var = variables[tokens[pos + 1 + offset]["value"].split(".")[0]]
    value = ""
    for i in range(len(var)):
        try:
            temp = var[i].index(item)
            value = var[i][1]
            break
        except:
            pass
    return value
class Tire:
    def __init__(self, code, inFunction=False, Importing=False):
        self.code = code.replace("(", " ").replace(")", " ").replace("{", " ").replace("}", "end ").replace(",", " ")
        self.code += "\0"
        self.inFunction = inFunction
        self.stopExecution = False
        self.indentLevel = 0
        self.Importing = Importing
    def tokinize(self):
        length = len(self.code)
        pos = 0
        tokens = []
        keywords = ["Print", "var", "Exit", "if", "end", "else", "Input", "Import", "Fn", "Call", "forever", 
        "Python", "System", "return", "Loop", "Output", "Struct"]
        varChars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@$_-.,\\'
        operators = ["=", "==", ">", "<"]
        mathOperators = ["+", "-", "*", "/", "%", "+="]
        breakCharacter = "\\"
        while pos < length:
            currentChar = self.code[pos]
            if currentChar == " " or currentChar == "\n" or currentChar == "\0" or currentChar == "\t":
                if currentChar == "\n":
                    tokens.append({'type': "newline", 'value': ""})
                pos += 1
                continue
            elif currentChar == "\"":
                res = ""
                pos += 1
                while self.code[pos] != "\n" and pos < length:
                    if self.code[pos] == "\"" and self.code[pos-1] != breakCharacter:
                        break
                    if self.code[pos] != breakCharacter:
                        res += self.code[pos]
                    pos += 1
                if self.code[pos] != "\"":
                    print_error(f"Error: Unterminated String \"{res}\"")
                pos += 1
                tokens.append({'type': "string", 'value': res})
            elif currentChar in varChars:
                res = currentChar
                pos += 1
                numbers = "123456789"
                while self.code[pos] in varChars or self.code[pos] in numbers:
                    res += self.code[pos]
                    pos += 1
                if not res in keywords:
                    tokens.append({'type': "other", 'value': res})
                    continue
                tokens.append({'type': "keyword", 'value': res})
            elif currentChar.isnumeric():
                res = currentChar
                pos += 1
                while self.code[pos].isnumeric() or self.code[pos] == ".":
                    res += self.code[pos]
                    pos += 1
                if self.code[pos-1] == "." and not self.code[pos].isnumeric():
                    print_error(f"Error: Invalid Float \"{res}\"")
                pos += 1
                tokens.append({'type': "number", 'value': res})
            elif currentChar in operators:
                if currentChar == "=" and self.code[pos+1] == "=":
                    tokens.append({'type': "operator", 'value': "=="})
                    pos += 1
                else:
                    tokens.append({'type': "operator", 'value': currentChar})
                pos += 1
            elif currentChar in mathOperators:
                if currentChar == "+" and self.code[pos+1] == "=":
                    tokens.append({'type': "operator", 'value': "+="})
                    pos += 1
                elif currentChar == "*" and self.code[pos+1] == "*":
                    tokens.append({'type': "math", 'value': "**"})
                    pos += 1
                else:
                    tokens.append({'type': "math", 'value': currentChar})
                pos += 1
            else:
                print_error(f"Error: Unexpected character \"{self.code[pos]}\"")
        tokens.append({'type': "eof", 'value': ""})
        return tokens
    def parse(self, tokens):
        length = len(tokens)
        pos = 0
        global skipElseStatment
        global returnValue
        global returnType
        global lineNum
        while pos < length:
            if self.stopExecution and not self.Importing:
                return
            token = tokens[pos]
            if token["type"] == "newline":
                lineNum += 1
                pos += 1
                continue
            if token["type"] == "keyword":
                if token["value"] == "Print":
                    missing = False
                    try:
                        temp = tokens[pos + 1]
                    except:
                        missing = True
                    if missing == True:
                        print_error("Error: Unexpected end of line, expected string")
                    isString = tokens[pos + 1]["type"] == "string"
                    isChild = tokens[pos + 1]["value"].split(".")[0] in variables and"." in tokens[pos + 1]["value"]
                    if not isString and not tokens[pos + 1]["value"] in variables and tokens[pos + 1]["type"] != "number" and not isChild:
                        print_error("Error: Unexpected token \"" + tokens[pos + 1]["value"] + "\", expected a string, number, or variable")
                    if isString:
                        print(tokens[pos + 1]["value"])
                    elif tokens[pos + 1]["type"] == "number":
                        sum = handleMath(tokens, pos, 1)
                        if sum != None:
                            print(sum)
                            tokens[pos + 2]["value"] = ""
                            tokens[pos + 3]["value"] = ""
                            tokens[pos + 2]["type"] = "ignore"
                            tokens[pos + 3]["type"] = "ignore"
                    else:
                        if not "." in tokens[pos + 1]["value"]:
                            print(variables[tokens[pos + 1]["value"]])
                        else:
                            print(handleDots(tokens, pos))
                    pos += 2
                elif token["value"] == "var":
                    missing = False
                    try:
                        temp = tokens[pos + 1]
                        temp = tokens[pos + 2]
                        temp = tokens[pos + 3]
                    except:
                        missing = True
                    if missing == True:
                        print_error("Error: Unexpected end of line, expected 2 arguments (name, value)")
                    if tokens[pos + 2]["value"] != "=":
                        print_error("Error: Forgotten operator \"=\"")
                    isString = tokens[pos + 3]["type"] == "string"
                    if tokens[pos+3]["type"] == "number":
                        try:
                            if tokens[pos+3]["value"] == "=":
                                pass
                            else:
                                variables[tokens[pos + 1]["value"]] = tokens[pos + 3]["value"]
                                pos += 4
                                continue
                        except:
                            variables[tokens[pos + 1]["value"]] = tokens[pos + 3]["value"]
                            pos += 4
                            continue
                        sum = handleMath(tokens, pos)
                        if sum != None:
                            tokens[pos + 3]["value"] = sum
                            tokens[pos + 4]["value"] = ""
                            tokens[pos + 5]["value"] = ""
                            tokens[pos + 4]["type"] = "ignore"
                            tokens[pos + 5]["type"] = "ignore"
                    if tokens[pos+3]["value"] in functions:
                        tire = Tire(functions[tokens[pos+3]["value"]], True)
                        index = 1
                        name = tokens[pos + 1]["value"]
                        while tokens[pos+4]["type"] != "keyword" and tokens[pos+4]["type"] != "other" and tokens[pos+4]["type"] != "eof" and tokens[pos+4]["type"] != "newline":
                            if tokens[pos]["type"] == "newline":
                                lineNum += 1
                            tire.code = tire.code.replace("$" + str(index), tokens[pos+4]["value"])
                            pos += 1
                            index += 1
                        tire.run()
                        variables[name] = returnValue
                        tokens[pos + 3]["type"] = returnType
                        pos += 4
                        continue
                    if tokens[pos + 3]["value"] in variables:
                        variables[tokens[pos + 1]["value"]] = variables[tokens[pos + 3]["value"]]
                        pos += 4
                        continue
                    if tokens[pos + 3]["type"] == "keyword" and tokens[pos + 3]["value"] == "Output":
                        variables[tokens[pos + 1]["value"]] = tmp.getTemp()
                        pos += 4
                        continue
                    if "." in tokens[pos + 3]["value"]:
                        variables[tokens[pos + 1]["value"]] = handleDots(tokens, pos, 2)
                        pos += 4
                        continue
                    if not isString and not tokens[pos + 3]["value"].isnumeric() and not isfloat(tokens[pos + 3]["value"]):
                        print_error("Error: Expected string, int, float, or function. Got type: " + tokens[pos + 3]["type"] + " instead.")
                    variables[tokens[pos + 1]["value"]] = tokens[pos + 3]["value"]
                    pos += 4
                elif token["value"] == "Exit":
                    try:
                        if not tokens[pos + 1]:
                            exit(0)
                        else:
                            exit(tokens[pos + 1])
                    except:
                        exit(0)
                elif token["value"] == "if":
                    missing = False
                    try:
                        temp = tokens[pos + 1]
                        temp = tokens[pos + 2]
                        temp = tokens[pos + 3]
                    except:
                        missing = True
                    if missing == True:
                        print_error("Error: Unexpected end of line, expected 2 arguments (comparsion 1, comparsion 2)")
                    isTrue = False
                    temp = tokens[pos + 1]["value"]
                    temp2 = tokens[pos + 3]["value"]
                    if temp in variables:
                        temp = variables[temp]
                        if not type(temp) == int:
                            if temp.isnumeric():
                                temp = int(temp) 
                    if temp2 in variables:
                        temp2 = variables[temp2]
                        if not type(temp2) == int:
                            if temp2.isnumeric():
                                temp2 = int(temp2)
                    try:
                        if "." in temp:
                            temp = handleDots(tokens, pos)
                            if not type(temp) == int:
                                if temp.isnumeric():
                                    temp = int(temp)
                        if "." in temp2:
                            temp2 = handleDots(tokens, pos, 3)
                            if not type(temp) == int:
                                if temp.isnumeric():
                                    temp = int(temp)
                    except:
                        pass
                    if tokens[pos + 1]["value"].isnumeric():
                        temp = int(temp)
                    if tokens[pos + 3]["value"].isnumeric():
                        temp2 = int(temp2)
                    if tokens[pos + 1]["type"] == "other":
                        if not tokens[pos + 1]["value"] in variables and not "." in tokens[pos + 1]["value"]:
                            print_error("Error: " + tokens[pos + 1]["value"] + " is unknown")
                        elif "." in tokens[pos + 1]["value"]:
                            if not tokens[pos + 1]["value"].split(".")[0] in variables:
                                print_error("Error: " + tokens[pos + 1]["value"] + " is unknown")
                    if tokens[pos + 3]["type"] == "other":
                        if not tokens[pos + 3]["value"] in variables and not "." in tokens[pos + 1]["value"]:
                            print_error("Error: " + tokens[pos + 3]["value"] + " is unknown")
                        elif "." in tokens[pos + 3]["value"]:
                            if not tokens[pos + 3]["value"].split(".")[0] in variables:
                                print_error("Error: " + tokens[pos + 3]["value"] + " is unknown")
                    if temp in variables:
                        temp = variables[temp]
                        if temp.isnumeric():
                           temp = int(temp) 
                    if temp2 in variables:
                        temp2 = variables[temp2]
                        if temp2.isnumeric():
                           temp2 = int(temp2) 
                    if tokens[pos + 2]["value"] == "==":
                        isTrue = temp == temp2
                    elif tokens[pos + 2]["value"] == "<":
                        if not str(temp).isnumeric() or not str(temp2).isnumeric() and not isfloat(str(temp)) or not isfloat(str(temp)):
                            print_error("Error: Both comparsions must be numbers when using > or <")
                        isTrue = temp < temp2
                    elif tokens[pos + 2]["value"] == ">":
                        if not str(temp).isnumeric() or not str(temp2).isnumeric() and not isfloat(str(temp)) or not isfloat(str(temp)):
                            print_error("Error: Both comparsions must be numbers when using > or <")
                        isTrue = temp > temp2
                    else:
                        print_error("Error: Invalid Operator " + tokens[pos + 2]["value"])
                    if not isTrue:
                        temp3 = self.indentLevel
                        lineNum += 1
                        pos += 4
                        while True:
                            if tokens[pos]["value"] == "end" and temp3 == self.indentLevel:
                                self.indentLevel -= 1
                                break
                            if tokens[pos]["value"] == "end":
                                self.indentLevel -= 1
                            if tokens[pos]["value"] == "if":
                                self.indentLevel += 1
                            if tokens[pos]["value"] == "Struct":
                                self.indentLevel += 1
                            if tokens[pos]["value"] == "Loop":
                                self.indentLevel += 1
                            if tokens[pos]["type"] == "newline":
                                lineNum += 1
                            pos += 1
                    else:
                        skipElseStatment = True
                        self.indentLevel += 1
                        pos += 4
                elif token["value"] == "else" and skipElseStatment == True:
                    self.indentLevel -= 1
                    temp = self.indentLevel
                    while True:
                        if tokens[pos]["value"] == "end" and temp == self.indentLevel:
                            self.indentLevel -= 1
                            break
                        if tokens[pos]["value"] == "end":
                            self.indentLevel -= 1
                        if tokens[pos]["value"] == "if":
                                self.indentLevel += 1
                        if tokens[pos]["value"] == "Struct":
                            self.indentLevel += 1
                        if tokens[pos]["value"] == "Loop":
                                self.indentLevel += 1
                        if tokens[pos]["type"] == "newline":
                            lineNum += 1
                        pos += 1
                    pos += 1
                    skipElseStatment = False
                elif token["value"] == "Input":
                    missing = False
                    try:
                        temp = tokens[pos + 1]
                        temp = tokens[pos + 2]
                    except:
                        missing = True
                    if missing == True:
                        print_error("Error: Unexpected end of line, expected 2 arguments (variable, string)")
                    variables[tokens[pos + 1]["value"]] = input(tokens[pos + 2]["value"])
                    pos += 3
                elif token["value"] == "Import":
                    tire = Tire(open(tokens[pos+1]['value'].replace("-","/") + ".tire").read(), True, True)
                    tire.run()
                    pos += 2
                elif token["value"] == "Fn":
                    name = tokens[pos+1]["value"]
                    definition = ""
                    lineNum += 1
                    pos += 2
                    temp = self.indentLevel
                    while True:
                        if tokens[pos]["value"] == "end" and temp == self.indentLevel:
                            self.indentLevel -= 1
                            break
                        if tokens[pos]["value"] == "end":
                            self.indentLevel -= 1
                        if tokens[pos]["value"] == "if":
                            self.indentLevel += 1
                        if tokens[pos]["value"] == "Loop":
                            self.indentLevel += 1
                        if tokens[pos]["value"] == "Struct":
                            self.indentLevel += 1
                        if tokens[pos]["type"] == "string":
                            definition += "\""+ tokens[pos]["value"] + "\"" + " "
                        else:
                            definition += tokens[pos]["value"] + " "
                        if tokens[pos]["type"] == "newline":
                            lineNum += 1
                        pos += 1
                    functions[name] = definition.replace("(", " ").replace(")", " ").replace("{", " ").replace("}", "end").replace(",", " ")
                elif token["value"] == "Call":
                    if tokens[pos+1]["value"] in functions:
                        tire = Tire(functions[tokens[pos+1]["value"]], True)
                        index = 1
                        while tokens[pos+2]["type"] != "keyword" and tokens[pos+2]["type"] != "other" and tokens[pos+2]["type"] != "eof" and tokens[pos+2]["type"] != "newline":
                            if tokens[pos+2]["type"] != "string":
                                tire.code = tire.code.replace("$" + str(index), tokens[pos+2]["value"])
                            else:
                                tire.code = tire.code.replace("$" + str(index), "\"" + tokens[pos+2]["value"] + "\"")
                            if tokens[pos+2]["type"] == "newline":
                                lineNum += 1
                            pos += 1
                            index += 1                 
                    else:
                        print_error("Function does not exist")
                    tire.run()
                    pos += 2
                elif token["value"] == "Python":
                    if tokens[pos+1]["type"] != "string":
                        print_error("Error: Expected string, got type \"" + tokens[pos+1]["type"] + "\" instead")
                    exec(open(tokens[pos+1]["value"].replace("-","/")).read())
                    pos += 2
                elif token["value"] == "System":
                    if tokens[pos+1]["type"] != "string":
                        print_error("Error: Expected string, got type \"" + tokens[pos+1]["type"] + "\" instead")
                    system(tokens[pos+1]["value"])
                    pos += 2
                elif token["value"] == "return":
                    if not self.inFunction:
                        print_error("Error: Return used outside of a function")
                    returnValue = tokens[pos+1]["value"]
                    returnType = tokens[pos+1]["type"]
                    if returnValue in variables:
                        returnValue = variables[returnValue]
                        returnType = "ignore"
                    if returnType != "string" and returnType != "number" and returnType != "ignore":
                        if "." in returnValue and returnType == "other":
                            returnValue = handleDots(tokens, pos)
                            pos += 2
                            self.stop()
                            continue
                        pos += 1
                        self.stop()
                        continue
                    else:
                        if returnType == "number":
                            sum = handleMath(tokens, pos, 1)
                            if sum != None:
                                returnValue = sum
                                tokens[pos + 2]["value"] = ""
                                tokens[pos + 3]["value"] = ""
                                tokens[pos + 2]["type"] = "ignore"
                                tokens[pos + 3]["type"] = "ignore"
                        returnType = tokens[pos+1]["type"]
                        pos += 2
                        self.stop()
                elif token["value"] == "Loop":
                    code = ""
                    temp = self.indentLevel
                    variables["i"] = 0
                    times = tokens[pos+1]["value"]
                    lineNum += 1
                    pos += 2
                    while True:
                        if tokens[pos]["value"] == "end" and temp == self.indentLevel:
                            self.indentLevel -= 1
                            break
                        if tokens[pos]["value"] == "end":
                            self.indentLevel -= 1
                        if tokens[pos]["value"] == "if":
                            self.indentLevel += 1
                        if tokens[pos]["value"] == "Loop":
                            self.indentLevel += 1
                        if tokens[pos]["value"] == "Struct":
                            self.indentLevel += 1
                        if tokens[pos]["type"] == "newline":
                            lineNum += 1
                        if tokens[pos]["type"] == "string":
                            code += "\""+ tokens[pos]["value"] + "\"" + " "
                        else:
                            code += tokens[pos]["value"] + " "
                        pos += 1
                    tire = Tire(code.replace("(", " ").replace(")", " ").replace("{", " ").replace("}", "end").replace(",", " ") + "\0")
                    if self.inFunction:
                        tire.inFunction = True
                    if not times == "forever":
                        for i in range(int(times)):
                            variables["i"] = i
                            tire.run()
                    else:
                        i = 0
                        while True:
                            variables["i"] = i
                            i += 1
                            tire.run()
                elif token["value"] == "Struct":
                    code = []
                    temp = self.indentLevel
                    name = tokens[pos+1]["value"]
                    lineNum += 1
                    pos += 2
                    while True:
                        if tokens[pos]["value"] == "end" and temp == self.indentLevel:
                            self.indentLevel -= 1
                            break
                        if tokens[pos]["value"] == "end":
                            self.indentLevel -= 1
                        if tokens[pos]["value"] == "if":
                            self.indentLevel += 1
                        if tokens[pos]["value"] == "Loop":
                            self.indentLevel += 1
                        if tokens[pos]["type"] == "newline":
                            lineNum += 1
                        code += [tokens[pos]["value"]]
                        pos += 1
                    temp = []
                    index = 0
                    times = 0
                    while True:
                        if index >= len(code):
                            break
                        if index == times:
                            temp += [[code[index], code[index+2]]]
                            times = index + 3
                        index += 1
                    variables[name] = temp
                else:
                    pos += 1
            elif token["type"] == "other" and token["value"] in variables:
                missing = False
                try:
                    temp = tokens[pos + 1]
                    temp = tokens[pos + 2]
                except:
                    missing = True
                if missing == True:
                    print_error("Error: Unexpected end of line, expected 1 argument (value)")
                if tokens[pos + 1]["value"] != "=" and tokens[pos + 1]["value"] != "+=":
                        print_error("Error: Forgotten operator \"=\"/\"+=\"")
                if tokens[pos + 1]["value"] == "+=":
                    if tokens[pos + 2]["type"] == "string":
                        variables[tokens[pos]["value"]] = variables[tokens[pos]["value"]] + tokens[pos + 2]["value"]
                        pos += 3
                        continue
                    elif tokens[pos + 2]["value"] in variables:
                        variables[tokens[pos]["value"]] = variables[tokens[pos]["value"]] + variables[tokens[pos + 2]["value"]]
                        pos += 3
                        continue
                    else:
                        print_error("Error: Expected string or variable, got type " + tokens[pos + 2]["type"] + " instead")
                if not tokens[pos + 2]["value"] in variables:
                    variables[tokens[pos]["value"]] = tokens[pos + 2]["value"]
                    if tokens[pos+2]["type"] == "number":
                        sum = handleMath(tokens, pos, 2)
                        if sum != None:
                            tokens[pos + 2]["value"] = sum
                            tokens[pos + 3]["value"] = ""
                            tokens[pos + 4]["value"] = ""
                            tokens[pos + 3]["type"] = "ignore"
                            tokens[pos + 4]["type"] = "ignore"
                        variables[tokens[pos]["value"]] = sum
                        pos += 3
                        continue
                    if tokens[pos+2]["value"] in functions:
                        tire = Tire(functions[tokens[pos+2]["value"]], True)
                        index = 1
                        name = tokens[pos + 1]["value"]
                        while tokens[pos+4]["type"] != "keyword" and tokens[pos+4]["type"] != "other" and tokens[pos+4]["type"] != "eof" and tokens[pos+4]["type"] != "newline":
                            if tokens[pos+4]["type"] == "newline":
                                lineNum += 1
                            tire.code = tire.code.replace("$" + str(index), tokens[pos+4]["value"])
                            pos += 1
                            index += 1
                        tire.run()
                        variables[name] = returnValue
                        tokens[pos + 2]["type"] = returnType
                        pos += 3
                        continue
                    if tokens[pos + 2]["type"] == "keyword" and tokens[pos + 2]["value"] == "Output":
                        variables[tokens[pos + 1]["value"]] = tmp.getTemp()
                        pos += 3
                        continue
                    if "." in tokens[pos + 2]["value"]:
                        variables[tokens[pos]["value"]] = handleDots(tokens, pos, 1)
                        pos += 3
                        continue
                else:
                    if variables[tokens[pos+2]["value"]].isnumeric():
                        try:
                            if tokens[pos+3]["value"] == "+":
                                pass
                            else:
                                variables[tokens[pos]["value"]] = variables[tokens[pos + 2]["value"]]
                                pos += 3
                                continue
                        except:
                            variables[tokens[pos]["value"]] = variables[tokens[pos + 2]["value"]]
                            pos += 3
                            continue
                        sum = handleMath(tokens, pos, 2)
                        if sum != None:
                            tokens[pos + 2]["value"] = sum
                            tokens[pos + 3]["value"] = ""
                            tokens[pos + 4]["value"] = ""
                            tokens[pos + 3]["type"] = "ignore"
                            tokens[pos + 4]["type"] = "ignore"
                        variables[tokens[pos]["value"]] = sum
                        pos += 3
                        continue
                    variables[tokens[pos]["value"]] = variables[tokens[pos + 2]["value"]]
                pos += 3
            elif token["type"] != "ignore" and token["type"] != "eof" and token["type"] != "newline":
                print_error("Error: Unexpected token \"" + token["value"] + "\"")
            else:
                pos += 1
    def run(self):
        tokens = self.tokinize()
        self.parse(tokens)
    def stop(self):
        self.stopExecution = True
        if not self.Importing and not self.inFunction:
            os.remove("temp")