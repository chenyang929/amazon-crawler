# -*- coding: utf-8 -*-
import json
from json.decoder import JSONDecodeError
import time
import traceback
import requests
from requests.exceptions import RequestException
from config import Config

# 私密代理接口
ProxyUrl = 'http://dps.kuaidaili.com/api/getdps/?orderid=921572509617587&num=1000&format=json&sep=1'
GouIp = 'http://dynamic.goubanjia.com/dynamic/get/b94808e4e950d7b06b5370231ae7304d.html'
KDI_IP = 'http://dps.kuaidaili.com/api/getdps/?orderid=941797185104558&num=1000&format=json&sep=1'
jiekou = 'http://47.90.32.89:20000/proxy/goubanjia'


# 接口取代理ip
def get_kdl_ip():
    flag = True
    while flag:
        try:
            res = requests.get(KDI_IP, timeout=10)
            if res.status_code == 200:
                try:
                    proxy_list = list(set(json.loads(res.text)['data']['proxy_list']))
                except TypeError:
                    print('get_proxy_ip failed')
                    time.sleep(2)
                else:
                    flag = False
                    return proxy_list
        except RequestException:
            print('No ProxyIp')
            time.sleep(2)


def get_gou_ip():
    ip_lst = []
    try:
        res = requests.get(GouIp, timeout=10)
        if res.status_code == 200:
            try:
                res.json()['success']
            except JSONDecodeError:
                proxy_list = res.text.strip().split('\n')
                ip_lst.extend(proxy_list)
    except Exception as err:
        print('Gou ProxyIp raise a exc {}'.format(err))
    finally:
        return ip_lst


def get_jiekou():
    ip_lst = []
    try:
        res = requests.get(jiekou, timeout=10)
        if res.status_code == 200:
            ip_lst = json.loads(res.text)
            # try:
            #     res.json()['success']
            # except JSONDecodeError:
            #     proxy_list = res.text.strip().split('\n')
            #     ip_lst.extend(proxy_list)
    except Exception as err:
        print('Gou ProxyIp raise a exc {}'.format(err))
    finally:
        return ip_lst


def update_proxy_ip(que):
    try:
        for n in range(que.qsize()):
            que.get_nowait()
    except:
        pass
    #ip_lst = get_kdl_ip()
    ip_lst = []
    ip_lst.extend(get_jiekou())
    for ip_proxy in ip_lst:
        que.put({'ip': ip_proxy, 'num': Config.FAIL_TIMES})
    print('update proxy ip: {!r}'.format(que.qsize()))


if __name__ == '__main__':
    get_jiekou()
