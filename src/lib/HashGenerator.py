#!/usr/bin/env python3

import sys
import os
import binascii
import hashlib

from abc import abstractmethod

from BytesReader import BytesSink

class BytesHasher(BytesSink):
    @abstractmethod
    def Reset(self):
        pass

    @abstractmethod
    def GetDigest(self):
        pass

    @abstractmethod
    def GetHexDigest(self):
        pass

class Crc32Hasher(BytesHasher):
    def __init__(self):
        self.Reset()
    
    def __str__(self):
        return f'crc32: {hex(self.crc32)}'
        
    def Reset(self):
        self.crc32 = 0
            
    def Write(self, data):
        self.crc32 = binascii.crc32(data, self.crc32)
            
    def GetDigest(self):
        return self.crc32

    def GetHexDigest(self):
        pass

class HashlibHasher(BytesHasher):
    def __init__(self, name):
        self.name = name
        self.Reset()
    
    def __str__(self):
        return f'{self.name}: {self.hasher.hexdigest()}'  
        
    def Reset(self):
        self.hasher = hashlib.new(self.name)
            
    def Write(self, data):
        self.hasher.update(data)
            
    def GetDigest(self):
        return self.hasher.digest()

    def GetHexDigest(self):
        return self.hasher.hexdigest()

class HashingCollective(BytesSink):
    def __init__(self):
        self.hashers = []
        self.Reset()
    
    def __str__(self):
        s = ''
        for hasher in self.hashers:
            s += f'{hasher}\n'
        
        return s
        
    def Reset(self):
        self.hashers = [
            Crc32Hasher(),
            HashlibHasher('md5'),
            HashlibHasher('sha1'),
            HashlibHasher('sha256')
            ]
            
    def Write(self, data):
        for hasher in self.hashers:
            hasher.Write(data)
