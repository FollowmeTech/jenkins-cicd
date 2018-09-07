Portainer发布脚本使用说明:

 `python main.py [param]`

以发布trader服务到beta为例:
```bash
python main.py --deploy_env=beta --docker_env='ASPNETCORE_ENVIRONMENT=Staging' --docker_env='TEST=Hello world' --node=1 --container_name=cs-trader-grpc-srv --docker_image=cs-trader-grpc-srv:v3.1.8.180717091123 --net=host
```

### 参数说明

--deploy_env 部署环境

可选值dev,beta，prod

eg: `python main.py [其他参数..] --deploy_env beta`

---------


--docker_env 自定义docker运行时候指定的环境变量

支持传入多个值

eg: `python main.py [其他参数..] --docker_env="ASPNETCORE_ENVIRONMENT=Development" --docker_env="ASPNETCORE_ENDPOINT=192.168.8.11"`

---------

--node portainer里对应的Endpoint

可选值1,2,3...
eg: `python main.py [其他参数..] --node 1`

---------


--docker_image 要拉取的镜像名称

eg: `python main.py [其他参数..] --docker_image cs-trader-grpc-srv:v3.1.8.180717091123`


-----

--container_name 容器运行时候指定的名称

eg: `python main.py [其他参数..] --container_name cs-trader-grpc-srv`

-------


--net docker网络模式(默认是host)

可选值host/bridge/none/container

eg: `python main.py [其他参数..] --net host`

-----------

--port 端口映射

目前只实现了基本的一种模式即 容器端口:宿主主机

eg: `python main.py [其他参数..] --port=8585:80`

----------