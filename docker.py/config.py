#-*-coding:utf-8-*-

import os

portainer_host="__portainer_url__"
portainer_account = "__portainer_account__"
portainer_password = "__portainer__password__"
dockerhub_domain = "__dockerhub__domain__"
dockerhub_group="__group__"
docker_username = "___username___"
docker_password = "__password__"

def getEnvValue(env,key):
    env_key="{0}_{1}".format(env,key)
    print(env_key)
    return os.environ.get(env_key)

def loadconfig(env):
    '''
    load config from system envs
    '''
    if env not in ["dev","beta","prod"]:
        raise Exception("unknow config [{}], only support[dev/beta/prod]".format(env))

    global portainer_host
    portainer_host=getEnvValue(env,"portainer_host")
    
    global portainer_account
    portainer_account=getEnvValue(env,"portainer_account")
    
    global portainer_password
    portainer_password=getEnvValue(env,"portainer_password")
    
    global dockerhub_domain
    dockerhub_domain=getEnvValue(env,"dockerhub_domain")
    
    global dockerhub_group
    dockerhub_group=getEnvValue(env,"dockerhub_group")
    
    global docker_username
    docker_username=getEnvValue(env,"docker_username")

    global docker_password
    docker_password=getEnvValue(env,"docker_password")

if __name__ =="__main__":
    import sys
    loadconfig(sys.argv[1])
    print(locals())