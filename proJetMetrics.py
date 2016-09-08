from github import Github
print("*************************************")
print("Welcome to ProJet analytics dashboard")
print("ProJet v0.0.1-alpha0")
print("*************************************")
print("\n")

def points():
    totalPoints = 0
    try:
        totalIssues = 0
        issue = input("Issue(opt): ")
        if issue == "":
            ## Represents the milestones
            sprints = {}
            ## Represents the devs
            assignees = {}
            ## Represents the points per dev in which milstone
            sprintsDevs = {}
            ## Represents the number of issues per dev in which milstone
            sprintsIssuesDevs = {}
            ## Represents the status by a numbered label
            status = {}
            for i in gRepo.get_issues():
                ## Issues under points process rules
                try:
                    ## Sprint
                    if i.title.rfind("- PT") != -1:
                        pt = int(i.title.split(" - PT")[1])
                    if i.title.rfind("- pt") != -1:
                        pt = int(i.title.split(" - pt")[1])
                    print("Pontos da issue " + str(i.number) + ": " + str(pt))
                    sprint = i.milestone.title
                    print("Sprint da issue: " + sprint)
                    if list(sprints.keys()).count(sprint) == 1:
                        sprints[sprint] = sprints[sprint] + pt
                    else:
                        sprints[sprint] = pt
                    totalPoints = totalPoints + pt
                    ## Assignees points
                    developer = i.assignee
                    if developer == None:
                        developer = "Nenhum colaborador associado"
                    else:
                        developer = developer.login
                    print("Colaborador envolvido na issue: " + developer)
                    if list(assignees.keys()).count(developer) == 1:
                        assignees[developer] = assignees[developer] + pt
                    else:
                        assignees[developer] = pt
                    ## Assignees points per sprint
                    if list(sprintsDevs.keys()).count(sprint) == 1:
                        if list(sprintsDevs[sprint].keys()).count(developer) == 1:
                            sprintsDevs[sprint][developer] = sprintsDevs[sprint][developer] + pt
                        else:
                            sprintsDevs[sprint].update({developer: pt})
                    else:
                        sprintsDevs[sprint] = {developer: pt}
                    ## Assignees number os task per sprint
                    if list(sprintsIssuesDevs.keys()).count(sprint) == 1:
                        if list(sprintsIssuesDevs[sprint].keys()).count(developer) == 1:
                            sprintsIssuesDevs[sprint][developer] = sprintsIssuesDevs[sprint][developer] + 1
                        else:
                            sprintsIssuesDevs[sprint].update({developer: 1})
                    else:
                        sprintsIssuesDevs[sprint] = {developer: 1}
                except:
                    print("Issue " + str(i.number) + " sem estimativa de pontos de esforço:")
                    print(i.title)
                    print("!_________________________!_________________________!")
                totalIssues = totalIssues + 1
                print("Aberta em: " + str(i.created_at))
                for l in i.get_labels():
                    print("Labels: " + l.name)
                    ## Status labels
                    if l.name.rfind("-") != -1:
                        if list(status.keys()).count(l.name) == 1:
                            status[l.name] = status[l.name] + 1
                        else:
                            status[l.name] = 1
                print("\n")
            print("Pontos totais no board: " + str(totalPoints))
            print("Numero de tarefas no board: " + str(totalIssues))
            for s in sprints:
                print("Pontos totais do sprint " + str(s) + ": " + str(sprints[s]))
            for a in assignees:
                print("Pontos totais do colaborador: " + str(a) + ": " + str(assignees[a]))
            for sd in sprintsDevs:
                print("Pontos do colaborador por sprint: " + str(sd) + ": " + str(sprintsDevs[sd]))
            for sid in sprintsIssuesDevs:
                print("Numero de tarefas do colaborador: " + str(sid) + ": " + str(sprintsIssuesDevs[sid]))
            for s in status:
                print("Numero de tarefas por status: " + str(s) + ": " + str(status[s]))
            
        else:
            gIssue=gRepo.get_issue(int(issue))
            print("Existe issue: " + gIssue.title)
            title = gIssue.title
            try:
                pt = int(title.split(" - PT")[1])
                print("Pontos da issue " + str(issue) + ": " + str(pt))
            except:
                print("Issue sem estimativa de pontos de esforço")
            print("Aberta em: " + str(gIssue.created_at))
            print("Fechada em: " + str(gIssue.closed_at))
    except:
        print("Issue não existe")

def speed():
    for x in gRepo.get_issues():
        if x.assignee != None:
            print(x.assignee.login)
        print(str(x.milestone))
        print("__________")

def start():
    global gRepo
   
    i=0
    print("Colaboradores do repositorio:")
    for x in gRepo.get_collaborators():
        print(x.login)
    print("Alocáveis do repositorio:")
    for x in gRepo.get_assignees():
        print(x.login)
    print("\n")
    points()
    print("\n")
    #speed()



## Auth
#user = input("user: ")
#senha = input("senha(: ")
user = "ViniciusBVilar"
senha = "asdf1234"
org = "TesteProGest"
repo = "progest"
#org = "indigotech"
#repo = "br-dunnhumby-comprappy-android"
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

    

