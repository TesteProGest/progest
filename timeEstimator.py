from github import Github
user = "xanderayes"
senha = "966d3V87."
org = "TesteProGest"
repo = "progest"

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

foi = 0
while(foi==0):
    #issue = input("issue")
    try:
        g=Github(user,senha).get_organization(org).get_repo(repo)#.get_issue(int(issue))
        print("foi")
        foi = 1
    except:
        print("nao")


userSearch = 'xanderayes'
tagSearch = 'Feature'
pointEstimate = 3

times = []
points = []
issueList = g.get_issues()
for issue in issueList:
    if issue.title.find(' - PT') != -1:
        for label in issue.labels:
            if label.name == tagSearch:
                for comment in issue.get_comments():
                    if comment.user.login == userSearch:
                        indice = comment.body.find('Total_time=') 
                        if indice != -1:
                            times.append(comment.body[indice+12:comment.body.index('</title>')])
                            points.append(issue.title[issue.title.index(' - PT')+5:])
totalTime = 0
for t in times:
    t2 = t.split(':',2)
    totalTime=totalTime+3600*int(t2[0])+60*int(t2[1])+int(t2[2])

totalPoints = 0
for p in points:
    totalPoints = totalPoints + int(p)
    
timeEstimate = pointEstimate * totalTime / totalPoints

print(format_time(timeEstimate))


    
