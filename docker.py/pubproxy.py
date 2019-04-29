# -*- coding:utf-8 -*-
'''
api
'''
import config
import requests
import json
import base64
import hashlib
import yaml
import time
import config

class PubProxy:

    _max_retry = 3

    def __init__(self, deploy_channel, node, container_name, docker_image, net, ports, volumes, docker_envs, mode, compose_file, stack_name):
        '''
        deploy_channel : 部署环境，dev/testing/staging/prod
        node: 表示node在portainer中的index,例如1/2/3/4
        container_name :cs-trader-grpc-srv
        docker_image : cs-trader-grpc-srv:v1.x.x.x
        docker_envs: list of ENV, ['ASPNETCORE_ENVIRONMENT=Staging','OtherThing=things']
        '''
        self.docker_envs = docker_envs
        self.deploy_channel = deploy_channel

        self.config=config
        self.config.loadconfig(deploy_channel)

        self.node = node
        self.container_name = container_name
        self.docker_image = docker_image
        self.token_portainer = None
        self.token_docker = None
        self.prefix_api = '{}/api/endpoints/{}/docker'.format(
            self.config.portainer_host, node)
        self.prefix_api_stack = '{}/api/endpoints/{}/stacks'.format(
            self.config.portainer_host, node)
        self.full_docker_image = '{}/{}/{}'.format(
            self.config.dockerhub_domain, self.config.dockerhub_group, docker_image)
        self.net = net
        self.ports = ports
        self.volumes = volumes
        self.mode = mode
        if compose_file:
            self.compose_file= base64.b64decode(compose_file)
        self.stack_name = stack_name
        print(self.deploy_channel, self.node, self.container_name, self.net)

    def auth_portainer(self):
        apiurl = self.config.portainer_host + '/api/auth'
        payload = json.dumps({'UserName': self.config.portainer_account,
                              'Password': self.config.portainer_password})
        headers = {'cache-control': 'no-cache', }

        response = requests.request(
            'POST', apiurl, data=payload, headers=headers)
        json_data = json.loads(response.text)
        self.token_portainer = json_data['jwt']

    def printJson(self, parsed):
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
        print(json.dumps(parsed, indent=4, sort_keys=False))

    def auth_docker(self):
        login_info = {
            'username': self.config.docker_username,
            'password': self.config.docker_password,
            'serveraddress': self.config.dockerhub_domain
        }
        login_info = json.dumps(login_info)
        token = base64.b64encode(login_info.encode())
        self.token_docker = token
        
    def docker_warmup(self):
        retry = 0
        while retry < 3:
            try:
                url = '{0}/containers/json'.format(self.prefix_api)
                headers = {
                    'authorization': self.token_portainer,
                    'content-type': 'application/json',
                    'cache-control': 'no-cache',
                }
                response = requests.request(
                    'GET', url, headers=headers, timeout=5)
                response.raise_for_status()
                break
            except Exception:
                pass
            retry += 1

    def create_container(self):
        url = '{0}/containers/create'.format(self.prefix_api)
        querystring = {'name': self.container_name}
        portBindings = {}
        exposedPorts = {}
        if len(self.ports):
            for port in self.ports:
                pubPort, internalPort = port.split(':')
                exposedPorts[internalPort + '/tcp'] = {}
                portBindings[internalPort + '/tcp'] = [
                    { 'HostPort': pubPort}
                ]

        binds = []
        if len(self.volumes):
            for volume in self.volumes:
                binds.append(volume)

        payload = {
            'Env': self.docker_envs,
            'Image': self.full_docker_image,
            'ExposedPorts': exposedPorts,
            'HostConfig': {
                'Binds': binds,
                'NetworkMode': self.net,
                'PortBindings': portBindings,
                'RestartPolicy': {
                    'Name': 'always',
                    'MaximumRetryCount': 0
                }
            }
        }

        payload = json.dumps(payload)
        print(payload)
        headers = {
            'authorization': self.token_portainer,
            'content-type': 'application/json',
            'cache-control': 'no-cache',
        }
        response = requests.request(
            'POST', url, data=payload, headers=headers, params=querystring)
        print(response.text)
    
    def update_restart_policy(self):
        url = '{}/containers/{}/update'.format(
            self.prefix_api, self.container_name)
        headers = {
            'authorization': self.token_portainer,
            'cache-control': 'no-cache',
        }
        payload = {
            'RestartPolicy': {
                'MaximumRetryCount': 1,
                'Name': 'on-failure'
            }
        }
        payload = json.dumps(payload)
        response = requests.request('POST', url, headers=headers, params='')
        print('cancel restart=always:' + response.text)

    def stop_container(self):
        url = '{}/containers/{}/stop'.format(self.prefix_api,
                                             self.container_name)
        headers = {
            'authorization': self.token_portainer,
            'cache-control': 'no-cache',
        }
        response = requests.request('POST', url, headers=headers, params='')

    def delete_container(self):
        url = '{}/containers/{}'.format(self.prefix_api, self.container_name)
        print(url)
        querystring = {'force': 'true'}
        headers = {
            'authorization': self.token_portainer,
            'cache-control': 'no-cache',
        }
        try:
            response = requests.request(
                'DELETE', url, headers=headers, params=querystring)
            print(response.text)
        except Exception as ex:
            if response.status_code != 404:
                print('Container not exists')
            else:
                raise ex

    def pull_docker_image(self, image_name=''):
        '''
        pull image from followme docker hub
        image_name: image name , example： cs-trader-grpc-srv:v8.0.0 , if null, it will read from self.docker_image
        '''
        url = '{}/images/create'.format(self.prefix_api)

        if not image_name:  # 兼容传统的发布模式
            image_name = self.docker_image

        if ':' not in image_name:  # 镜像没有打tag
            image_name += ':latest'

        lsimg = image_name.split(':')

        querystring = {'fromImage': '{}/{}/{}'.format(self.config.dockerhub_domain,
                                                      self.config.dockerhub_group,
                                                      lsimg[0]),
                       'tag': lsimg[1]}
        print (querystring)
        headers = {
            'authorization': self.token_portainer,
            'X-Registry-Auth': self.token_docker,
            'cache-control': 'no-cache',
        }

        result = False
        retry = 0
        while retry < 3:
            try:
                response = requests.request(
                    'POST', url, headers=headers, params=querystring, timeout=30 * (1 + retry))
                print(response.text)
                if response.status_code < 300:
                    result = True
                    break
            except Exception:
                pass
            retry += 1
        if result == False:
            raise Exception("Pull image failed")

    def start_container(self):
        url = '{}/containers/{}/start'.format(
            self.prefix_api, self.container_name)
        headers = {
            'authorization': self.token_portainer,
            'cache-control': 'no-cache'
        }
        response = requests.request('POST', url, headers=headers)
        print(response.text)

    def get_swarm_id(self, stack_name=''):
        '''
        根据节点获取swarm唯一id
        '''
        url = self.prefix_api_stack
        headers = {
            'authorization': self.token_portainer
        }
        response = requests.request('GET', url, headers=headers)
        stack_dict = json.loads(response.text)
        swarm_id = None
        if not stack_name:
            stack_name = self.stack_name

        try:
            for stack in stack_dict:
                if(stack['SwarmId'] and stack['Name'] == stack_name):
                    swarm_id = stack['SwarmId']
                    break
        except:
            pass
        return swarm_id

    def remove_stack(self, stack_id):
        '''
        移除一个stack
        '''
        url = self.prefix_api_stack + '/' + stack_id
        headers = {
            'authorization': self.token_portainer
        }
        response = requests.request('DELETE', url, headers=headers)
        print(response.text)

    def create_stack(self, stack_name=None):
        '''
        创建并启动一个stack
        stack_name:swarm服务名称，如果没指定则默认用self.stack_name
        '''
        url = self.prefix_api_stack
        querystring = {'method': 'string'}

        if not stack_name:
            stack_name = self.stack_name

        # 如果当前部署环境没有认为swarm服务，则结果为空，需要自行赋一个id值
        sid = self.get_swarm_id(stack_name)
        if(not sid):
            sid = hashlib.sha224(str(self.deploy_channel).encode()).hexdigest()

        payload = {
            'Name': stack_name,
            'SwarmID': sid,
            # convert to raw string that contains space and '/n '
            'StackFileContent': self.compose_file  # repr(self.compose_file)
        }
        payload = json.dumps(payload)

        headers = {'authorization': self.token_portainer}
        response = requests.request(
            'POST', url, data=payload, headers=headers, params=querystring)
        print(response.text)

    def update_stack(self, stack_id=''):
        '''
        更新一个已经存在的stack
        '''
        url = self.prefix_api_stack + '/' + stack_id
        payload = {
            'StackFileContent': self.compose_file,  # repr(self.compose_file)
            'Env': [], 
            'Prune':False
        }
        payload = json.dumps(payload)
        headers = {'authorization': self.token_portainer}
        response = requests.request(
            'PUT', url, data=payload, headers=headers)
        print(response.text)

    def publish_stack(self):
        '''
        根据stack_compose.yml文件发布swarm服务
        '''
        compose_dict = yaml.load(self.compose_file)
        #print (json.dumps(compose_dict))
        if not compose_dict:
            raise Exception('compose_file error')

        # auth portainer and docker
        self.auth_portainer()
        print ('auth portianer successful')

        self.auth_docker()
        print ('auth docker successful')

        # 解析compose.yml 拉取所有service下的镜像
        for srv in compose_dict['services']:
            full_image = compose_dict['services'][srv]['image']
            if '/' in full_image:
                end_index = full_image.rfind('/')
                # 提取不包含域名的镜像名称 比如 cs-trader-grpc-srv:v8.0.0
                image_name = full_image[end_index + 1:]
            else:
                image_name = full_image
            self.pull_docker_image(image_name)
        print ('pull docker successful')

        # delete stack
        swarm_id = self.get_swarm_id()
        # if swarm exist, try to delete previous stack
        if(swarm_id):
            stack = self.stack_name + '_' + swarm_id
            self.update_stack(stack_id=stack)
            # self.remove_stack(stack_id)
            # ''' TODO
            # with docker stack rm, the network lingers for about 10 seconds before it's finally removed
            # see https://github.com/moby/moby/issues/29293
            # let's wait
            # '''
            # print('sleep for a while because just remove a stack and its network')
            # time.sleep(9)  # in second
        else:
            # create stack
            self.create_stack()

    def publish_container(self):
        '''
        发布普通的容器服务
        '''
        self.auth_portainer()
        print('auth portianer successful')

        self.auth_docker()
        print('auth docker successful')

        self.docker_warmup()
        print('docker warmup successfully')

        self.pull_docker_image()
        print('pull docker successful')

        self.update_restart_policy()

        self.stop_container()
        print('stop previous container successful')

        self.delete_container()
        print('delete container container successful')

        self.create_container()
        self.start_container()
        print('!---->publish over!')

    def print_endpoints(self):
        self.auth_portainer()
        url = '{}/api/endpoints'.format(self.config.portainer_host)
        headers={'authorization': self.token_portainer}
        response=requests.request('GET',url, headers=headers)
        print(response.text)
