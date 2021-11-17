import os
import firstuseauthenticator
import shutil
import sys
def fix_dir(spawner):
    username = spawner.user.name
    path = os.path.join('/home', username)
    statement = username +":" + str(100) + " " + path
    s = "chown -R " + statement
    if not os.path.exists(path):
        u = "useradd " + username
        os.system(u)
        os.chdir('/home')
        os.mkdir(username)
        l = "ln -s /opt/notebooks " +path
        os.system(l)
        os.system(s)


c.JupyterHub.authenticator_class = 'firstuseauthenticator.FirstUseAuthenticator'
c.FirstUseAuthenticator.create_users=True

c.JupyterHub.cookie_secret_file = '/root/jupyterhub_cookie_secret'
c.JupyterHub.db_url = '/root/jupyterhub.sqlite'

c.Spawner.pre_spawn_hook = fix_dir

c.JupyterHub.bind_url = 'http://:8000/'

#admins = set(line.strip() for line in open('admins.txt'))
#c.Authenticator.admin_users = set(admins)
c.Authenticator.admin_users = set({'admin'})
