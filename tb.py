#林 test
from math import sin
from math import cos
import math
import os


VERSION = 1
reserved = ["LET", "PRINT", "INPUT", "IF", "ELSE","GOTO",
            "SLEEP", "END", "LIST", "REM", "READ","STOP",
            "WRITE", "APPEND", "RUN", "CLS", "CLEAR",
            "EXIT", "ABS", "SIN", "COS"]#write read append 讀檔 寫入 加入
            #"LET", "PRINT", "INPUT", "IF", "GOTO","LIST", "REM", "READ", "RUN", "CLS", "CLEAR"
operators = [["==", "!=", ">", "<", ">=", "<="], #第0層
             ["."],
             ["+", "-"],
             ["*", "/", "&", "|", "%","<<", ">>"],
             ["^"]] #已做好的運算符號(可使用) #第4層
             #層數依據 越上面越先讀到
lines = {} #lines存行號
maxLine = 0
linePointer = 0
stopExecution = False
identifiers = {}
printReady = True

def main():
    print(f"Tiny BASIC version {VERSION}\nby Chung-Yuan Huang")
    while True:
            try:
                if printReady:
                    print("OK.")
                nextLine = input() #輸入之內容存進nextLine(下一步要做的指令)
                if len(nextLine) > 0: #如果nextLine裡有東西
                    executeTokens(lex(nextLine)) #()裡面是token(行號)
            except KeyboardInterrupt: #如果執行中按Ctrl+C，要強制停止
                pass
            except SystemExit: #關閉終端機
                print("Bye!")
                break
            except:
                print("Execution halted.")

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def getVarType(token):
    if len(token) > 1:
        if token[-1] == "$":
            return "STRING"
    return "NUM"

def isValidIdentifier(token):
    if len(token) == 0:
        return False
    if len(token) > 1:
        if token[-1] == "$":
            token = token[0:-1]
    if not(token[0].lower() in "abcdefghijklmnopqrstuvwxyz"):#lower() 方法轉換字符串中所有大寫字符為小寫。
        return False
    for c in token[1:]:
        if not(token[0].lower() in "abcdefghijklmnopqrstuvwxyz0123456789"):
            return False
    return True
    
def lex(line):#分類
    # Splitteo la linea en varios tokens
    inString = False
    tokens = []
    currentToken = ""
    line = line + " "
    for c in line:
        if not(inString) and c in " ()\"":
            if len(currentToken) != 0: #如果currentToken裡有東西
                tokens.append([currentToken, "TBD"])#TBD:代定
                currentToken = ""
            if c == '"':
                inString = True
        elif inString and c == '"':
            tokens.append([currentToken, "STRING"]) #將()中的東西新增到tokens的尾巴後
            currentToken = ""
            inString = False
        else:
            currentToken += c #當前行數=當前行數+c
    # Le asigno un tipo a cada token
    for token in tokens:#整行叫tokens
        if token[1] != "TBD":
            continue
        value = token[0]
        if is_number(value):
            token[0] = float(token[0])
            token[1] = "NUM" #Number
        elif value.upper() in reserved:#upper()方法將字符串中的所有小寫字符轉換為大寫字符並返回。
            token[0] = value.upper()
            token[1] = "RESVD" #Reserved word
        elif value.upper() == "THEN": #upper()方法將字符串中的所有小寫字符轉換為大寫字符並返回。
            token[0] = value.upper()
            token[1] = "THEN"
        elif value == "=":
            token[1] = "ASGN"
        elif isValidIdentifier(token[0]):
            token[1] = "ID" #Identifier #全部變數都是ID
        else:
            for i in range(0, len(operators)):
                if token[0] in operators[i]:
                    token[1] = "OP"
    return tokens

def executeTokens(tokens):#執行指令
    global lines, maxLine, stopExecution, linePointer, printReady
    printReady = True
    if tokens[0][1] == "NUM":
        lineNumber = int(tokens.pop(0)[0])
        if len(tokens) != 0:
            lines[lineNumber] = tokens
            if lineNumber > maxLine:#maxLine是現在有寫之指令最大行數
                maxLine = lineNumber
        else:
            lines.pop(lineNumber, None)
        printReady = False
        return
    if tokens[0][1] != "RESVD": #存資料
        print(f"Error: Unknown command {tokens[0][0]}.")
    else:
        command = tokens[0][0] #command 是指令
        if command == "REM": #增加註解
            return
        elif command == "CLS":#清空屏幕
            print("\n"*500)#連續換500行
        elif command == "END":#結束
            stopExecution = True 
        elif command == "EXIT":#關掉終端機
            quit() #離開 內建
        elif command == "CLEAR":#清除前面所寫之指令
            maxLine = 0
            lines = {}
            identifiers = {}
        elif command == "STOP":#暫停
            os.system("pause")
        elif command == "LIST":#列出前面所寫之指令
            i = 0
            while i <= maxLine:
                if i in lines:
                    line = str(i)
                    for token in lines[i]:
                        tokenVal = ""
                        if token[1] == "NUM":
                            tokenVal = getNumberPrintFormat(token[0])
                        elif token[1] == "STRING":
                            tokenVal = f"\"{token[0]}\""
                        else:
                            tokenVal = token[0]
                        line += " " + str(tokenVal)
                    print(line)
                i = i + 1
        elif command == "PRINT":
            if not(printHandler(tokens[1:])): stopExecution = True
        elif command == "ABS":                                        #abs函式
            if not(absHandler(tokens[1:])): stopExecution = True
        elif command == "SIN":                                        #sin函式
            if not(sinHandler(tokens[1:])): stopExecution = True
        elif command == "COS":                                        #cos函式
            if not(cosHandler(tokens[1:])): stopExecution = True


        elif command == "LET":
            if not(letHandler(tokens[1:])): stopExecution = True
        elif command == "INPUT":
            if not(inputHandler(tokens[1:])): stopExecution = True
        elif command == "GOTO":
            if not(gotoHandler(tokens[1:])): stopExecution = True
        elif command == "IF":
            if not(ifHandler(tokens[1:])): stopExecution = True

        elif command == "ELSE":                                     #else
            if not(ifHandler(tokens[1:])): stopExecution = True
        elif command == "RUN":
            linePointer = 0
            while linePointer <= maxLine:
                if linePointer in lines:
                    executeTokens(lines[linePointer])
                    if stopExecution:
                        stopExecution = False
                        return
                linePointer = linePointer + 1

def getNumberPrintFormat(num):#給予整數值
    if int(num) == float(num):
        return int(num)
    return num

def gotoHandler(tokens):#tokens 是行號
    global linePointer #全域變數 行指令(一開始為0)
    if len(tokens) == 0: #返回其長度或個數(length)，當指令長度為0
        print("Error: Expected expression.") #期待的表示式
        return  #沒有寫=false
    newNumber = solveExpression(tokens, 0) #行數層數為0的地方
    if newNumber[1] != "NUM": #如果不是NUM
        print("Error: Line number expected.") #行數預期
    else:
        linePointer = newNumber[0] - 1
    return True

def inputHandler(tokens):#負責處理輸入的行號
    varName = None
    if len(tokens) == 0: #指令長度為0
        print("Error: Expected identifier.") #定義名稱發生衝突
        return
    elif len(tokens) == 1 and tokens[0][1] == "ID": #變數=ID
        varName = tokens[0][0] #x
    else: #solveExpression處理運算式
        varName = solveExpression(tokens, 0)[0] #行數層數為0的地方，陣列0的地方
        if not(isValidIdentifier(varName)):#有定義的字符
            print(f"Error: {varName} is not a valid identifier.") #不是定義符號
            return #沒有寫=false
    while True:
        print("?", end = '')
        varValue = input()
        if getVarType(varName) == "STRING":#判斷字串還是num
            identifiers[varName] = [varValue, "STRING"] #標示為string與其值
            break
        else:#num的情況
            if is_number(varValue): #回傳數值
                identifiers[varName] = [varValue, "NUM"]#標示為num與其值
                break
            else:
                print("Try again.")
    return True

def ifHandler(tokens):
    thenPos = None
    for i in range(0, len(tokens)): #i=0~指令長度
        if tokens[i][1] == "THEN":
            thenPos = i
            break
    if thenPos == None:
        print("Error: Malformed IF statement.")#IF格式錯誤
        return
    exprValue = solveExpression(tokens[0:thenPos], 0) #解碼指令定位且層數=0
    if exprValue == None:
        return
    elif exprValue[0] != 0:
        if len(tokens[i+1:]) == 0: #i+1的指令長度
            print("Error: Malformed IF statement.")#IF格式錯誤
            return      #flase
        executeTokens(tokens[i+1:]) #執行指令
    return True
def elseHandler(tokens):
    thenPos = None
    for i in range(0, len(tokens)): #i=0~指令長度
        if tokens[i][1] == "THEN":
            thenPos = i
            break
        if tokens[i][1] == "ELSE":
            thenPos = i
            break
    if thenPos == None:
        print("Error: Malformed IF statement.")#IF格式錯誤
        return
    exprValue = solveExpression(tokens[0:thenPos], 0) #解碼指令定位且層數=0
    if exprValue == None:
        return
    elif exprValue[0] != 0:
        if len(tokens[i+1:]) == 0: #i+1的指令長度
            print("Error: Malformed IF statement.")#IF格式錯誤
            return      #flase
        executeTokens(tokens[i+1:]) #執行指令
    return True



def letHandler(tokens):#處理程序
    varName = None
    varValue = None
    eqPos = None
    for i in range(0, len(tokens)):#0~指令長度
        if tokens[i][1] == "ASGN":
            eqPos = i #ASGN指令將位置令為i
            break
    if eqPos == None:
        print("Error: Malformed LET statement.")#LET格式錯誤
        return
    if eqPos == 1 and tokens[0][1] == "ID":
        varName = tokens[0][0] #varname設為指令最初位置
    else:
        if len(tokens[0:i]) == 0:
            print("Error: Expected identifier.")#定義名稱發生衝突
            return
        varName = solveExpression(tokens[0:i], 0)
        if varName == None:
            stopExecution = True #end的情況
            return
        varName = varName[0]
        if not(isValidIdentifier(varName)):
            print(f"Error: {varName} is not a valid identifier.")#(變數)定義名稱不符合
            return
    if len(tokens[i+1:]) == 0: #下個指令長度為0
        print("Error: Expected expression.")#定義名稱發生衝突
        return
    varValue = solveExpression(tokens[i+1:], 0)
    if varValue == None:
        return
    if getVarType(varName) != varValue[1]:
        print(f"Error: Variable {varName} type mismatch.") #該變數發生型別不符
        return
    identifiers[varName] = varValue#將值賦予名稱定義
    return True

def printHandler(tokens): #輸出
    if len(tokens) == 0: #長度為0
        print("Error: Expected identifier.")#定義名稱發生衝突
        return
    exprRes = solveExpression(tokens, 0)
    if exprRes == None:
        return
    if exprRes[1] == "NUM":#若其為NUM
        exprRes[0] = getNumberPrintFormat(exprRes[0]) #將exprRes[0]給予整數值
    print(exprRes[0]) #輸出
    
    return True

def absHandler(tokens):                                   #ABS數學
    if len(tokens) == 0:
        print("Error: Expected identifier.")
        return
    exprRes = solveExpression(tokens, 0)
    if exprRes == None:
        return
    if exprRes[1] == "NUM":
        exprRes[0] = getNumberPrintFormat(exprRes[0])
    print(abs(exprRes[0]))
    return True

def sinHandler(tokens):                                   #SIN數學
    if len(tokens) == 0:
        print("Error: Expected identifier.")
        return
    exprRes = solveExpression(tokens, 0)
    if exprRes == None:
        return
    if exprRes[1] == "NUM":
        exprRes[0] = getNumberPrintFormat(exprRes[0])
    print(sin(math.radians(exprRes[0])))
    return True

def cosHandler(tokens):                                   #COS數學
    if len(tokens) == 0:
        print("Error: Expected identifier.")
        return
    exprRes = solveExpression(tokens, 0)
    if exprRes == None:
        return
    if exprRes[1] == "NUM":
        exprRes[0] = getNumberPrintFormat(exprRes[0])
    print(cos(math.radians(exprRes[0])))
    return True



def getIdentifierValue(name):
    return identifiers[name]

def solveExpression(tokens, level): #數學運算的函式
    leftSideValues = []             #運算符號左邊的值
    rightSideValues = []            #運算符號右邊的值
    if level < len(operators):
        for i in range(0, len(tokens)):
            if not(tokens[i][1] in ["OP", "NUM", "STRING", "ID"]):
                print(f"Error: Unknown operand {tokens[i][0]}") #未知運算元
                return None
            elif tokens[i][1] == "OP" and tokens[i][0] in operators[level]:    #如果是數學運算
                exprResL = None     #初始化左運算子變數
                exprResR = None     #初始化右運算子變數
                if len(leftSideValues) != 0:
                    exprResL = solveExpression(leftSideValues, level) #用遞迴的方式做重複運算
                rightSideValues = tokens[i+1:]
                if len(rightSideValues) != 0:
                    exprResR = solveExpression(rightSideValues, level)#用遞迴的方式做重複運算
                if exprResL == None or exprResR == None:
                    return None
                if tokens[i][0] == "+":    #加法運算
                    if exprResL == None or exprResR == None: #沒有值的情況
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [float(exprResL[0]) + float(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "-":    #減法運算
                    if exprResL == None or exprResR == None:    #沒有值的情況
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [float(exprResL[0]) - float(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "/":    #除法運算
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [float(exprResL[0]) / float(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None 
                elif tokens[i][0] == "*":    #乘法運算
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [float(exprResL[0]) * float(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None     
                elif tokens[i][0] == "^":    #次方運算
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [float(exprResL[0]) ** float(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "%":    #餘數運算
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [float(exprResL[0]) % float(exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "==":    #相等運算
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] == exprResR[0], "NUM"]
                elif tokens[i][0] == "!=":    #不等於運算
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] != exprResR[0], "NUM"]
                elif tokens[i][0] == "<=":    #<=運算
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] <= exprResR[0], "NUM"]
                elif tokens[i][0] == "<":    #<運算
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] < exprResR[0], "NUM"]
                elif tokens[i][0] == ">":    #>運算
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] > exprResR[0], "NUM"]
                elif tokens[i][0] == ">=":    #>=運算
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        return [exprResL[0] >= exprResR[0], "NUM"]
                elif tokens[i][0] == "&":    #AND運算
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [(exprResL[0]) and (exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "|":   #OR數字
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [(exprResL[0]) or (exprResR[0]), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == "<<":    #左移運算
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [float(exprResL[0]) * (2 ** (exprResR[0])), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == ">>":    #右移運算
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    elif exprResL[1] == "NUM" and exprResR[1] == "NUM":
                        return [float(exprResL[0]) / float(2 ** (exprResR[0])), "NUM"]
                    else:
                        print("Error: Operand type mismatch.")
                        return None
                elif tokens[i][0] == ".":   #字串相加
                    if exprResL == None or exprResR == None:
                        print("Error: Operator expects value.")
                        return None
                    else:
                        value1 = exprResL[0]
                        if exprResL[1] == "NUM":
                            value1 = str(getNumberPrintFormat(value1))
                        value2 = exprResR[0]
                        if exprResR[1] == "NUM":
                            value2 = str(getNumberPrintFormat(value2))
                        return [value1 + value2, "STRING"] #相加2字串 再將型別轉成STRING
                
            else:
                leftSideValues.append(tokens[i])
        return solveExpression(leftSideValues, level + 1)
    else:
        if len(tokens) > 1: #長度>1
            print("Error: Operator expected.")
            return None
        elif tokens[0][1] == "ID":
            if tokens[0][0] in identifiers:
                return getIdentifierValue(tokens[0][0]) #拿取數值
            else:
                print(f"Error: Variable {tokens[0][0]} not initialized.") #變數尚未初始化
                return None
        return tokens[0]

main()
# Hello
#HI
#123
