import os
import shutil
import sys

#--------------------------------------------------------------------------------
# Fill this variables to get things working
#--------------------------------------------------------------------------------
# Please select at leat one admin, if using firstuse spawner make sure, that you login 
admin_users = set({'admin'})

# If you run the classroom in a subdirectory, i.e. https://jupyterserver.com/classroom1
subdir = ''

# Port the docker container is mapped to (in docker run ... -p HOST:CONATINER) HOST is the one you need to use.
# Use this for reverse-proxying in nginx or other
local_port = '8000'

# Make sure, that you've set the right git url in dockerfile
use_oAuth = False            # Set to True if you want to use oAuth
oAuth_client_ID = ''
oAuth_client_secret = ''
oAuth_callback_url = ''
 
# If using SSL (recommended)
use_SSL = False
path_key = ''       # Path to keyfile ending with .key 
path_pem = ''       # Path to public cert ending with .pem

#--------------------------------------------------------------------------------
# Other config starts here
#--------------------------------------------------------------------------------
def fix_dir(spawner):
    username = spawner.user.name
    path = os.path.join('/home', username)
    statement = username +":" + str(100) + " " + path
    s = "chown -R " + statement
    t = "chmod -R 0700 " + path
    if not os.path.exists(path):
        u = "useradd " + username
        os.system(u)
        os.chdir('/home')
        os.mkdir(username)
        os.system(t)
    os.system(s)

#Setup auth
if not use_oAuth:
    import firstuseauthenticator
    c.JupyterHub.authenticator_class = 'firstuseauthenticator.FirstUseAuthenticator'
    c.FirstUseAuthenticator.create_users=True

c.Authenticator.admin_users = admin_users

if use_SSL:
    c.JupyterHub.ssl_key = path_key
    c.JupyterHub.ssl_cert = path_pem

c.JupyterHub.cookie_secret_file = '/root/jupyterhub_cookie_secret'
c.JupyterHub.db_url = '/root/jupyterhub.sqlite'

c.Spawner.pre_spawn_hook = fix_dir
url=''
if subdir:
    c.JupyterHub.bind_url = 'http://:' +local_port +'/' +subdir
    url='--url=http://127.0.0.1:8081/' +subdir +'/hub/api'
else:
    c.JupyterHub.bind_url = 'http://:' +local_port +'/'
    url='--url=http://127.0.0.1:8081/hub/api'

c.JupyterHub.load_groups = {
    'formgrader': grader_users
}

# GitLab OAuth
if use_oAuth:
    from oauthenticator.gitlab import GitLabOAuthenticator
    c.JupyterHub.authenticator_class = 'oauthenticator.gitlab.LocalGitLabOAuthenticator'
    c.LocalAuthenticator.create_system_users = True
    c.LocalGitLabOAuthenticator.oauth_callback_url = oAuth_callback_url
    c.GitLabOAuthenticator.client_id = oAuth_client_ID
    c.GitLabOAuthenticator.client_secret = oAuth_client_secret

c.JupyterHub.services = [
    {
        'name': 'idle-culler',
        'admin': True,
        'command': [
            sys.executable,
            '-m', 'jupyterhub_idle_culler',
            '--timeout=1800',url
        ],
    }
]
