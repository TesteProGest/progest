#Imports necessarios para ter acesso aos eventos do windows, para manipular os aqruivos .csv, para administrar o tempo e ler sinais do sistema.
import sqlite3
import win32con
import sys
import ctypes
import ctypes.wintypes
import numpy as np
import time
import signal
import matplotlib.pyplot as plt
from imgurpython import ImgurClient
from github import Github
from easygui import *

booleano = False

tempTitle = ""

conn = sqlite3.connect('timegen.db')
try:
    conn.execute('''CREATE TABLE events
           (USERNAME TEXT NOT NULL,
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

def authenticate():
    client_id = '8fbf5c5728003fa'
    client_secret = 'f572e08a3005299aa5260a31c10edc7acb87b216'
    client = ImgurClient(client_id, client_secret)
    client.set_user_auth('6f5d0cf446bf216b9617e7a29bf637c212812fcc', '8b4641ffdf4c0cb66984466624f326461cf49600')
    return client

client = authenticate()    

def make_autopct_time(values):
    def my_autopct(pct):
        total = sum(values)
        segtotal = int(round(pct*total/100.0))
        horas = int(segtotal / 3600)
        mins = int((segtotal - horas * 3600) / 60)
        segs = segtotal - 3600 * horas - 60 * mins
        return '{p:.2f}%  ({h:2d}:{m:2d}:{s:2d})'.format(p=pct,h=horas,m=mins,s=segs)
    return my_autopct

def format_time(tstamp):
    x = int(tstamp)
    seconds = int(x % 60)
    x = int(x/60)
    minutes = int(x % 60)
    x = int(x/60)
    hours = int(x)

    #horas = int(tstamp / 3600)
    #mins = int((tstamp - horas * 3600)/60)
    #segs = int(tstamp - horas * 3600 - mins / 60)
    return '{h}:{m}:{s}'.format(h=hours,m=minutes,s=seconds)


#[Temporário] Recebe o sinal de Ctrl + C para parar o programa e salvar o .csv
def signal_handler():
    global username
    global taskID
    global projectName
    global org
    global password
    global client
    totalTime = 0
    totalClicks = 0
    print ("terminating")
    cur = conn.execute('select SHORT_NAME , count(EVENT_TYPE), sum(EVENT_TIME), count(EVENT_TYPE) / sum(EVENT_TIME) from events where USERNAME = ? and TASK = ? and PROJECT = ? group by 1', (username, taskID, projectName))
    #cur = conn.execute('select * from events')
    #res = [dict(username=row[0], projectName=row[1], taskID=row[2], tstamp=row[3], eventTime=row[4], eventType=row[5], windowShortName=row[6], windowTitle=row[7]) for row in cur.fetchall()]
    totalLinhas = 0
    for row in cur.fetchall():
        totalTime = totalTime + row[2]
        totalClicks = totalClicks + row[1]
        totalLinhas += 1
    cur2 = conn.execute('select SHORT_NAME , count(EVENT_TYPE), sum(EVENT_TIME), count(EVENT_TYPE) / sum(EVENT_TIME) from events where USERNAME = ? and TASK = ? and PROJECT = ? group by 1', (username, taskID, projectName))
    res = [[0 for x in range(6)] for y in range(totalLinhas)]
    titles = []
    times = []
    fTimes = []
    clicks = []
    #res[0][0] = "Window Title"
    #res[0][1] = "Click count"
    #res[0][2] = "Total time"
    #res[0][3] = "Clicks per second"
    #res[0][4] = "Clicks by total"
    #res[0][5] = "Time by total"
    
    i = 0
    for row in cur2.fetchall():
        res[i][0] = row[0]
        res[i][1] = row[1]
        res[i][2] = row[2]
        res[i][3] = row[3]
        res[i][4] = row[1] / totalClicks
        res[i][5] = row[2] / totalTime
        titles.append(row[0])
        times.append(row[2])
        fTimes.append(format_time(row[2]))
        clicks.append(row[1])
        i += 1

    #pie = plt.subplot(211)    
    #pie = plt.pie(times,autopct=make_autopct_time(times),shadow=True,startangle=70)
    #plt.axis('equal')
    #plt.legend(pie[0],titles, loc='upper right')

    #pie2 =  plt.subplot(212) #'%.2f'
    #pie2 = plt.pie(clicks,autopct=make_autopct_click(clicks),shadow=True,startangle=70)
    #plt.axis('equal')
    #plt.legend(pie2[0],titles, loc='upper right')
    timesVector = []
    timesVectorF = []
    for x in range(0,9):
        t = (x+1) * (totalTime / 10)
        timesVector.append(t)
        timesVectorF.append(format_time(t))
        
    
    y_pos = np.arange(len(titles))
    plt.barh(y_pos, times, align='center', alpha=0.4)
    plt.yticks(y_pos, titles)
    plt.xticks(timesVector, timesVectorF)
    plt.xlabel('Total time')
    plt.title('Total time per window')
    
    plt.savefig('foo.png', bbox_inches='tight')
    plt.show()
    
    image = client.upload_from_path('foo.png',anon=False)
    print('image uploaded')
    link_img = '"' + image['link'] + '"'
    s=u"""<html>
				<head>
					<title>Total_time= %s</title>
				</head>
				<body>
					<figure>
						<img src= %s alt="graphs" />
					</figure>

				</body>
			</html>""" % (format_time(totalTime), link_img)
    
        
    #s=username + "," + projectName + "," + taskID + "\n"
    #graphX = []
    #graphy = []
    #for x in res:
        #print(x)
        #s +=str(key)
        #s +="\n"
        #graphX.append(key().[0])
        #graphY.append(key[1])
    #Github(username,password).get_organization(org).get_repo(projectName).get_issue(int(taskID)).create_comment(s)
    Github(username,password).get_organization(org).get_repo(projectName).get_issue(int(taskID)).create_comment(s)
    print('image sent')
    conn.close()
    print('connection closed')
    
    #print(graphX)
    #print(graphY)
    sys.exit()


#Salva no arquivo de logs o timestamp do evento, o tempo gasto em cada evento,
#o tipo de evento e o nome de cada janela aberta
def log(tstamp,eventTime,eventType,windowShortName,windowTitle):
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
        conn.execute("INSERT INTO events (USERNAME, PROJECT, TASK, TIMESTAMP, EVENT_TIME, EVENT_TYPE, SHORT_NAME, WINDOW_TITLE) \
                    VALUES (?,?,?,?,?,?,?,?)", [username, projectName, taskID, tstamp, eventTime, eventType, windowShortName, tempTitle])
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
    if ccbox('Clique em "Continue" para finalizar a execucao da tarefa', 'Finalizar captacao'):
        signal_handler()
    try:
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
                user32.TranslateMessageW(msg)
                user32.DispatchMessageW(msg)
    except:
        pass

    for hookID in hookIDs:
        user32.UnhookWinEvent(hookID)
    ole32.CoUninitialize()


#Recebe o sinal de Ctrl + C ao final da execução 
signal.signal(signal.SIGINT, signal_handler)


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
