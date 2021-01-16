#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# script version: 1.0.1

import requests
import re
import sys
import json
import configparser
# from retrying import retry
from time import sleep


def GetWlanParams():
    msft_url = "http://www.msftconnecttest.com/redirect"
    global header
    header = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
             Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75'
    }
    try:
        msft = requests.get(msft_url, headers=header, allow_redirects=False, timeout=10)
        if msft.headers['location'].find("microsoft") != -1:
            print("Error: 你已经登录了网络\n*程序退出*")
            sys.exit()
        else:
            location = msft.headers['location']
            tmpWlanParams = SplitWlanParams(location)
            wlanParams = {
                'enAdvert': '0',
                'queryACIP': '0',
                'loginMethod': '1',
                'c': 'ACSetting',
                'a': 'Login',
                'protocol': 'http:',
                'iTermType': '1',
                'enAdvert': '0',
                'queryACIP': '0',
                'loginMethod': '1'
            }
            return dict(wlanParams, **tmpWlanParams)

    except Exception:
        print("Error: 从http://www.msftconnecttest.com/redirect中获取信息时出现错误\n*程序终止*")
        sys.exit()


def SplitWlanParams(location):
    dict = {}
    re1 = re.findall(r"([\w.]+)=[\w.]+", location)
    re2 = re.findall(r"[\w.]+=([\w.]+)", location)
    for n in range(len(re1)):
        dict[re1[n]] = re2[n]
    dict['ip'] = dict['wlanuserip']
    return dict


def InputLoginData(configFile):
    if configFile == "":
        userAccount = input("输入登录用户名：")
        userPasswd = input("输入密码：")
    else:
        cf = configparser.ConfigParser()
        cf.read(configFile)
        userAccount = cf.get("login", "user_name")
        userPasswd = cf.get("login", "password")
        print("用户名:", userAccount, "\n密码:", userPasswd)
    return userAccount, userPasswd


def BuildData(userAccount, userPasswd):
    data = {
        'DDDDD': ',0,' + str(userAccount),
        'upass': str(userPasswd),
        'R1': '0',
        'R2': '0',
        'R3': '0',
        'R6': '0',
        'para': '00',
        '0MKKey': ' 123456',
    }
    return data


def LoginPost(configFile):
    post_url = "http://192.168.7.221:801/eportal/"
    wlanParams = GetWlanParams()
    userAccount, userPasswd = InputLoginData(configFile)
    data = BuildData(userAccount, userPasswd)
    respData = requests.post(post_url, headers=header, data=data, params=wlanParams,\
            allow_redirects=False, timeout=10)
    return respData


def GetResult(resultUrl):
    callBack = requests.get(resultUrl, headers=header, timeout=10)
    reStatus = re.findall(r'<title>(.*)</title>', callBack.text)
    if reStatus[0] == "认证成功页":
        print("-->登录成功<--")
    else:
        print("Error: 登录失败，3秒后将自动重试一次")
        sleep(3)


def Login(configFile=""):
    respData = LoginPost(configFile)
    resultUrl = respData.headers['location']
    GetResult(resultUrl)


if __name__ == "__main__":
    Login("config.ini")
    print("*程序退出*")
