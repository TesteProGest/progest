from github import Github
print("*************************************")
print("Welcome to ProJet analytics dashboard")
print("ProJet v0.0.1-alpha0")
print("*************************************")
print("\n")

printEvents = False

totalPoints = 0
totalIssues = 0
## Represents the points per milestones
sprintsPoints = {}
## Represents the points per dev
assigneesPoints = {}
## Represents the points per dev in which milestone
sprintsPointsDevs = {}
## Represents the points per status
statusPoints = {}
## Represents the points per dev in which status
statusPointsDevs = {}

## Represents the number of issues per milestones
sprintsIssues = {}
## Represents the number of issues per status
statusIssues = {}
## Represents the number of issues per dev
assigneesIssues = {}
## Represents the number of issues per dev in which milestone
sprintsIssuesDevs = {}
## Represents the number of issues per dev in which status
statusIssuesDevs = {}


#################################################################           
def issueMapper(i):
    global totalPoints
    global totalIssues
    
    global sprintsPoints
    global assigneesPoints
    global sprintsPointsDevs
    global statusPoints
    global statusPointsDevs
    
    global sprintsIssues
    global assigneesIssues
    global sprintsIssuesDevs
    global statusIssues
    global statusIssuesDevs
    
    MAX_POINTS = 100
    
    ## Get sprint if the issue is milestones
    sprint = i.milestone
    if sprint == None:
        sprint = "Nenhum sprint associado"
    else:
        sprint = sprint.title
    ## Get assignee if the issue is assigned
    developer = i.assignee
    if developer == None:
        developer = "Nenhum colaborador associado"
    else:
        developer = developer.login
    ## Issues under points process rules
    try:
        ## Extract points
        if i.title.rfind("- PT") != -1:
            pt = int(i.title.split(" - PT")[1])
        elif i.title.rfind("- pt") != -1:
            pt = int(i.title.split(" - pt")[1])
        elif i.title.rfind("- Pt") != -1:
            pt = int(i.title.split(" - Pt")[1])
        else:
             print("Issue #" + str(i.number) + " sem estimativa de pontos de esforço:")
        ## Points validation
        if pt > MAX_POINTS:
            print("Issue #" + str(i.number) + " com pontos acima do limite estipulado")       
            print("Estimativa de: " + str(pt))
            pt = MAX_POINTS
            print("Pontuação alterada para: " + str(pt))
        elif pt < 0:
            print("Issue com pontos negativos: " + str(pt))
            pt = pt * int(-1)
            print("Pontuação alterada para: " + str(pt))
        print("Pontos da issue #" + str(i.number) + ", " + str(i.title) + ": " + str(pt))
        totalPoints = totalPoints + pt
        ## Milestone points
        print("Sprint da issue: " + sprint)
        if list(sprintsPoints.keys()).count(sprint) == 1:
            sprintsPoints[sprint] = sprintsPoints[sprint] + pt
        else:
            sprintsPoints[sprint] = pt
        ## Assignees points
        print("Colaborador envolvido na issue: " + developer)
        if list(assigneesPoints.keys()).count(developer) == 1:
            assigneesPoints[developer] = assigneesPoints[developer] + pt
        else:
            assigneesPoints[developer] = pt
        ## Assignees points per sprint
        if list(sprintsPointsDevs.keys()).count(sprint) == 1:
            if list(sprintsPointsDevs[sprint].keys()).count(developer) == 1:
                sprintsPointsDevs[sprint][developer] = sprintsPointsDevs[sprint][developer] + pt
            else:
                sprintsPointsDevs[sprint].update({developer: pt})
        else:
            sprintsPointsDevs[sprint] = {developer: pt}
        ## Status labels points 
        for l in i.get_labels():
            status = l.name
            if status.rfind("-") != -1:
                if list(statusPoints.keys()).count(status) == 1:
                    statusPoints[status] = statusPoints[status] + pt
                else:
                    statusPoints[status] = pt
            ## Assignees points per status
            if list(statusPointsDevs.keys()).count(status) == 1:
                if list(statusPointsDevs[status].keys()).count(developer) == 1:
                    statusPointsDevs[status][developer] = statusPointsDevs[status][developer] + pt
                else:
                    statusPointsDevs[status].update({developer: pt})
            else:
                statusPointsDevs[status] = {developer: pt}
    except:
        print("Problema nos pontos da issue #" + str(i.number) +" "+str(i.title))
        print("!_________________________!_________________________!")

    try:
        ## Total number of issues
        totalIssues = totalIssues + 1
        ## Milestone number of tasks
        if list(sprintsIssues.keys()).count(sprint) == 1:
            sprintsIssues[sprint] = sprintsIssues[sprint] + 1
        else:
            sprintsIssues[sprint] = 1
        ## Assignees number of tasks
        if list(assigneesIssues.keys()).count(developer) == 1:
            assigneesIssues[developer] = assigneesIssues[developer] + 1
        else:
            assigneesIssues[developer] = 1
        ## Assignees number of tasks per sprint
        if list(sprintsIssuesDevs.keys()).count(sprint) == 1:
            if list(sprintsIssuesDevs[sprint].keys()).count(developer) == 1:
                sprintsIssuesDevs[sprint][developer] = sprintsIssuesDevs[sprint][developer] + 1
            else:
                sprintsIssuesDevs[sprint].update({developer: 1})
        else:
            sprintsIssuesDevs[sprint] = {developer: 1}    
        ## Status labels number of tasks
        for l in i.get_labels():
            status = l.name
            print("Labels: " + status)
            ## Status labels
            if status.rfind("-") != -1:
                if list(statusIssues.keys()).count(status) == 1:
                    statusIssues[status] = statusIssues[status] + 1
                else:
                    statusIssues[status] = 1
            ## Assignees number of tasks per status
            if list(statusIssuesDevs.keys()).count(status) == 1:
                if list(statusIssuesDevs[status].keys()).count(developer) == 1:
                    statusIssuesDevs[status][developer] = statusIssuesDevs[status][developer] + 1
                else:
                    statusIssuesDevs[status].update({developer: 1})
            else:
                statusIssuesDevs[status] = {developer: 1}
    except:
        print("Problema com a issue #" + str(i.number) +" "+str(i.title))
        print("!______________!______________!______________!______________!")        
        ## Events track
        print("Aberta em: " + str(i.created_at))
        if printEvents == True:
            for e in i.get_events():
                if e.event == "assigned" or e.event == "unassigned":
                    actor = e.raw_data.get("assigner").get("login")
                else:
                    actor = e.actor.login
                print(str(e.event) + " por " + str(actor) + " em: " + str(e.created_at))
                if e.event == "closed" or e.event == "reopened":
                    print(" Fechada em: " + str(i.closed_at))
                elif e.event == "labeled" or e.event == "unlabeled":
                    if (e.raw_data.get("label").get("name").rfind("-") != -1):
                        if int(e.raw_data.get("label").get("name").split(" - ")[0]) > 0:
                            print(" Deslocado para o estado: " + str(e.raw_data.get("label").get("name").split(" - ")[1]))
                    else:
                        print(" (Des)Associada ao label: " + str(e.raw_data.get("label").get("name")))
                elif e.event == "milestoned" or e.event == "demilestoned":
                    print(" (Des)Associada ao sprint: " + str(e.raw_data.get("milestone").get("title")))
                elif e.event == "assigned" or e.event == "unassigned":
                    print(" (Des)Associado ao colaborador: " + str(e.raw_data.get("assignee").get("login")))
                    print(" Pelo colaborador: " + str(e.raw_data.get("assigner").get("login")))
                elif e.event == "renamed":
                    print(" Nome alterado de: " + str(e.raw_data.get("rename").get("from")))
                    print(" Para: " + str(e.raw_data.get("rename").get("to")))
    
    print("\n")

#################################################################
    
#################################################################
def points():
    try:
        issue = ""
        #issue = input("Issue(opt): ")
        if issue == "":
            ## Lookup for all issues in repo
            lookup = True
            issueCounter = 1
            while lookup == True:
                try:
                    issue = gRepo.get_issue(issueCounter)
                    issueMapper(issue)
                    issueCounter = issueCounter + 1
                except:
                    lookup = False
                
            print("Pontos totais: " + str(totalPoints))
            for sP in sprintsPoints:
                print("Pontos totais do sprint " + str(sP) + ": " + str(sprintsPoints[sP]))
            for aP in assigneesPoints:
                print("Pontos totais do colaborador: " + str(aP) + ": " + str(assigneesPoints[aP]))
            for sDP in sprintsPointsDevs:
                print("Pontos do colaborador no sprint: " + str(sDP) + ": " + str(sprintsPointsDevs[sDP]))
            for stP in statusPoints:
                print("Pontos por status: " + str(stP) + ": " + str(statusPoints[stP]))
            for stPD in statusPointsDevs:
                print("Pontos do colaborador no status: " + str(stPD) + ": " + str(statusPointsDevs[stPD]))
            print("\n")
            
            print("Numero de tarefas totais: " + str(totalIssues))
            for sI in sprintsIssues:
                print("Numero de tarefas totais do sprint " + str(sI) + ": " + str(sprintsIssues[sI]))
            for aI in assigneesIssues:
                print("Numero de tarefas totais do colaborador: " + str(aI) + ": " + str(assigneesIssues[aI]))
            for sID in sprintsIssuesDevs:
                print("Numero de tarefas do colaborador no sprint: " + str(sID) + ": " + str(sprintsIssuesDevs[sID]))
            for stI in statusIssues:
                print("Numero de tarefas por status: " + str(stI) + ": " + str(statusIssues[stI]))
            for stID in statusIssuesDevs:
                print("Numero de tarefas do colaborador no status: " + str(stID) + ": " + str(statusIssuesDevs[stID]))
        else:
            issue = gRepo.get_issue(int(issue))
            issueMapper(issue)
    except:
        print("Issue não existe")
        
#################################################################

#################################################################
def start():
    global gRepo
    global printEvents
    
    i=0
    print("Colaboradores do repositorio:")
    for x in gRepo.get_collaborators():
        print(x.login)
    print("Alocáveis do repositorio:")
    for x in gRepo.get_assignees():
        print(x.login)
    print("\n")
    #print("Print events?")
    #v = input("(y/Y)(opt)?: ")
    #if v == "y" or v == "Y":
    #    printEvents = True
    #else:
    #    printEvents = False
    points()
    print("\n")
#################################################################

#################################################################
## Auth
user = input("user: ")
senha = input("senha: ")

org = "TesteProGest"
repo = "progest"

try:
    login=Github(user,senha).get_user().login
    print("Login autenticado")
    try:
        gOrg=Github(user,senha).get_organization(org)
        gRepo=Github(user,senha).get_organization(org).get_repo(repo)
        print("Existe Repo")
        try:
            print("\n")
            start()
        except:
            print("Ocorreu um erro")
    except:
        print("Nao existe issue")
except:
    print("Login incorreto")

    

