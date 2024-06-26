# -*- coding: utf-8 -*-
# @Time    : 2021/2/23 06:30
# @Author  : srcrs
# @Email   : srcrs@foxmail.com

import smtplib,traceback,os,requests,urllib,json
from email.mime.text import MIMEText
import smtplib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr,formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import pytools

#返回要推送的通知内容
#对markdown的适配要更好
#增加文件关闭操作
def readFile(filepath):
    content = ''
    with open(filepath, encoding='utf-8') as f:
        for line in f.readlines():
            content += line + '\n\n'
    return content

#返回要推送的通知内容
#对text的适配要更好
#增加文件关闭操作
def readFile_text(filepath):
    content = ''
    with open(filepath, encoding='utf-8') as f:
        for line in f.readlines():
            content += line
    return content

#返回要推送的通知内容
#对html的适配要更好
#增加文件关闭操作
def readFile_html(filepath):
    content = ''
    with open(filepath, "r" , encoding='utf-8') as f:
        for line in f.readlines():
            content += line + '<br>'
    return content

#邮件推送api来自流星云
#备用方案推送api来自BER
def sendEmail(email):
    try:
        #要发送邮件内容
        content = readFile('./log.txt')
        content=content.replace('\n\n','')
        #接收方邮箱
        receivers = email
        #邮件主题
        subject = 'UnicomTask每日报表'
        pytools.jmail('UnicomTask',subject,content)
    except Exception as e:
        print('邮件推送异常，原因为: ' + str(e))
        print(traceback.format_exc())

#邮件推送
def sendMail(email,wo_mail,wo_mail_passwd):
    try:
        #要发送邮件内容
        content = readFile('./log.txt')
        #接收方邮箱
        receivers = email
        #邮件主题
        subject = 'UnicomTask每日报表'

        mailserver='smtp.wo.cn'   #邮件服务器
        port=25                   #端口
        sender=wo_mail            #发件人，用户

        server = smtplib.SMTP(mailserver, port)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(sender, wo_mail_passwd)  # 发件人邮箱账号、邮箱授权码
        msg = MIMEMultipart('mixed')
        msg['From'] = Header(sender)
        msg['To'] = Header(receivers)
        msg['subject'] = Header(subject, 'utf-8')
        body = MIMEText(content, 'plain', 'utf-8')
        msg.attach(body)
        # msg.as_string()中as_string()是将msg(MIMEText或MIMEMultipart对象)变为str。
        errmsg=server.sendmail(sender, receivers, msg.as_string())
        #print(errmsg)
        server.quit()
        print('邮件推送成功')

    except Exception as e:
        print('邮件推送异常，原因为: ' + str(e))
        print(traceback.format_exc())

#钉钉群自定义机器人推送
def sendDing(webhook):
    try:
        #要发送邮件内容
        content = readFile('./log.txt')
        data = {
            'msgtype': 'markdown',
            'markdown': {
                'title': 'UnicomTask每日报表',
                'text': content
            }
        }
        headers = {
            'Content-Type': 'application/json;charset=utf-8'
        }
        res = requests.post(webhook,headers=headers,json=data)
        res.encoding = 'utf-8'
        res = res.json()
        print('dinngTalk push : ' + res['errmsg'])
    except Exception as e:
        print('钉钉机器人推送异常，原因为: ' + str(e))
        print(traceback.format_exc())

#发送Tg通知
def sendTg(tgBot):
    try:
        token = tgBot['tgToken']
        chat_id = tgBot['tgUserId']
        #发送内容
        content = readFile_text('./log.txt')
        data = {
            'UnicomTask每日报表':content
        }
        content = urllib.parse.urlencode(data)
        #TG_BOT的token
        #token = os.environ.get('TG_TOKEN')
        #用户的ID
        #chat_id = os.environ.get('TG_USERID')
        url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={content}'
        session = requests.Session()
        resp = session.post(url)
        print(resp)
    except Exception as e:
        print('Tg通知推送异常，原因为: ' + str(e))
        print(traceback.format_exc())

#发送push+通知
def sendPushplus(token):
    try:
        #发送内容
        data = {
            "token": token,
            "title": "UnicomTask每日报表",
            "content": readFile_html('./log.txt')
        }
        url = 'http://www.pushplus.plus/send'
        headers = {'Content-Type': 'application/json'}
        body = json.dumps(data).encode(encoding='utf-8')
        resp = requests.post(url, data=body, headers=headers)
        print(resp)
    except Exception as e:
        print('push+通知推送异常，原因为: ' + str(e))
        print(traceback.format_exc())
        
#发送serverchan通知
def sendServerChan(SCKEY):
    try:
        #发送内容
        data = {
            "text": "UnicomTask每日报表",
            "desp": readFile_html('./log.txt')
        }
        url = 'https://sc.ftqq.com/'+SCKEY+'.send'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        #body = json.dumps(data).encode(encoding='utf-8')
        body = urllib.parse.urlencode(data).encode(encoding='utf-8')
        resp = requests.post(url, data=body, headers=headers)
        print(resp)
    except Exception as e:
        print('serverchan通知推送异常，原因为: ' + str(e))
        print(traceback.format_exc())

#企业微信通知，普通微信可接收
def sendWechat(wex):
    #获得access_token
    url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
    token_param = '?corpid=' + wex['id'] + '&corpsecret=' + wex['secret']
    token_data = requests.get(url + token_param)
    token_data.encoding = 'utf-8'
    token_data = token_data.json()
    access_token = token_data['access_token']
    #发送内容
    content = readFile_text('./log.txt')
    #创建要发送的消息
    data = {
        "touser": "@all",
        "msgtype": "text",
        "agentid": wex['agentld'],
        "text": {"content": content}
    }
    send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    message = requests.post(send_url,json=data)
    message.encoding = 'utf-8'
    res = message.json()
    print('Wechat send : ' + res['errmsg'])

#发送IFTTT通知
def sendIFTTT(ifttt):
    try:
        content = readFile('./log.txt')
        body = { ifttt['subjectKey']: 'UnicomTask每日报表', ifttt['contentKey']: content }
        url = 'https://maker.ifttt.com/trigger/{event_name}/with/key/{key}'.format(event_name=ifttt['eventName'], key=ifttt['apiKey'])
        response = requests.post(url, json=body)
        print(response)
    except Exception as e:
        print('IFTTT通知推送异常，原因为: ' + str(e))
        print(traceback.format_exc())

#发送Bark通知
def sendBark(Bark):
    #发送内容
    Barkkey = Bark['Barkkey']
    Barksave = Bark['Barksave']
    content = readFile_text('./log.txt')
    data = {
        "title": "UnicomTask每日报表",
        "body": content
    }
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    url = f'https://api.day.app/{Barkkey}/?isArchive={Barksave}'
    session = requests.Session()
    resp = session.post(url, json = data, headers = headers)
    state=json.loads(resp.text)
    print(state)
