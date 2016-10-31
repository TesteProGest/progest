#Imports necessarios para ter acesso aos eventos do windows, para manipular os aqruivos .csv, para administrar o tempo e ler sinais do sistema.
import sqlite3
import win32con
import datetime
import sys
import ctypes
import ctypes.wintypes
import time
from github import Github
from easygui import *


booleano = False

tempTitle = ""

inicioSessao = datetime.datetime.now()


conn = sqlite3.connect('timegen.db')
try:
    conn.execute('''CREATE TABLE events
           (SESSION INTEGER NOT NULL,
            USERNAME TEXT NOT NULL,
            PROJECT TEXT NOT NULL,
            TASK INTEGER NOT NULL,
            TIMESTAMP INTEGER NOT NULL,
            EVENT_TIME REAL NOT NULL,
            EVENT_TYPE TEXT NOT NULL,
            SHORT_NAME TEXT NOT NULL,
           WINDOW_TITLE TEXT)''')
    print ("Table created successfully");
except:
    pass

cur_session = conn.execute('SELECT DISTINCT MAX(SESSION) FROM events')
try:
    for row in cur_session.fetchall():
        session = row[0] + 1
except:
    session = 0
print(session)
    



#Ctypes é uma biblioteca de funções externas para python. Permite chamar funções em arquivos .dll ou em bibliotecas compartilhadas.
user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32
kernel32 = ctypes.windll.kernel32




#A função WINFUNCTYPE cria definições de funções de callback usando a convenção stdcall
WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.HWND,
    ctypes.wintypes.LONG,
    ctypes.wintypes.LONG,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD
)


#Define os tipos de eventos a serem capturados
eventTypes = {
    win32con.EVENT_SYSTEM_FOREGROUND: "Foreground",
    win32con.EVENT_SYSTEM_CAPTURESTART: "Click"
}


#Retorna informações a respeito da thread e do processo correntes
processFlag = getattr(win32con, 'PROCESS_QUERY_LIMITED_INFORMATION',
                      win32con.PROCESS_QUERY_INFORMATION)

threadFlag = getattr(win32con, 'THREAD_QUERY_LIMITED_INFORMATION',
                     win32con.THREAD_QUERY_INFORMATION)


#Armazena o timestamp do último evento para mostrar o tempo entre eventos
lastTime = 0

 



def format_time(tstamp):
    x = int(tstamp)
    seconds = int(x % 60)
    x = int(x/60)
    minutes = int(x % 60)
    x = int(x/60)
    hours = int(x)

    return '{h}:{m}:{s}'.format(h=hours,m=minutes,s=seconds)


def signal_handle(answer):
    global username
    global taskID
    global projectName
    global org
    global password
    global client
    global session
    print ("terminating")
   
    if (answer != 1):
        g = Github(username,password).get_organization(org).get_repo(projectName).get_issues()
        for x in g:
            if x.title == username:
                issueID = x.number
        
        fimSessao = datetime.datetime.now()
        totalString=''
        header1 = "{"
        header2 = "'session': " + '"{0}", '.format(session) + "'username': "+ '"{0}", '.format(username) + "'repo': "+'"{0}", '.format(projectName)+"'start': "+'"{0}", '.format(inicioSessao)+"'end': " +'"{0}", '.format(fimSessao)+"'tasks': ["
        header = header1 + header2
        cur = conn.execute('select TASK,  SHORT_NAME , sum(EVENT_TIME) from events where SESSION = ? group by 1,2', (session,))
        for row in cur.fetchall():
            totalString = totalString + "{'taskId': " + '"{0}"'.format(str(row[0])) + "', 'tool': " + '"{0}"'.format(row[1]) + "', 'totalTime': " + '"{0}"'.format(format_time(row[2])) + "}, "
        g2 = Github(username,password).get_organization(org).get_repo(projectName).get_issue(int(issueID))

        finalString = header+totalString[:-2]+"]}"
        #finalString.replace("'", '**')
        #finalString.replace('"',"'")
        #finalString.replace('**', '"')
        finalString.replace('\\', '/')
        
        
        g2.create_comment(finalString)
        conn.close()
        print('connection closed')
        sys.exit()
    else:
        taskID = integerbox("Digite o ID da tarefa / issue: ", 'issue')
        while (testAuth(username, password, org, projectName, int(taskID)) == 0):
            msgbox("Erro... issue nao encontrada")
            taskID = integerbox("Digite o ID da tarefa / issue: ", 'issue')
        print("iniciando nova captacao")
        main()


#Salva no arquivo de logs o timestamp do evento, o tempo gasto em cada evento,
#o tipo de evento e o nome de cada janela aberta
def log(tstamp,eventTime,eventType,windowShortName,windowTitle):
    global session
    global booleano
    global username
    global projectName
    global taskName
    global tempTitle
    if windowTitle == "":
        windowTitle = tempTitle
    else:
        tempTitle = windowTitle
    if booleano == True:
        if 'Stack Overflow' in tempTitle:
            windowShortName = 'Stack Overflow'
        if 'Facebook' in tempTitle:
            windowShortName = 'Facebook'
        conn.execute("INSERT INTO events (SESSION, USERNAME, PROJECT, TASK, TIMESTAMP, EVENT_TIME, EVENT_TYPE, SHORT_NAME, WINDOW_TITLE) \
                    VALUES (?,?,?,?,?,?,?,?,?)", [session, username, projectName, taskID, tstamp, eventTime, eventType, windowShortName, tempTitle])
        conn.commit()
    booleano = True    


#Imprime uma mensagem de erro    
def logError(msg):
    sys.stdout.write(msg + '\n')


#Retorna o ID do processo e define as mensagens de erro caso ocorram
def getProcessID(dwEventThread, hwnd):
    
    hThread = kernel32.OpenThread(threadFlag, 0, dwEventThread)

    if hThread:
        try:
            processID = kernel32.GetProcessIdOfThread(hThread)
            if not processID:
                logError("Couldn't get process for thread %s: %s" %
                         (hThread, ctypes.WinError()))
        finally:
            kernel32.CloseHandle(hThread)
    else:
        errors = ["No thread handle for %s: %s" %
                  (dwEventThread, ctypes.WinError(),)]

        if hwnd:
            processID = ctypes.wintypes.DWORD()
            threadID = user32.GetWindowThreadProcessId(
                hwnd, ctypes.byref(processID))
            if threadID != dwEventThread:
                logError("Window thread != event thread? %s != %s" %
                         (threadID, dwEventThread))
            if processID:
                processID = processID.value
            else:
                errors.append(
                    "GetWindowThreadProcessID(%s) didn't work either: %s" % (
                    hwnd, ctypes.WinError()))
                processID = None
        else:
            processID = None

        if not processID:
            for err in errors:
                logError(err)

    return processID


#Retorna o nome do arquivo do processo especificado
def getProcessFilename(processID):
    hProcess = kernel32.OpenProcess(processFlag, 0, processID)
    if not hProcess:
        logError("OpenProcess(%s) failed: %s" % (processID, ctypes.WinError()))
        return None

    try:
        filenameBufferSize = ctypes.wintypes.DWORD(4096)
        filename = ctypes.create_unicode_buffer(filenameBufferSize.value)
        kernel32.QueryFullProcessImageNameW(hProcess, 0, ctypes.byref(filename),
                                            ctypes.byref(filenameBufferSize))

        return filename.value
    finally:
        kernel32.CloseHandle(hProcess)


#Define o que ocorre quando um evento de troca de janela ou clique é capturado
def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread,
             dwmsEventTime):
    global lastTime
    length = user32.GetWindowTextLengthW(hwnd)
    title = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, title, length + 1)

    processID = getProcessID(dwEventThread, hwnd)

    shortName = '?'
    if processID:
        filename = getProcessFilename(processID)
        if filename:
            shortName = '\\'.join(filename.rsplit('\\', 2)[-2:])

    if hwnd:
        hwnd = hex(hwnd)
    elif idObject == win32con.OBJID_CURSOR:
        hwnd = '<Cursor>'

    log(dwmsEventTime, float(dwmsEventTime - lastTime)/1000, eventTypes.get(event, hex(event)),
        shortName, title.value)

    lastTime = dwmsEventTime


#Define os eventos a serem capturados
def setHook(WinEventProc, eventType):
    return user32.SetWinEventHook(
        eventType,
        eventType,
        0,
        WinEventProc,
        0,
        0,
        win32con.WINEVENT_OUTOFCONTEXT
    )

def testAuth(username, password, org, repo, issue):
    try:
        g=Github(username,password).get_organization(org).get_repo(repo).get_issue(issue)
        return 1
    except:
        return 0
    


#Inicia o loop que captura os eventos
def main():
    ole32.CoInitialize(0)

    WinEventProc = WinEventProcType(callback)
    user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE

    hookIDs = [setHook(WinEventProc, et) for et in eventTypes.keys()]
    if not any(hookIDs):
        print ('SetWinEventHook failed')
        sys.exit(1)

    msg = ctypes.wintypes.MSG()
    if ccbox('Clique em "Cancel" para finalizar a execucao da tarefa ou em "Continue" para executar outra tarefa', 'Finalizar captacao'):
        signal_handle(1)
    else:
        signal_handle(2)
    try:
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
                user32.TranslateMessageW(msg)
                user32.DispatchMessageW(msg)
    except:
        pass

    for hookID in hookIDs:
        user32.UnhookWinEvent(hookID)
    ole32.CoUninitialize()






#Chama a função main e escreve os headers do arquivo .csv
if __name__ == '__main__':
    username = enterbox('Digite o nome de usuario: ', 'username')
    password = passwordbox('Digite a senha: ', 'password')
    org = enterbox("Digite o nome da organizacao: ", 'organization')
    projectName = enterbox("Digite o nome do repositorio / projeto: ", 'repository')
    taskID = integerbox("Digite o ID da tarefa / issue: ", 'issue')

    while (testAuth(username, password, org, projectName, int(taskID)) == 0):
        msgbox("Erro... tente novamente")
        username = enterbox('Digite o nome de usuario: ', 'username')
        password = passwordbox('Digite a senha: ', 'password')
        org = enterbox("Digite o nome da organizacao: ", 'organization')
        projectName = enterbox("Digite o nome do repositorio / projeto: ", 'repository')
        taskID = integerbox("Digite o ID da tarefa / issue: ", 'issue')
    print("iniciando captacao")
    main()
