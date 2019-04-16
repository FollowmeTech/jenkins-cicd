# encoding=utf-8
import json
import re
import yaml
import os


class ProjFilter:
    def __init__(self):
        filter_file_path=os.path.dirname(__file__) + '/project_filter.json'
        print('using filter.json from '+ filter_file_path)
        with open(filter_file_path, 'r') as f:
            filter_json = f.read()
            filter_dict = json.loads(filter_json)
            self.white_list = filter_dict['white_list']
            self.black_list = filter_dict['black_list']

    def filter_container(self, container):
        '''
        过滤需要发布的container
        只有containername 在white list里的项目才可发布，否则抛出异常
        container： 发布的容器名称
        '''
        for pre_pattern in self.white_list:
            if re.match(pre_pattern, container):
                print('容器{}匹配完成，准许发布到prod'.format(container))
                return
        
        raise Exception('容器/服务(container_name={}) 不在配置的白名单中，此项目不允许发布到prod，请联系CI管理员添加白名单'.format(container))

    def filter_stack_service(self, stack_compose):
        compose_dict = yaml.load(stack_compose)
        for srv in list(compose_dict['services']):
            self.filter_container(srv)

    def filter_container_or_stack(self, container=None, stack_compose=None):
        if(container):
            self.filter_container(container)
        elif(stack_compose):
            self.filter_stack_service(stack_compose)
        else:
            raise Exception('unkown ...pls check the code ..')


f=ProjFilter()
def filter(container=None,stack_compose=None):
    '''
    filter the containername ,or stack compose.
    '''
    f.filter_container_or_stack(container,stack_compose)


###testing..
if __name__ =='__main__':
    filter('cs-social.main-srv',None)    
