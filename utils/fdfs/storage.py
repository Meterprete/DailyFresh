from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client


class FDFSStorage(Storage):
    '''fast dfs的存储类'''

    def _open(self, name, mode='rb'):
        '''打开文件时使用'''
        pass

    def _save(self, name, content):
        '''保存文件时使用'''
        # 创建一个Fast_client对象
        client = Fdfs_client('./utils/fdfs/client.conf')

        # 上传文件到fast dfs系统中
        res = client.upload_by_buffer(content.read())
        if res.get('Status') != 'Upload successed.':
            raise Exception("上传文件到 Fast_DFS 失败！")
        # 返回文件ID
        filename = res.get('Remote file_id')
        return filename

    def exists(self, name):
        '''Django判断文件是否可用'''
        return False

    def url(self, name):
        '''返回访问文件的url'''
        return 'http://39.105.92.190:8888' + name
