import os, sys, pdb
from subprocess import Popen, call, check_output, CalledProcessError, PIPE
from dotenv import load_dotenv

load_dotenv()

SERVICE_PRINCIPAL_APPID=os.getenv("AZURE_ACR_TOKEN_NAME")
SERVICE_PRINCIPAL_CLIENT_SECRET=os.getenv("AZURE_ACR_TOKEN_PASS")
REGISTRY=os.getenv("AZURE_CONTAINER_REGISTRY")+".azurecr.io"
# pdb.set_trace()


# task_args should look like this:
# task_args = {'file_name': 'mednist_docker_image.zip','user':'24'}
# temp_dir = '/tmp/codalab'
# unzip_dir = os.path.join(temp_dir,'tmp_unzip_dir')

def login(registry=REGISTRY):
    login_cmd = "docker login {registry} --username {appid} --password {secret}".format(
        appid=SERVICE_PRINCIPAL_APPID, 
        secret=SERVICE_PRINCIPAL_CLIENT_SECRET, 
        registry=registry)
    process = Popen(login_cmd.split(" "), stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print("stdout: " + stdout)
    print("stderr: " + stderr)


login()


def do_docker_pull(image_name):
    print("Running docker pull for image: {}/{}".format(REGISTRY,image_name))
    try:
        cmd = ['docker', 'pull', "{}/{}".format(REGISTRY,image_name)]
        docker_pull = check_output(cmd)
        print("Docker pull complete for image: {0} with output of {1}".format(image_name, docker_pull))
    except CalledProcessError as error:
        print("Docker pull for image: {}/{} returned a non-zero exit code!".format(REGISTRY,image_name))

do_docker_pull("user_1:docker_submission_v1")

