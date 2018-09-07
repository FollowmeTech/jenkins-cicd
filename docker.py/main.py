# encoding=utf-8
import sys
import getopt
import pubproxy
import filter

def main(argv):
    deploy_env = None
    docker_env = []
    node = None
    container_name = None
    docker_image = None
    net = 'host'  # 默认网络模式
    port = None
    mode = 'default'  # default or swarm
    compose_file = None
    stack_name = None

    usage = 'Usage: main.py --deploy_env=dev \
                --docker_env="ASPNETCORE_ENVIRONMENT=Development" \
                --docker_env="ASPNETCORE_ENDPOINT=192.168.8.11" \
                --node=1 \
                --container_name=cs-trader-grpc-srv \
                --docker_image=cs-trader-grpc-srv:v3.1.8.180717091123 \
                --net=host \
                --port=8585:80'

    try:
        opts, args = getopt.getopt(argv,
                                   'e:o:n:c:i:p:m:f:',
                                   ['deploy_env=', 'env=', 'docker_env=', 'node=', 'container_name=', 'docker_image=', 'net=', 'port=', 'mode=', 'file=', 'stack='])
    except getopt.GetoptError as er:
        print(er)
        print(usage)

        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-e", "--deploy_env", "--env"):
            deploy_env = arg
        elif opt in ("-n", "--node"):
            node = arg
        elif opt in ("-c", "--container_name"):
            container_name = arg
        elif opt in("-i", "--docker_image"):
            docker_image = arg
        elif opt in("--net"):
            net = arg
        elif opt in("-p", "--port"):
            port = arg
        elif opt in("-o", "--docker_env"):
            docker_env.append(str.strip(arg))
        elif opt in("-m", "--mode"):
            mode = arg
        elif opt in("-f", "--file"):
            compose_file = arg
        elif opt in("--stack"):
            stack_name = arg

    #filter the prod pub list
    if deploy_env == 'prod':
        filter.filter(container=container_name, stack_compose=compose_file)

    proxy = pubproxy.PubProxy(
        deploy_env, node, container_name, docker_image, net, port, docker_env, mode, compose_file, stack_name)

    if(mode == 'swarm'):
        proxy.publish_stack()
    else:
        proxy.publish_container()

if __name__ == "__main__":
    main(sys.argv[1:])
