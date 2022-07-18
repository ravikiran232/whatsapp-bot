# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 12:54:13 2022

@author: ravik
"""
from flask import *
import os
import sys
import requests
from pyngrok import ngrok
import json
import sqlite3
import mysql.connector as mysql_conn
import time
import string
import random
#ngrok.kill()
static_dir = str(os.path.abspath(os.path.join(path="")))
#url = ngrok.connect(80,bind_tls=True).public_url
#print(url)
key_id='141630a4daf9ae2a6912f8d696036141'
secret='1b08e97659cb965064b5f59cbd7aeeb839e72f41'
app=Flask(__name__,static_folder=static_dir,
            static_url_path="", template_folder=static_dir)
person={'response':{'object': 'whatsapp_business_account', 'entry': [{'id': '100199116099450', 'changes': [{'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '15550380849', 'phone_number_id': '107230952048191'}, 'contacts': [{'profile': {'name': 'Ravi Kiran'}, 'wa_id': '917032528158'}], 'messages': [{'from': '917032528158', 'id': 'wamid.HBgMOTE3MDMyNTI4MTU4FQIAEhggMDUyOTkyMDM1MTMyQkVDMEQ2ODZCMzI0OTM2OTc4NEUA', 'timestamp': '1657607914', 'text': {'body': 'ok1234'}, 'type': 'text'}]}, 'field': 'messages'}]}]}}

# coonecting to database
def connect_sql():
  mydb=mysql_conn.connect(host='localhost',
                             auth_plugin='mysql_native_password',
                             user='root',
                             password='Sreedhar@123'
                             )
  
  return mydb
# end ---------

def get_random_string(length):
           letters = string.ascii_lowercase
           result_str = ''.join(random.choice(letters) for i in range(length))
           result_str="order_"+result_str
def send_message(body,number):
    url='https://graph.facebook.com/v13.0/107230952048191/messages'
    headers={'Authorization': 'Bearer EAAID3XxMVc4BAKr1tCzj4bi1JmOQ17ga4ZCkveMcF4ErwqpZAcSsxvEhoooWU7NgaD30vGwZCaDLW78z192BdUdz4CaJiRr6dunTnj6EgdRMiQwxNToZA8OJXPblAFA9t3Jy42Catdp9Y0EeEosLFoh0IAtkdwb9e06FMbbAjizutqPZALUY8VTIlYRMnNDDissmvjgtcmgZDZD',
             'Content-Type':'application/json'}
    data={
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": number,
  "type": "text",
  "text": {
    "preview_url": True,
    "body": body
  }
}
    data=json.dumps(data)
    response=requests.post(url=url,data=data,headers=headers)
    return response.json()
def orders(amt,phone):
        DATA={ "order_id":get_random_string(9) ,
  "order_amount": amt+amt*2.5/100,
  "order_currency": "INR",
  "customer_details": {
    "customer_id":phone ,
    "customer_email": 'abcde@gmail.com',
    "customer_phone": '+'+phone},
  "order_meta":{
      "payment_method":"cc"}
  }
        body=json.dumps(DATA)
        headers={'Content-Type': 'application/json','x-api-version': '2022-01-01','x-client-id': key_id,'x-client-secret': secret}
        response=requests.post('https://sandbox.cashfree.com/pg/orders',headers=headers,data=body)
        details1=response.json()
        link_for_payment=details1['payment_link']
        order_id=details1['order_id']
        return [link_for_payment,order_id,details1]
def payment_status(order_id):
    url="https://sandbox.cashfree.com/pg/orders/"+order_id+"/payments"
    headers=headers = {"Accept": "application/json",'x-client-id':key_id,
                       'x-client-secret':secret,'x-api-version':'2022-01-01'}
    response=requests.get(url=url,headers=headers)
    response=response.json()
    return response
@app.route("/home",methods=['POST','GET'])
def results():
        if request.method=='POST':
            print(request.json)
            response=request.json
            upi_id=''
            amount=0
            if str(response)==str(person['response']):
                return 'we recieved the same response'
            if 'statuses' in str(response):
                return 'we have recievied your webhook thank you !'
            if 'statuses' not in str(response) and response['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']!=person['response']['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']:
              person['response']=response
              name=response['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
              number=response['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
              message_body=response['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
              if (message_body).lower()=='hi':
                print(number,'********',name)
                print(send_message(body='hi '+name+'',number=number))
                send_message(body='welcome to c2b',number=number)
                send_message(body='''choose the product to countinue with:
                1.c2b(card to bank)
                2.w2(wallet to bank)
                3.cbill(credit card bill)
                                     
                ***reply the product name''',number=number)
                return 'thank you'
              if message_body=='c2b':
                send_message(body='''enter the upi id to get the amount
                example->upi:12345678@ybl
                                     
                ***please don't give spaces''',number=number)
                return 'thank you'
              if 'upi' in (message_body).lower():
                upi_id=str(message_body[4:])
                mydb=mysql_conn.connect(host='localhost',
                             auth_plugin='mysql_native_password',
                             user='root',
                             password='Sreedhar@123'
                             )
                crsr=mydb.cursor()
                crsr.execute('use whatsapp')
                value=(name,upi_id)
                crsr.execute('''insert into user_memory(name,upi_id) values(%s,%s);''',value)
                mydb.commit()
                send_message(body='''enter the amount to transfer
    example->amount:100
                                     
                ***please don't give spaces''',number=number)
                return 'thank you'
              if 'amount' in (message_body).lower():
                amount=int(message_body[7:])
                mydb=mysql_conn.connect(host='localhost',
                             auth_plugin='mysql_native_password',
                             user='root',
                             password='Sreedhar@123'
                             )
                value=(amount,name)
                crsr=mydb.cursor()
                crsr.execute('use whatsapp;')
                crsr.execute('''update user_memory set amount=%s where name=%s ;''',value)
                mydb.commit()
                value=[(name)]
                crsr.execute('select upi_id,amount from user_memory where name=%s',value)
                result=crsr.fetchall()
                send_message(body='''transferring to : '''+result[0][0]+'''
                amount: '''+str(result[0][1]+(2.5*result[0][1]/100))+'''
                                     
                ***amount is inclusive of 2.5% convinence fee''',number=number)
                send_message('type ok to countinue',number=number)
                return 'thank you'
              if 'ok' in message_body.lower():
                  mydb=mysql_conn.connect(host='localhost',
                             auth_plugin='mysql_native_password',
                             user='root',
                             password='Sreedhar@123'
                             )
                  value=[(amount,name)]
                  crsr=mydb.cursor()
                  crsr.execute('use whatsapp;')
                  value=[(name)]
                  crsr.execute('select amount from user_memory where name=%s;',value)
                  result=crsr.fetchall()
                  oder=orders(amt=result[0][0],phone=number)
                  print(oder)
                  link=oder[0]
                  order_id=oder[1]
                  value=(link,name)
                  crsr.execute('update user_memory set payment_link=%s where name=%s;',value)
                  mydb.commit()
                  value=[(name)]
                  crsr.execute('select payment_link,amount from user_memory where name=%s;',value)
                  result=crsr.fetchall()
                  send_message(''' click the below link and complete the payment of'''+str(result[0][1])+
                                 ''':'''+result[0][0],number=number)
                  send_message('you have only five minutes to complete the payment',number=number)
                  
                  crsr.execute('select upi_id from user_memory;')
                  result_upi=crsr.fetchall()
                  start_time=time.perf_counter()
                  while(True):
                     timer=time.perf_counter()-start_time
                     if 'payment_status' in str(payment_status(order_id=order_id)):
                      
                       if payment_status(order_id=order_id)[0]['payment_status']=='SUCCESS':
                          print(payment_status(order_id=order_id))
                          send_message('payment success your transfer will be initiated shortly',number=number)
                          value=(name,int(number),order_id,result[0][1],result_upi[0][0],'pending to transfer','0000')
                          crsr.execute('''insert into user_transactions(customer_name,mobile_no,order_id,amount,transferring_to,status
                                       ,card_ending) values=(%s,%s,%s,%s,%s,%s,%s);''',value)
                          mydb.commit()
                          value=[(name)]
                          crsr.execute('delete from user_memory where name=%s',value)
                          mydb.commit()
                          break;
                       if payment_status(order_id=order_id)[0]['payment_status']=='FAILED' or int(timer)==300:
                          print(payment_status(order_id=order_id))
                          send_message('payment failed to reattempt the payment send ok',number=number)
                          value=(name,number,order_id,result[0][1],result_upi[0][0],'transaction failed','0000')
                          crsr.execute('''insert into user_transactions(customer_name,mobile_no,order_id,amount,transferring_to,status
                                       ,card_ending) values=(%s,%s,%s,%s,%s,%s,%s);''',value)
                          mydb.commit()
                          value=[(name)]
                          crsr.execute('delete from user_memory where name=%s',value)
                          mydb.commit()
                          send_message('if any amount deducted it will be refunded in 5-7 business days',number=number)
                          break;
                     if int(timer)==120:
                          print(payment_status(order_id=order_id))
                          send_message('you have only 3min to complete payment ',number=number)
                          time.sleep(6)
                     
                     else:
                         print(payment_status(order_id=order_id))
                         time.sleep(6)
                  
                  return 'thank you'
              #if message_body[0]=='4' or message_body[0]=='5' or message_body[0]=='6':
                  #person['card']=message_body[:16]
                  #person['expiry']=message_body[17:22]
                  #person['cvv']=message_body[23:]
                  
        if request.method=='GET':
          if request.args.get('hub.verify_token')=='iitk3951969010613072002':
            return make_response(request.args.get('hub.challenge'))
          else:
            return make_response('sorry auth token cannot be verified')

if __name__== '__main__':
    app.run(port=80)