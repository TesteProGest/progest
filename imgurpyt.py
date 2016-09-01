# coding: utf-8
from imgurpython import ImgurClient
from github import Github

def authenticate():

	client_id = '8fbf5c5728003fa'
	client_secret = 'f572e08a3005299aa5260a31c10edc7acb87b216'
	
	#https://api.imgur.com/oauth2/authorize?client_id=8fbf5c5728003fa&response_type=pin

	client = ImgurClient(client_id, client_secret)

	# Authorization flow, pin example (see docs for other auth types)
	#authorization_url = client.get_auth_url('pin')

	#print("Go to the following URL: {0}".format(authorization_url))

	# Read in the pin, handle Python 2 or 3 here.
	#pin = input("Enter pin code: ")

	# ... redirect user to `authorization_url`, obtain pin (or code or token) ...
	#authorization_url = client.get_auth_url('pin')
	#credentials = client.authorize(pin, 'pin')
	#client.set_user_auth(credentials['access_token'], credentials['refresh_token'])
	client.set_user_auth('6f5d0cf446bf216b9617e7a29bf637c212812fcc', '8b4641ffdf4c0cb66984466624f326461cf49600')
	

	#print("Authentication successful! Here are the details:")
	#print("   Access token:  {0}".format(credentials['access_token']))
	#print("   Refresh token: {0}".format(credentials['refresh_token']))

	return client

def testAuth(username, password, org, repo, issue):
    try:
        g=Github(username,password).get_organization(org).get_repo(repo).get_issue(issue)
        return 1
    except:
        return 0
	

if __name__ == "__main__":
	
		username = input("Digite o nome de usuario: ")
		password = input("Digite a senha: ")
		org = input("Digite o nome da organizacao: ")
		projectName = input("Digite o nome do repositorio / projeto: ")
		taskID = input("Digite o ID da tarefa / issue: ")

		while (testAuth(username, password, org, projectName, int(taskID)) == 0):
			print("Erro... tente novamente")
			username = input("Digite o nome de usuario: ")
			password = input("Digite a senha: ")
			org = input("Digite o nome da organizacao: ")
			projectName = input("Digite o nome do repositorio / projeto: ")
			taskID = input("Digite o ID da tarefa / issue: ")
		
	
		client = authenticate()
		#Coloca aqui o endereço da imagem no PC
		image = client.upload_from_path('C:\\Users\\Lucas\\Desktop\\Colunas.jpg', anon=False)
		link_img =  '"' + image['link'] +  '"'
		
		print(link_img)
	
		s=u"""<html>
				<head>
					<title>afe</title>
				</head>
				<body>
					<figure>
						<img src= %s alt="Nao deu" width="400" height="400" />
					</figure>

				</body>
			</html>""" % link_img
		
		print(s)	

		#s = format(image['link'])
		Github(username,password).get_organization(org).get_repo(projectName).get_issue(int(taskID)).create_comment(s)
	


