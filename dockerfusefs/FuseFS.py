import os
import sys
import errno
from collections import Counter,defaultdict
from fuse import FUSE, FuseOSError, Operations
import configFile as c
from google.cloud import storage
import json
from threading import Thread, Lock
import time

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = c.CREDENTIALS
client = storage.Client()
bucket = client.bucket(c.BUCKET_NAME)

class FuseFS(Operations):
    def __init__(self,root,mount,foreground=True,nothreads=False,nonempty=True, default_permissions=True):
        self.root = root
        self.mount = mount
        self.FuseLock = Lock()
        super().__init__()
        
    def create(self,path,mode,fi = None):
        try:
            with self.FuseLock:
                localPath = os.path.join(self.root, path[1:]) if path.startswith("/") else os.path.join(self.root, path)
                print(f'Create Local Path : {path}')
                print(f'Create Call Invoked at : {localPath}')
                
                dict = defaultdict(list)
                currentBlob = bucket.blob(path)
                if not currentBlob.exists():
                    currentBlob.upload_from_string(json.dumps(dict),content_type='application/json')
                
                return os.open(localPath, os.O_WRONLY | os.O_CREAT, mode)
        except OSError as e:
            raise FuseOSError(e.errno)

    def open(self,path,flags):
        try:
            with self.FuseLock:
                localPath = os.path.join(self.root, path[1:]) if path.startswith("/") else os.path.join(self.root, path)
                print(f'Open Local Path : {path}')
                print(f'Open Call Invoked at : {localPath}')        
                return os.open(localPath, flags)
        except OSError as e:
            raise FuseOSError(e.errno)
        
    def read(self, path, size, offset, fh):
        try:
            with self.FuseLock:            
                localPath = os.path.join(self.root, path[1:]) if path.startswith("/") else os.path.join(self.root, path)
                print(f'Read Local Path : {path}')
                print(f'Read Call Invoked at: {localPath}')
                os.lseek(fh, offset, os.SEEK_SET)

                currentBlob = bucket.blob(path)
                if currentBlob.exists():
                    gcsdata = currentBlob.download_as_string()
                else:
                    print("Blob Not Found\n")
                return os.read(fh, size)
        except OSError as e:
            raise FuseOSError(e.errno)
    
    def write(self, path, data, offset, fh):
        try:
            with self.FuseLock:            
                localPath = os.path.join(self.root, path[1:]) if path.startswith("/") else os.path.join(self.root, path)
                print(f'Write Local Path : {path}')
                print(f'Write Call Invoked at : {localPath}') 
                 
                print(f'Local Data : {data}')
                print(f'FH Data : {fh}')
                      
                with open(localPath, 'rb+') as file:
                    file.seek(offset)
                    file.write(data)
                    file.flush()
                os.lseek(fh, offset, os.SEEK_SET)
                
                
                currentBlob = bucket.blob(path)
                dict = defaultdict(list)
                if currentBlob.exists():
                    time.sleep(0.5)
                    currentBlob.upload_from_filename(localPath)
                return os.write(fh, data)
        except UnicodeDecodeError as ue:
            print(f'Unicode Exception : {ue}')
            return os.write(fh, data)
        except OSError as e:
            raise FuseOSError(e.errno)
    
    def release(self,path,fh):
        try:
            with self.FuseLock:            
                localPath = os.path.join(self.root, path[1:]) if path.startswith("/") else os.path.join(self.root, path)
                print(f'Release Local Path : {path}')
                print(f'Release Call Invoked at : {localPath}')
                return os.close(fh)
        except OSError as e:
            raise FuseOSError(e.errno)
            
    def getattr(self, path, fh=None):
        try:
            with self.FuseLock:    
                localPath = os.path.join(self.root, path[1:]) if path.startswith("/") else os.path.join(self.root, path)
                print(f'Get Attr Local Path : {path}')
                st = os.lstat(localPath)
                statDict = ('st_ctime', 'st_nlink', 'st_mtime','st_atime', 'st_size', 'st_uid','st_gid','st_dev','st_ino', 'st_mode')
                res = {}
                for key in statDict:
                    res[key] = getattr(st, key)
                return res
        except OSError as e:
            raise FuseOSError(e.errno)
    
    def mkdir(self,path,mode):
        try:
            with self.FuseLock:            
                localPath = os.path.join(self.root, path[1:]) if path.startswith("/") else os.path.join(self.root, path)
                print(f'mkdir Local Path : {path}')
                print(f'Make Directory Call Invoked at : {localPath}')
                
                dict = defaultdict(list)
                currentBlob = bucket.blob(path + '/')
                if not currentBlob.exists():
                    currentBlob.upload_from_string(json.dumps(dict),content_type='application/json')
                    
                return os.mkdir(localPath,mode)
        except OSError as e:
            raise FuseOSError(e.errno)
            
    def readdir(self, path, fh):
        try:  
            localPath = os.path.join(self.root, path[1:]) if path.startswith("/") else os.path.join(self.root, path)
            print(f'readdir Local Path : {path}')
            print(f'Read Directory Call Invoked at : {localPath}')
            directory = ['.', '..']
            if os.path.isdir(localPath):
                directory.extend(os.listdir(localPath))
            yield from directory
        except OSError as e:
            raise FuseOSError(e.errno)        

    def rmdir(self,path):
        try:
            with self.FuseLock:            
                localPath = os.path.join(self.root, path[1:]) if path.startswith("/") else os.path.join(self.root, path)
                print(f'rmdir Local Path : {path}')
                print(f'Remove Directory Call Invoked at : {localPath}')
                
                currentBlob = bucket.blob(path + '/')
                if currentBlob.exists():
                    currentBlob.delete()
                    
                return os.rmdir(localPath)
        except OSError as e:
            raise FuseOSError(e.errno)  
    
    
    def truncate(self, path, length, fh=None):
        try:
            with self.FuseLock:            
                localPath = os.path.join(self.root, path[1:]) if path.startswith("/") else os.path.join(self.root, path)
                
                print(f'Truncate Local Path : {path}')
                print(f'Truncate Call Invoked at : {localPath}')
                
                with open(localPath, 'r+') as file:
                    file.truncate(length)
        except OSError as e:
            raise FuseOSError(e.errno)  
            
    def flush(self, path, fh):
        try:
            with self.FuseLock:            
                return os.fsync(fh)
        except OSError as e:
            raise FuseOSError(e.errno)  
    
    def fsync(self, path, data, fh):
        try:
            with self.FuseLock:            
                return self.flush(path, fh)
        except OSError as e:
            raise FuseOSError(e.errno)  
    
    def unlink(self, path):
        try:
            with self.FuseLock:            
                localPath = os.path.join(self.root, path[1:]) if path.startswith("/") else os.path.join(self.root, path)
                print(f'Unlink Invoked for Local Path : {path}')        
                currentBlob = bucket.blob(path)
                if currentBlob.exists():
                    currentBlob.delete()
                    
                return os.unlink(localPath)
        except OSError as e:
            raise FuseOSError(e.errno)  
        
    def opendir(self, path):
        try:
            with self.FuseLock:
                print(f'Open Dir Local Path : {path}')         
                return 0
        except OSError as e:
            raise FuseOSError(e.errno)
    def rename(self,old, new):
        try:
            with self.FuseLock:
                localPathFrom = os.path.join(self.root, old[1:]) if old.startswith("/") else os.path.join(self.root, old)
                localPathTo = os.path.join(self.root, new[1:]) if new.startswith("/") else os.path.join(self.root, new)
                print(f'Rename file Local Path : {localPathFrom}') 
                print(f'Rename file Local Path : {localPathFrom[len(self.root):]}') 
                currentBlob = bucket.blob(localPathFrom[len(self.root):])
                if currentBlob.exists():
                    bucket.rename_blob(currentBlob,localPathTo)
                
                return os.rename(localPathFrom,localPathTo) 
        except OSError as e:
            raise FuseOSError(e.errno)
    
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'usage: {sys.argv[0]} <root> <mountpoint>')
        sys.exit(1)

    rootPath = sys.argv[1]
    mountPoint = sys.argv[2]
    print("FUSE File System Mounted")
    fuseFS = FuseFS(rootPath,mountPoint)
    FUSE(fuseFS,mountPoint,foreground=True,nothreads=False,nonempty=True,default_permissions=True)
