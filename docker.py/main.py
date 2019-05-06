# encoding=utf-8
import sys
import string
import getopt
import pubproxy
import filter

def main(argv):
    deploy_channel = None
    docker_envs = []
    node = None
    container_name = None
    docker_image = None
    volumes = []
    net = 'bridge'  # 默认网络模式
    ports = []
    mode = 'default'  # default or swarm
    compose_file = None
    stack_name = None

    usage = 'Usage: main.py --deploy_channel=DEV \
                --docker_env="ASPNETCORE_ENVIRONMENT=Development" \
                --docker_env="ASPNETCORE_ENDPOINT=192.168.8.11" \
                --node=1 \
                --container_name=cs-trader-grpc-srv \
                --docker_image=cs-trader-grpc-srv:v3.1.8.180717091123 \
                --net=host \
                --v=source:target \
                --port=8585:80'

    try:
        opts, args = getopt.getopt(argv,
                                   'c:n:cn:i:p:e:m:f:v',
                                   ['deploy_channel=', 'channel=', 'docker_env=', 'env=', 'node=', 'container_name=', 'docker_image=', 'image=', 'net=', 'port=', 'mode=', 'file=', 'stack=', 'volume='])
    except getopt.GetoptError as er:
        print(er)
        print(usage)

        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-c', '--deploy_channel', '--channel'):
            deploy_channel = arg
        elif opt in ('-n', '--node'):
            node = arg
        elif opt in ('-cn', '--container_name'):
            container_name = arg
        elif opt in('-i', '--docker_image', '--image'):
            docker_image = arg
        elif opt in('--net'):
            net = arg
        elif opt in('-p', '--port'):
            ports.append(arg)
        elif opt in('-e', '--docker_env', '--env'):
            docker_envs.append(str.strip(arg))
        elif opt in('-m', '--mode'):
            mode = arg
        elif opt in('-f', '--file'):
            compose_file = arg
        elif opt in('--stack'):
            stack_name = arg
        elif opt in('-v', '--volume'):
            volumes.append(str.strip(arg))


    #filter the prod pub list
    if deploy_channel.lower() == 'prod':
        filter.filter(container=container_name, stack_compose=compose_file)

    proxy = pubproxy.PubProxy(
        deploy_channel, node, container_name, docker_image, net, ports, volumes, docker_envs, mode, compose_file, stack_name)

    if(mode == 'swarm'):
        proxy.publish_stack()
    else:
        proxy.publish_container()

if __name__ == '__main__':
    main(sys.argv[1:])
