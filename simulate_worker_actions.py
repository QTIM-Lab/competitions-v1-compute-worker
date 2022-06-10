import os, sys, pdb
from subprocess import Popen, call, check_output, CalledProcessError, PIPE
from dotenv import load_dotenv
from zipfile import ZipFile
import shutil
# import patoolib
from unrar import rarfile

import worker as w

load_dotenv()

SERVICE_PRINCIPAL_APPID=os.getenv("AZURE_ACR_TOKEN_NAME")
SERVICE_PRINCIPAL_CLIENT_SECRET=os.getenv("AZURE_ACR_TOKEN_PASS")
REGISTRY=os.getenv("AZURE_CONTAINER_REGISTRY")+".azurecr.io"
# pdb.set_trace()

# def test(task_id, task_args):

docker_image_path = "/tmp/codalab/docker_images_img" # tmp dir I copied some failed images to
docker_image_path = "/tmp/codalab/docker_images"
temp_dir = '/tmp/codalab' # local development; should exist already

# task_args should look like this:
task_args = {'file_name': 'specific_docker_image_archive.zip','user':'1'}
unzip_dir = os.path.join(temp_dir,'tmp_unzip_dir') # real environment
unzip_dir = os.path.join(temp_dir,'tmp_unzip_dir_practice')

# stdout, stderr
stdout_docker_build = """### STDOUT docker image build ###"""
stderr_docker_build = """### STDERR docker image build ###"""

# Look around
os.listdir(temp_dir)
os.listdir(docker_image_path)
os.listdir(unzip_dir)

def login(registry=REGISTRY):
    #logger.info('#### login started ####')
    login_cmd = "docker login {registry} --username {appid} --password {secret}".format(
        appid=SERVICE_PRINCIPAL_APPID, secret=SERVICE_PRINCIPAL_CLIENT_SECRET, registry=registry)
    process = Popen(login_cmd.split(" "), stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print("stdout: " + stdout)
    print("stderr: " + stderr)

def unzip():
    #logger.info('#### unzip ####')
    try:
        # pdb.set_trace()
        shutil.rmtree(unzip_dir)
    except:
        print('creating {} directory'.format(unzip_dir))
        os.mkdir(unzip_dir)
        shutil.copyfile(src=os.path.join(docker_image_path, task_args['file_name']),dst=os.path.join(unzip_dir, task_args['file_name']))
        #logger.info('#### unzip - B ####')
    if task_args['file_name'].find(".rar") != -1:
        rar = rarfile.RarFile(os.path.join(unzip_dir, task_args['file_name']))
        rar.extractall(unzip_dir)
    elif task_args['file_name'].find(".zip") != -1:
        with ZipFile(os.path.join(unzip_dir, task_args['file_name']), 'r') as zipObj:
            zipObj.extractall(path=unzip_dir)


def build(repo,image):
    #logger.info('#### build ####')
    global stdout_docker_build
    global stderr_docker_build
    tag = task_args['file_name'].replace('.zip','').replace('.rar','').replace('\n','').replace(' ','')
    tag = tag if tag[0] != '.' and tag[0] != '-' else tag[1:]
    #logger.info('#### {repo} {image} {tag} ####')
    try:
        os.chdir(unzip_dir)
    except:
        raise Exception('Can\'t get into {}'.format(unzip_dir))
    print('done')
    docker_build_cmd = "docker build -t {}/user_{}:{} .".format(repo,image,tag)
    process = Popen(docker_build_cmd.split(" "), stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    stdout_docker_build += stdout
    stderr_docker_build += stderr
    print("stdout: " + stdout)
    print("stderr: " + stderr)

def push(repo,image):
    #logger.info('#### push ####')
    tag = task_args['file_name'].replace('.zip','').replace('.rar','').replace('\n','').replace(' ','')
    tag = tag if tag[0] != '.' and tag[0] != '-' else tag[1:]
    docker_push_cmd = "docker push {}/user_{}:{}".format(repo,image,tag)
    process = Popen(docker_push_cmd.split(" "), stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print("stdout: " + stdout)
    print("stderr: " + stderr)

def clean_up(repo,image):
    #logger.info('#### clean_up ####')
    # Docker image
    tag = task_args['file_name'].replace('.zip','').replace('.rar','').replace('\n','').replace(' ','')
    tag = tag if tag[0] != '.' and tag[0] != '-' else tag[1:]
    docker_clean_up_cmd = "docker image rm {}/user_{}:{}".format(repo,image,tag)
    process = Popen(docker_clean_up_cmd.split(" "), stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print("stdout: " + stdout)
    print("stderr: " + stderr)
    # Zipfile and extracted directory
    try:
        # pdb.set_trace()
        os.chdir('../') # meant to bring you to path in variable `temp_dir`
        shutil.rmtree(unzip_dir)
        os.remove(os.path.join(docker_image_path, task_args['file_name']))
    except:
        raise Exception( "Can\'t find {} or {}".format( unzip_dir, os.path.join(docker_image_path, task_args['file_name']) ) )

def collect_docker_submission_logs():
    pdb.set_trace()


try:
    login()
    unzip()
    build(REGISTRY,task_args['user'])
    push(REGISTRY,task_args['user'])
    clean_up(REGISTRY,task_args['user'])
    collect_docker_submission_logs()
    # time.sleep(5)
    _send_update(task_id, 'finished', secret=task_args['secret'], extra={
                    'metadata': 'image upload'})
except:
    _send_update(task_id, 'failed', secret=task_args['secret'], extra={
                    'metadata': 'image upload'})


# def do_docker_pull(image_name):
#     print("Running docker pull for image: {}/{}".format(REGISTRY,image_name))
#     try:
#         cmd = ['docker', 'pull', "{}/{}".format(REGISTRY,image_name)]
#         docker_pull = check_output(cmd)
#         print("Docker pull complete for image: {0} with output of {1}".format(image_name, docker_pull))
#     except CalledProcessError as error:
#         print("Docker pull for image: {}/{} returned a non-zero exit code!".format(REGISTRY,image_name))

# do_docker_pull("user_1:docker_submission_v1")

# _send_update - happens from worker
task_id = 324
# {'file_name': 'test_rar.rar', 'message': "image upload job"} # 
task_args = {'file_name': 'midrc_docker_image_inference_pytorch.zip', 'user':'1', 'secret':'secret'}
w._send_update(task_id, 'running', secret=task_args['secret'], extra={'metadata': 'image upload', 'info':'docker somehtihn'})

# docker run
participant_docker_submission_cmd = ['docker', 'run', '--net', 'none', '--shm-size=256m', '--rm', '--name=participant_docker_submission_taskid_368', '--stop-timeout=500', '--security-opt=no-new-privileges', '-v', '/mnt/midrccodalab/input-data/MIDRC/validation_data/:/mnt/in:ro', '-v', '/tmp/codalab/tmpadNhtI/run/input/res:/mnt/out', u'{}/user_1:midrc_docker_image_inference_pytorch'.format(REGISTRY)]
participant_docker_process = Popen(participant_docker_submission_cmd, stdout=PIPE, stderr=PIPE)
participant_docker_process.wait() # This halts other actions till this run is finished.
drun_stdout, drun_stderr = participant_docker_process.communicate()

participant_docker_submission_cmd = ['echo', 'test message']
participant_docker_process = Popen(participant_docker_submission_cmd, stdout=PIPE, stderr=PIPE)
drun_stdout, drun_stderr = participant_docker_process.communicate()
print(drun_stdout)
print(drun_stderr)

os.getcwd()
os.listdir(os.getcwd())
with open('test_output.txt', 'w') as f:
    f.write(drun_stderr)
    f.write(drun_stdout)

with open('test_output.txt', 'r') as f:
    f.readlines()

    
