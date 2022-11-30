import os
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext, filedialog
import docker
import platform
import subprocess
#import netifaces as ni
from hostapdconf.parser import HostapdConf
from numpy import c_


class DockerController:
    def __init__(self):
        self.client = docker.client.from_env()
        self.container_all = []
        self.container_active = []
        
    def get_all(self):
        self.container_all.clear()
        for c in self.client.containers.list(all=True):
            curr = {}
            curr['port'] = ''
            curr['name'] = c.name
            curr['id'] = c.short_id
            curr['image'] = c.image.tags[0]
            curr['status'] = c.status
            if '8000/tcp' in c.attrs['NetworkSettings']['Ports']:
                curr['port'] = c.attrs['NetworkSettings']['Ports']['8000/tcp'][0]['HostPort']
            self.container_all.append(curr)
        return self.container_all
    
    def get_running(self):
        self.container_active.clear()
        for c in self.client.containers.list():
            curr = {}
            curr['name'] = c.name
            curr['id'] = c.short_id
            curr['image'] = c.image.tags[0]
            curr['status'] = c.status
            curr['port'] = c.attrs['NetworkSettings']['Ports']['8000/tcp'][0]['HostPort']
            self.container_active.append(curr)
        return self.container_active

    def toggleContainer(self, id):
        if self.client.containers.get(id).status == "exited":
            self.client.containers.get(id).start()
        else:
            self.client.containers.get(id).stop()
        
    def delContainer(self, id):
        if self.client.containers.get(id).status == "exited":
            self.client.containers.get(id).remove()
        else:
            self.client.containers.get(id).stop()
            self.client.containers.get(id).remove()
    
    def run_cmd(self, name, cmd):
        return self.client.containers.get(name).exec_run(cmd, stream=True)[1]

    def getLog(self, name):
        if name == "Select Item":
            pass
        return self.client.containers.get(name).logs(tail=20).decode("utf-8")
    
    def get_images(self):
        ret = []
        for l in self.client.images.list():
            ret.append(l.tags[0])
        return ret

    def copy_req_file_container(self, container, source, filename):
        cp="docker cp " +source +" "+container +":/tmp"
        run = "pip3 install -r /tmp/" +filename
        os.system(cp)
        return self.run_cmd(container, run)
    
    def copy_notebookfolder_container(self, container, source):
        cp = "docker cp " +source  +" " +container +":/opt/notebooks"
        return os.system(cp) 

    def new_classroom(self, name, image, port, admin, *args):
        os.system('docker run -d --name '+name +' -p ' +str(port) +':8000 ' +image)
        
class WifiController:
    def __init__(self):
        self.hostapd = HostapdConf('/run/media/andy/Data/git/PiHub/piconfig/hostapd.conf')
    def getWifiName(self):
        return self.hostapd['ssid']
    def getWifiPw(self):
        return self.hostapd['wpa_passphrase']
    def setWifiName(self, ssid):
        self.hostapd['ssid'] = ssid
    def setWifiPw(self, pw):
        self.hostapd['wpa_passphrase'] = pw

class View:
    def __init__(self, master, dockercontroller, wificontroller ,gui):
        self.master = master
        self.dockerc = dockercontroller
        self.wific = wificontroller
        self.gui = gui
        self.os = platform.system()
       
        self.tabControl = ttk.Notebook(master) 
        # Tab Start
        self.tab_start = ttk.Frame(self.tabControl)
        self.draw_start_view(self.dockerc, self.wific)
        self.tabControl.add(self.tab_start, text ='Start Classroom') 
        
        # Tab Config Container 
        self.tab_config = ttk.Frame(self.tabControl) 
        self.draw_config(self.dockerc)
        self.tabControl.add(self.tab_config, text ='Config Classroom') 
        
        # Tab New Container
        self.tab_new_class = ttk.Frame(self.tabControl)
        self.draw_new_class(self.dockerc)
        self.tabControl.add(self.tab_new_class, text = 'New Classroom')

        # Tab Advanced
        self.tab_advanced = ttk.Frame(self.tabControl)
        self.draw_advanced(self.dockerc)
        self.tabControl.add(self.tab_advanced, text = 'Advanced')

        # Tab Build Image
        self.tab_image = ttk.Frame(self.tabControl)
        self.draw_build_image(self.tabControl)
        self.tabControl.add(self.tab_image, text="Build Image")


        # Tab Network
        self.tab_network = ttk.Frame(self.tabControl)
        self.draw_network(self.dockerc)
        self.tabControl.add(self.tab_network, text = 'Network')

        #Pack them 
        self.tabControl.pack(expand = 1, fill ="both") 
    
    def popup(self, msg):
        popup = tk.Tk()
        popup.wm_title("Warning")
        label = ttk.Label(popup, text=msg)
        label.pack(side="top", fill="x", pady=10)
        B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
        B1.pack()
        popup.mainloop()

    def draw_start_view(self, dockerc, wific):
        for child in self.tab_start.winfo_children():
            child.destroy()
        self.tab_start.columnconfigure(0, weight=1)
        self.tab_start.columnconfigure(1, weight=1)
        self.tab_start.columnconfigure(2, weight=1)
        self.tab_start.columnconfigure(3, weight=1)
        self.tab_start.columnconfigure(4, weight=1)

        ttk.Label(self.tab_start, text="Classrooms", font='Helvetica 16 bold').grid(column=0, row=0, pady=10, columnspan=5)
        
        ttk.Label(self.tab_start, text='Name').grid(column=0, row=1, sticky='w')
        ttk.Label(self.tab_start, text='Port').grid(column=1, row=1, sticky='w')
        ttk.Label(self.tab_start, text='Image').grid(column=2, row=1, sticky='w')
        ttk.Label(self.tab_start, text='Status').grid(column=3, row=1, sticky='w')
        ttk.Label(self.tab_start, text='Start/Stop').grid(column=4, row=1, padx=5, sticky='e')
        lc=0
        container_all = dockerc.get_all()
        for c,e in enumerate(container_all,start=2):
            ttk.Label(self.tab_start, text=e['name']).grid(column=0, row=c, pady=5, sticky="w")
            ttk.Label(self.tab_start, text=e['port']).grid(column=1, row=c, padx=5, sticky='w')    
            ttk.Label(self.tab_start, text=e['image']).grid(column=2, row=c, pady=5, sticky='w')
            ttk.Label(self.tab_start, text=e['status']).grid(column=3, row=c, pady=5, sticky='w')
            ttk.Button(self.tab_start, text="Start/Stop", command=lambda e=e: self.gui.toggleContainer(e['id'])).grid(column=4, row=c, pady=5, padx=5, sticky='e')
            lc=c

        ttk.Label(self.tab_start, text="Access Point Settings", font='Helvetica 16 bold').grid(column=0, row=lc+2, pady=10, columnspan=5)
        
        ttk.Label(self.tab_start, text="WiFi Name").grid(column=0, row=lc+3, pady=5, sticky='w')
        self.wifi_ssid = tk.StringVar(value=wific.getWifiName())
        ttk.Label(self.tab_start, textvariable=self.wifi_ssid).grid(column=3, row=lc+3, pady=5, padx=5, sticky='w', columnspan=2)

        ttk.Label(self.tab_start, text="WiFi Password").grid(column=0, row=lc+4, pady=5, sticky='w')
        self.wifi_pw = tk.StringVar(value=self.wific.getWifiPw())
        ttk.Label(self.tab_start, textvariable=self.wifi_pw).grid(column=3, row=lc+4, pady=5, padx=5, sticky='w', columnspan=2)

        ttk.Label(self.tab_start, text="Classroom URL").grid(column=0, row=lc+5, pady=5, sticky='w')
        self.pi_adrr = tk.StringVar(value="http://pi.lan")
        ttk.Label(self.tab_start, textvariable=self.pi_adrr).grid(column=3, row=lc+5, pady=5, padx=5, sticky='w', columnspan=2)

    def draw_config(self, dockerc):
        for child in self.tab_config.winfo_children():
            child.destroy()
        self.tab_config.columnconfigure(0, weight=100)
        self.tab_config.columnconfigure(1, weight=1)
        self.tab_config.columnconfigure(2, weight=1)

        running = []
        running.clear()
        for e in dockerc.get_running():
            running.append(e['name'])

        # Select container on which commands are executed
        ttk.Label(self.tab_config, text="Select Classroom").grid(column=0, row=0, pady=5, sticky='w')
        self.active = tk.StringVar(self.tab_config)
        self.d_active = ttk.OptionMenu(self.tab_config, self.active, "Select Item" ,*running).grid(column=1,pady=5, row=0, sticky='e', columnspan=2)
   
        # Send commands to container
        ttk.Label(self.tab_config, text="Send command to Classroom").grid(column=0, row=1, pady=5, sticky='w')
        self.user_input = tk.StringVar(self.tab_config)
        self.command = ttk.Entry(self.tab_config, textvariable=self.user_input, width=60).grid(column=0, row=3, pady=5, sticky='w')
        self.btn_send_cmd = ttk.Button(self.tab_config, text="Send", command=lambda: self.run_cmd(self.active.get(), self.user_input.get())).grid(column=1, row=3, pady=5, sticky='e', columnspan=2)

        # Send Requirements to container
        
        self.label_package_file = tk.StringVar()
        ttk.Label(self.tab_config, text="Install Packages from file: ").grid(column=0, row=4, pady=5, sticky='w')
        self.label_filename = ttk.Label(self.tab_config, textvariable=self.label_package_file).grid(column=0, row=4, pady=5)
        ttk.Button(self.tab_config, text="Open", command=lambda: self.file_dialog("requirements")).grid(column=1, row=4, pady=5, sticky='e')
        ttk.Button(self.tab_config, text="Install", command=lambda: self.install_requirements(self.active.get(), self.filepath, self.filename)).grid(column=2, row=4, pady=5, sticky='e')
    
        # Get logs from selected container
        ttk.Label(self.tab_config, text="Get Logs").grid(column=0, row=5, pady=5, sticky='w')
       
        self.logbox = scrolledtext.ScrolledText(self.tab_config, height=13, width=110)
        self.logbox.grid(column=0, row=6, pady=5, sticky='w', columnspan=3)
        self.logbox['font'] = ('consolas', '9')
        
        self.btn_get_log = ttk.Button(self.tab_config, text="Get now", command=lambda: self.insert_logbox(self.logbox, dockerc.getLog(self.active.get()))).grid(column=2, row=5, pady=5, sticky='e')
        self.btn_clear = ttk.Button(self.tab_config, text='Clear', command = lambda: self.logbox.delete(1.0, tk.END)).grid(column=1, row=5, pady=5, sticky='e')
        
        # Copy Notebooks to classroom directory
        self.var_notebook_folder = tk.StringVar()
        self.label_notebook_folder = ttk.Label(self.tab_config, textvariable=self.var_notebook_folder).grid(column=0,row=7, pady=5, padx=5, sticky='e')
        ttk.Label(self.tab_config, text='Copy Notebook Folder to classroom').grid(column=0, row=7, pady=5, sticky='w')
        ttk.Button(self.tab_config, text="Open", command = lambda: self.file_dialog("notebooks")).grid(column=1, row=7, pady=5, sticky='e')
        ttk.Button(self.tab_config, text="Copy", command = lambda: self.copy_notebookfolder_container(self.active.get(), self.folder)).grid(column=2, row=7, pady=5, sticky='e')

        # Open shell inside Conatainer
        ttk.Label(self.tab_config, text="Open bash inside Classroom").grid(column=0, row=8, pady=5, sticky='w')
        ttk.Button(self.tab_config, text="Open", command = lambda: self.open_terminal(self.active.get())).grid(column=2, row=8, pady=5, sticky='e')



    def draw_new_class(self, dockerc):
        for child in self.tab_new_class.winfo_children():
            child.destroy()
        self.tab_new_class.columnconfigure(0, weight=3)
        self.tab_new_class.columnconfigure(1, weight=1)
        # Select image
        ttk.Label(self.tab_new_class, text="Select Image").grid(column=0, row=0, pady=5, sticky='w')
        images = self.dockerc.get_images()
        self.activeImage = tk.StringVar(self.tab_new_class)
        ttk.OptionMenu(self.tab_new_class, self.activeImage, "Select Image", *images).grid(column=1, row=0, pady=5, sticky='e')
    
        # Choose name
        ttk.Label(self.tab_new_class, text="Classroom Name").grid(column=0, row=1, pady=5, sticky='w')
        self.c_name = tk.StringVar(self.tab_new_class)
        ttk.Entry(self.tab_new_class, textvariable=self.c_name, width=20).grid(column=1, row=1, pady=5, sticky='e')

        # Choose Port
        ttk.Label(self.tab_new_class, text="Select Port").grid(column=0, row=2, pady=5, sticky='w')
        self.port = tk.IntVar()
        ttk.Entry(self.tab_new_class, textvariable=self.port, width=6).grid(column=1, row=2, pady=5, sticky='e')

        # Custom config file
        ttk.Label(self.tab_new_class, text="Custom config file").grid(column=0, row=3, pady=5, sticky='w')
        ttk.Button(self.tab_new_class, text="Select File", command=lambda: self.file_dialog("config_file")).grid(column=1, row=3, pady=5, sticky='e')

        #Admin Name
        ttk.Label(self.tab_new_class, text="Admin Username").grid(column=0, row=4, pady=5, sticky='w')
        self.admin_name = tk.StringVar(self.tab_new_class)
        ttk.Entry(self.tab_new_class, textvariable=self.admin_name, width=20).grid(column=1, row=4, pady=5, sticky='e')

        # Start
        ttk.Button(self.tab_new_class, text="Start", command=lambda: self.gui.new_classroom(self.c_name.get(), self.activeImage.get(), self.port.get(), self.admin_name.get() )).grid(column=1, row=8, pady=5, sticky='e')

    def draw_advanced(self, dockerc):
        for child in self.tab_advanced.winfo_children():
            child.destroy()
        self.tab_advanced.columnconfigure(0, weight=100)
        self.tab_advanced.columnconfigure(1, weight=1)
        self.tab_advanced.columnconfigure(2, weight=1)

        running = []
        running.clear()
        for e in dockerc.get_all():
            running.append(e['name'])

        ttk.Label(self.tab_advanced, text="Select Classroom").grid(column=0, row=0, pady=5, sticky='w')
        self.activeADV = tk.StringVar(self.tab_advanced)
        self.d_active = ttk.OptionMenu(self.tab_advanced, self.activeADV, "Select Item" ,*running).grid(column=1,pady=5, row=0, sticky='e', columnspan=2)

        # Remove selected Container
        ttk.Label(self.tab_advanced, text="Delete selected Classroom").grid(column=0, row=1, pady=5, sticky='w')
        ttk.Button(self.tab_advanced, text="Delete", command = lambda: self.gui.rmClassroom(self.activeADV.get())).grid(column=2, row=1, pady=5, sticky='e')

        # TODO Make Snapshot of running container

    def draw_network(self, dockerc):
        for child in self.tab_network.winfo_children():
            child.destroy()
        self.tab_network.columnconfigure(0, weight=100)
        self.tab_network.columnconfigure(1, weight=1)
        self.tab_network.columnconfigure(2, weight=1)

        # Set Wifi Name
        ttk.Label(self.tab_network, text="Wifi Name").grid(column=0, row=0, pady=5, sticky='w')
        self.wifi_name = tk.StringVar()
        ttk.Entry(self.tab_network, textvariable=self.wifi_name, width=20).grid(column=2, row=0, pady=5, sticky='e')
    
        # Set encryption 
        ttk.Label(self.tab_network, text="Password").grid(column=0, row=1, pady=5, sticky='w')
        self.wifi_password = tk.StringVar(self.tab_network)
        ttk.Entry(self.tab_network, textvariable=self.wifi_password, width=20).grid(column=2, row=1, pady=5, sticky='e')

        # Status
        ttk.Label(self.tab_network, text="Status").grid(column=0, row=2, pady=5, sticky='w')
        self.wifi_status= tk.StringVar()
        ttk.Label(self.tab_network, textvariable=self.wifi_status).grid(column=1, row=2, pady=5, sticky='e')

        # Start Stop Access Point
        ttk.Label(self.tab_network, text="Start / Stop Access Point").grid(column=0, row=3, pady=5, sticky='w')
        ttk.Button(self.tab_network, text="Start", command="").grid(column=1, row=3, pady=5, sticky='e')
        ttk.Button(self.tab_network, text="Stop", command="").grid(column=2, row=3, pady=5, sticky='e')

    def draw_build_image(self, dockerc):
        for child in self.tab_image.winfo_children():
            child.destroy()
        self.tab_image.columnconfigure(0, weight=100)
        self.tab_image.columnconfigure(1, weight=1)
        self.tab_image.columnconfigure(2, weight=1)

        ttk.Label(self.tab_image, text="Select dockerfile").grid(column=0, row=0, pady=5, sticky='w')
        ttk.Button(self.tab_image, text="Open", command="").grid(column=1, row=0, pady=5, sticky='e')

    def file_dialog(self, action):
        if self.os == 'Windows':
            c = chr(92) # is char \
            home = ''
        else: 
            c = chr(47) # is char /
            home = chr(126) # is char ~
        if action == "requirements":
            self.filepath = filedialog.askopenfilename(initialdir =  home, title = "Select A File", filetypes=[("Textfile", ".txt")])
            self.filename = self.filepath[self.filepath.rfind(c)+1:]
            self.label_package_file.set(self.filename)

        if action == "config_file":
            file = filedialog.askopenfilename(initialdir =  home, title = "Select A File", filetypes=[("Python files", ".py")])
            print(file)

        if action == "notebooks":
            self.folder = filedialog.askdirectory(initialdir =  home, title = "Select A Folder")
            self.var_notebook_folder.set(self.folder)
   
    def insert_logbox(self, logbox, text):
        logbox.insert(tk.END, text)
        logbox.see(tk.END)
    
    def run_cmd(self, container, command):
        if container == "Select Item":
            self.popup("No Classroom selected")
            pass
        response = self.dockerc.run_cmd(container, command)
        for l in response:
            self.logbox.insert(tk.END, l.decode("utf-8"))
        self.logbox.see(tk.END)

    def install_requirements(self, container, filepath, filename):
        if container == "Select Item":
            self.popup("No Classroom selected")
            pass
        response = self.dockerc.copy_req_file_container(container, filepath, filename)
        for l in response:
            self.logbox.insert(tk.END, l.decode("utf-8"))
        self.logbox.see(tk.END)    

    def copy_notebookfolder_container(self, container, folder):
        if container == "Select Item":
            self.popup("No Classroom selected")
            pass
        response = self.dockerc.copy_notebookfolder_container(container, folder)
        if response == 0:
            m = "Sucessful copy folder " + folder +" to " + container +" \n"
            self.logbox.insert(tk.END,  m)
        else:
            self.logbox.insert(tk.END, "Error")
    
    # Working in Arch TODO: Rpi i.e. Raspbian implementation
    def open_terminal(self, container):
        if container == "Select Item":
            self.popup("No Classroom selected")
            pass
        c = "konsole -e \"docker exec -ti " +container +" /bin/bash\" &"
        os.system(c)

class JupyterGui:
    def __init__(self, master):
        self.master = master
        master.title("JupyterHub in Raspberry Pi")
        self.dockercontroller = DockerController()
        self.wificontroller = WifiController()
        self.view = View(self.master, self.dockercontroller, self.wificontroller, self)
    
    def redraw(self):
        self.view.draw_start_view(self.dockercontroller, self.wificontroller)
        self.view.draw_config(self.dockercontroller)
        self.view.draw_advanced(self.dockercontroller)

    def toggleContainer(self,arg):
        self.dockercontroller.toggleContainer(arg)
        self.redraw()

    def new_classroom(self, name, image, port, admin, *args):
        self.dockercontroller.new_classroom(name, image, port, admin)
        self.redraw()
    
    def rmClassroom(self, id):
        self.dockercontroller.delContainer(id)
        self.redraw()   

def main():
    root = tk.Tk()
    root.geometry('800x480')
    root.option_add('*Font', '25')
    JupyterGui(root)
   
    root.mainloop()
    
if __name__ == "__main__":
    main()

