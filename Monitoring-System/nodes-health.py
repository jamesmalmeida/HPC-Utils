import smtplib
import subprocess
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re

def send_email(body):
    sender = 'heisenberg@ilum.cnpem.br'
    receivers = ['james.almeida@ilum.cnpem.br']

    # Create a MIMEMultipart message
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = ', '.join(receivers)
    msg['Subject'] = "Heisenberg Monitoring System"

    # Add body as MIMEText (HTML)

    init = '''\
        <html>
            <head></head>
            <body>
            <p>'''
    ending = '''</p>
            </body>
        </html>
        '''
    fullbody = init + body + ending 

    part = MIMEText(fullbody, 'html')
    msg.attach(part)

    message = msg.as_string()
    
    try:
        smtpObj = smtplib.SMTP('mail.cnpem.br')
        smtpObj.sendmail(sender, receivers, message)         
        print(datetime.now(), 'Successfully sent email')
    except smtplib.SMTPResponseException as e:
        print(datetime.now(), ': Error sending email:', e.smtp_code)
        print(datetime.now(), ': Error sending email:', e.smtp_error)
        #print('Failed to send email')
        pass

def check_mount_points(node, mount):
    command = "pdsh -w " + str(node) + " 'df -h | grep " + mount + "' | awk '{print $NF}'"
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
    out, err = proc.communicate()
    solved = None
    #print(out, err)
    if str(out) == "b''":
        print(datetime.now(), ': Error in node',node, 'for mount point', mount)
        #Try to restore mount point:
        remount_command = "pdsh -w " + str(node) + " 'mount -a'"
        mount_restore = subprocess.Popen(remount_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mount_out, mount_err = mount_restore.communicate()
        #Testing if the mount worked
        new_proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        newout, newerr = new_proc.communicate()
        if str(newout) == "b''":
            print(datetime.now(), ': Mount error persisted on node', node, 'for mount point', mount)
            solved = 'not solved'
        else:
            print(datetime.now(), ': Mount error solved for node', node, 'on mount point', mount)
            solved = 'solved'
        #Store all errors and outputs
        list_node_error = [node, mount, err, mount_out, mount_err, newout, newerr, solved] 
        #print(list_node_error)
    else:
        print(datetime.now(), ': Node', node, 'has a health mount point', mount)
        list_node_error = list()
    return list_node_error

def gpu_status(node):
    command = "pdsh -w " + str(node) + ''' "nvidia-smi | grep 'Driver Version: 525.60.13'"'''
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    #print(out)
    #print(err)
    return out, err

def slurm_node_status(node):
    command = "sinfo -N | grep " + str(node) + " | awk '{print $1,$NF}'"
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    out = out.decode("utf-8").strip()
    return out, err

#FINDING ALL NODES
command = "scontrol show node | grep 'NodeName' | awk '{print $1}' | cut -d'=' -f2"
proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = proc.communicate()
# Decode bytes to string
out = out.decode('utf-8')
# Splitting the output into lines
nodes = re.split('\n', out)
# Removing empty elements from the list
nodes = [node for node in nodes if node]
#print(nodes) #DEBUG

#GETTING GRES OF EACH NODE
command = "scontrol show node | grep 'Gres' | awk -F '=' '{print $2}'"
proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = proc.communicate()
# Decode bytes to string
out = out.decode('utf-8')
# Splitting the output into lines
gres_nodes = re.split('\n', out)
# Removing empty elements from the list
gres_nodes = [node for node in gres_nodes if node]
#print(gres_nodes) #DEBUG

#CREATING THE GPU NODES LIST
gpu_nodes = list()
for node, gres in zip(nodes, gres_nodes):
    #print(node, gres)
    if gres != '(null)':
        gpu_nodes.append(node)

#print('ALL Nodes:', nodes)
#print('GPU Nodes:', gpu_nodes)

check_mounts = True
if check_mounts == True:
    #nodes=['work1', 'work4', 'work5'] #NOW DETECTING AUTOMATICALLY
    mounts=["172.20.10.15:/home", "172.20.60.33:/opt"]
    
    error_list = list()
    for node in nodes:
        for mount in mounts:
            error_status = check_mount_points(node, mount)
            #print(node, mount, error_status)
            if error_status != []:
                #print('DEBUG: Appending error')
                error_list.append(error_status)
                #print('DEBUG: found error', error_list)
    
    #print(error_list)
    #print(len(error_list))
    
    if len(error_list) != 0:
        body = str()
        for error in error_list:
            print(datetime.now(), ': Node', error[0], 'has a problem in the mount point', error[1])
            print(datetime.now(), ': After remount atempt:', error[3], error[4], error[5], error[6])
            print(datetime.now(), ': Problem solved?', error[7])
            body = body + 'Node ' + str(error[0]) + ' has a problem in the mount point ' + str(error[1]) + '<br>' + 'After remount atempt the error was ' + str(error[7])
        send_email(body)

check_gpu = True
if check_gpu == True:
    #gpu_nodes = ['work1', 'work2'] #NOW DETECTING AUTOMATICALLY
    error_list = list()
    for node in gpu_nodes:
        out, err = gpu_status(node)
        if str(err) != "b''":
            print(datetime.now(), ': Node', node, 'has a problem with the NVIDIA Driver')
            error_list.append([node, out, err])
        else:
            print(datetime.now(), ': Node', node, 'has a healthly GPU')
    if len(error_list) != 0:
        body = str()
        for error in error_list:
            body = body + 'Node' + str(error[0]) + ' has a problem with the NVIDIA Driver, please check it<br>'
        send_email(body)

check_slurm_node_status = True
if check_slurm_node_status == True:
    #nodes=['work0', 'work1', 'work4', 'work5'] #NOW DETECTING AUTOMATICALLY
    error_list = list()
    for node in nodes:
        out, err = slurm_node_status(node)
        nodename, nodestatus = str(out).split(" ")
        print(datetime.now(), ': Node', nodename, 'has the following status', nodestatus)
        if (nodestatus == 'down') or (nodestatus == 'down*'):
            error_list.append([nodename, nodestatus])
    if len(error_list) != 0:
        body = str()
        for error in error_list:
            body = body + 'Node ' + str(error[0]) + ' has the status ' + str(error[1]) + ' please check'
        #print('DEBUG', body, type(body))
        send_email(body)
