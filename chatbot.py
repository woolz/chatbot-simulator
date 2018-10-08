#!flask/bin/python
# -*- encoding: utf-8 -*-
__author__ = 'woolz'
__git__ = 'https://github.com/woolz/chatbot-simulator'

import sys, os
import re
import urllib
import json
import time
from itertools import chain
from datetime import timedelta
import requests
import json
import unicodedata
import datetime
import base64
import binascii
import random


class ChatbotSimulator:

    def get_bot_rules(self):
        with open('app/default.json') as json_file:  
            return json.load(json_file) 

    def obtain_record(self, name):
        try:
            sep_record = self.record.split('|||')
            for f in range (0, len(sep_record)):
                if not (sep_record[f] == ""):
                    sep_namevalue = sep_record[f].split(':::')
                    if (sep_namevalue[0] == name):
                        return sep_namevalue[1]
            return False
        except:
            return False

    def remove_record(self, name):
        try:
            sep_record = self.record.split('|||')
            for f in range (0, len(sep_record)):
                if not (sep_record[f] == ""):
                    sep_namevalue = sep_record[f].split(':::')
                    if (sep_namevalue[0] == name):
                        self.record = self.record.replace(''+sep_namevalue[0]+':::'+sep_namevalue[1]+'|||', '')
                        return True
            return False
        except:
            return False

    def normalize(self, string):
        return unicodedata.normalize('NFKD', string).encode('ascii','xmlcharrefreplace')#encode('ascii', 'ignore')

    def append_record(self, name, value):
        value = value.replace('+', ' ')
        value = value.replace(':::', '').replace('|||', '')
        try:
            sep_record = self.record.split('|||')
            for f in range (0, len(sep_record)):
                if not (sep_record[f] == ""):
                    sep_namevalue = sep_record[f].split(':::')
                    if (sep_namevalue[0] == name):
                        if (is_number(value) == True):
                            return self.record.replace(''+sep_namevalue[0]+':::'+sep_namevalue[1]+'|||', ''+sep_namevalue[0]+':::'+str(value)+'|||')
                        else:
                            return self.record.replace(''+sep_namevalue[0]+':::'+sep_namevalue[1]+'|||', ''+sep_namevalue[0]+':::'+value+'|||')
            if (self.is_number(value) == True):
                self.record += ""+name+":::"+str(value)+"|||"
            else:
                self.record += ""+name+":::"+value+"|||"
        except:
            if (self.is_number(value) == True):
                self.record += ""+name+":::"+str(value)+"|||"
            else:
                self.record += ""+name+":::"+value+"|||"
        return True


    def convert_option(self, number):
        if len(str(number)) == 1:
            return str(number) + '\u20e3'.decode('unicode-escape')
        else:
            numbers = ""
            number_str = str(number)
            for x in range (0, len(str(number))):
                 numbers += number_str[x] + '\u20e3'.decode('unicode-escape')
            return numbers


    def convert_to_money(self, value):
        return '{:,.2f}'.format(value)#.replace(',', '#').replace('.', ',').replace('#','.')

    def is_number(self, s):
        try: 
            int(s)
            return True
        except ValueError:
            return False  


    def is_date(self, date_text):
        try:
            datetime.datetime.strptime(date_text, "%d-%m-%Y")
            return True
        except:
            return False
        

    def get_weekday(self, date):
        days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dayNumber=date.weekday()
        return days[dayNumber]


    def rest_information(self, url):
        response = urllib.urlopen(url)
        data = response.read().decode("utf-8")
        json_data = json.loads(data)
        return json_data

    def post_rest_information(self, url, values):
        response = requests.post(url, json=values)
        data = response.read().decode("utf-8")
        json_data = json.loads(data)
        return json_data

    def __init__(self, user_section, user_sentence, input_value, retry, record):
    
        self.bot_rules = self.get_bot_rules()
        self.user_section = user_section
        self.user_sentence = user_sentence
        self.input_value = input_value
        self.retry = retry
        self.record = record.decode('base64').decode('utf8')


    def chatbot_response(self):
        calc_values = False
        calc_distance = False
        wait_input = False
        error_callback = False
        api_integration = False
        api_information = False
        mark_consultation = False
        
        x = self.user_section
        messages = ""
        funcs = ""
        get_number_rule = self.bot_rules[x]['id']

        if  self.bot_rules[x].get('message'):
            get_message = self.bot_rules[x]['message']
            if (self.input_value == 0):
                messages += get_message
                
        if self.bot_rules[x].get('functions'):
            if self.bot_rules[x]['functions'].get('calc_values_by_virgule'):
                if self.bot_rules[x]['functions']['calc_values_by_virgule'] == True:
                    calc_values = True
                    cost_total = 0
                    pedidos = ""
            elif self.bot_rules[x]['functions'].get('calc_distance'):
                if self.bot_rules[x]['functions']['calc_distance'] == True:
                    calc_distance = True
                    
            elif self.bot_rules[x]['functions'].get('api_integration'):
                if self.bot_rules[x]['functions']['api_integration'] == True:
                    api_integration = True
                    
            elif self.bot_rules[x]['functions'].get('api_information'):
                if self.bot_rules[x]['functions']['api_information'] == True:
                    api_information = True
                    
            elif self.bot_rules[x]['functions'].get('mark_consultation'):
                if self.bot_rules[x]['functions']['mark_consultation'] == True:
                    mark_consultation = True
                    
            elif self.bot_rules[x]['functions'].get('wait_input'):
                wait_input = True
                    
            elif self.bot_rules[x]['functions'].get('goto'):
                self.user_section = int(self.bot_rules[x]['functions']['goto'])
                return {"message": messages, "section": self.user_section, "input": 0, "retry": 1, "record": self.record.encode('utf-8').encode('base64')}
            elif self.bot_rules[x]['functions'].get('close'):
                if self.bot_rules[x]['functions']['close'] == True:
                    self.user_section = 0
                    self.record = "|||"
                    return {"message": messages, "section": self.user_section, "input": 0, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}

                    
        if not self.input_value == 1 or self.input_value == 2 or self.input_value == 3:
            if self.bot_rules[x].get('options'):
                options_rule = len(self.bot_rules[x]['options']) 
                for f in range (0, options_rule):
                    choise_n = self.bot_rules[x]['options'][f]['id'] + 1
                    if self.bot_rules[x]['options'][f].get('price'):
                        messages += "\n" + self.bot_rules[x]['style_choice'].replace('{number}', self.convert_option(choise_n)).replace('{option}', self.bot_rules[x]['options'][f]['name']).replace('{price}', self.convert_to_money(self.bot_rules[x]['options'][f]['price']))
                    else:
                        messages += "\n" + self.bot_rules[x]['style_choice'].replace('{number}', self.convert_option(choise_n)).replace('{option}', self.bot_rules[x]['options'][f]['name']) 
        if (calc_values == True):
            if not self.input_value == 0:
                if (self.input_value == 1):
                    prev_sec = self.user_section
                    self.user_section = self.user_sentence
                elif (self.input_value == 2):
                    continue_or_return = self.user_sentence
            else:
                messages += "\n" + self.bot_rules[x]['example_message']
                return {"message": messages, "section": self.user_section, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
            if not self.input_value == 2:
                ret = 0
                while True:
                    self.user_section = self.user_section.replace(" ", "")
                    options_split = self.user_section.split(',')
                    try:
                        if self.user_section.count(',') > 0:
                            for b in range(0, len(options_split)):
                               n_object = int(options_split[b]) - 1
                               cost_total += self.bot_rules[x]['options'][n_object]['price']
                               pedidos += self.bot_rules[x]['options'][n_object]['name'] + " ($: " + self.convert_to_money(self.bot_rules[x]['options'][n_object]['price']) + "), "
                               
                        else:
                            value = int(self.user_section) - 1
                            cost_total = self.bot_rules[x]['options'][value]['price']
                            pedidos = self.bot_rules[x]['options'][value]['name']
                            ret = 1
                        break
                    except:
                        messages += self.bot_rules[x]['error_message']
                        if (self.bot_rules[x]['error_callback'] == True):
                            return {"message": messages, "section": prev_sec, "input": 0, "retry": 1, "record": self.record.encode('utf-8').encode('base64')}
                        else:
                            return {"message": messages, "section": prev_sec, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}

            if (self.input_value == 1):
                if not (ret == 1):
                    pedidos = pedidos[:-2]
                confirmation_message = self.bot_rules[x]['confirmation_message'].replace("{%price%}", self.convert_to_money(cost_total)).replace('{%products%}', pedidos)
                confirmation_message = confirmation_message.encode('utf-8')

                if self.bot_rules[x].get('save_has'):
                    price = self.convert_to_money(cost_total)
                    saved_v = '[' + pedidos + '] [All: $: ' + price + '] '
                    self.append_record(self.bot_rules[x]['save_has'], saved_v)
                    
                messages += confirmation_message
                messages += "\n" + self.convert_option(1).encode('utf-8') + " - Confirm choice\n" + self.convert_option(2).encode('utf-8') + " - Return to Selection\n" + self.convert_option(3).encode('utf-8') + " - Return to Home"
                return {"message": messages, "section": prev_sec, "input": 2, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}

            elif (self.input_value == 2):
                messages = ""
                if (continue_or_return == "1"):
                    self.user_section = self.bot_rules[x]['functions']['goto']
                    return {"message": messages, "section": self.user_section, "input": 0, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                elif (continue_or_return == "2"):
                    self.user_section = self.bot_rules[x]['id']
                    self.remove_record(self.bot_rules[x]['save_has'])
                    return {"message": messages, "section": self.user_section, "input": 0, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                elif (continue_or_return == "3"):
                    self.user_section = self.bot_rules[x]['id']
                    self.record = '|||'
                    return {"message": messages, "section": 0, "input": 0, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                else:
                    messages += self.bot_rules[x]['error_message']
                    self.user_section = 0
                    if (self.bot_rules[x]['error_callback'] == True):
                        return {"message": messages, "section": self.user_section, "input": 0, "retry": 1, "record": self.record.encode('utf-8').encode('base64')}
                    else:
                        return {"message": messages, "section": self.user_section, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
        elif (calc_distance == True):
            if not self.input_value == 0:
                if (self.input_value == 1):
                    prev_sec = self.user_section
                    self.user_section = self.user_sentence
                elif (self.input_value == 2):
                    continue_or_return = self.user_sentence
            else:
                messages += self.bot_rules[x]['example_message'] 
                return {"message": messages, "section": self.user_section, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
            if not self.input_value == 2:
                try:
                    method = self.bot_rules[x]['config']['method']
                    if (method == "money_per_km"):
                        price_distance = distance_price(self.user_sentence, self.bot_rules[x]['config']['origin_address'], self.bot_rules[x]['config']['cost'])
                    elif (method == "fixed"):
                        price_distance = self.bot_rules[x]['config']['cost']
                    else:
                        price_distance = 0
                    
                except:
                    messages += self.bot_rules[x]['error_message']
                    if (self.bot_rules[x]['error_callback'] == True):
                        return {"message": messages, "section": prev_sec, "input": 0, "retry": 1, "record": self.record.encode('utf-8').encode('base64')}
                    else:
                        return {"message": messages, "section": prev_sec, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                

            if (self.input_value == 1):
                confirmation_message = self.bot_rules[x]['confirmation_message'].replace("{%price%}", '{:,.2f}'.format(price_distance).replace(',', '#').replace('.', ',').replace('#','.'))
                confirmation_message = confirmation_message.encode('utf-8')
                messages += confirmation_message
                messages += "\n" + self.convert_option(1).encode('utf-8') + " - Continue\n" + self.convert_option(2).encode('utf-8') + " - Set address again\n" + self.convert_option(3).encode('utf-8') + " - Return to Home"

                if self.bot_rules[x].get('save_has'):
                    saved_v = '[Send from:' + self.user_sentence + '] [Cost: $: ' + self.convert_to_money(price_distance) + '] '
                    self.append_record(self.bot_rules[x]['save_has'], saved_v)
                    
                return {"message": messages, "section": prev_sec, "input": 2, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}

            elif (self.input_value == 2):
                messages = ""
                if (continue_or_return == "1"):
                    self.user_section = self.bot_rules[x]['functions']['goto']
                    return {"message": messages, "section": self.user_section, "input": 0, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                elif (continue_or_return == "2"):
                    self.user_section = self.bot_rules[x]['id']
                    self.remove_record(self.bot_rules[x]['save_has'])
                    return {"message": messages, "section": self.user_section, "input": 0, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                elif (continue_or_return == "3"):
                    self.user_section = self.bot_rules[x]['id']
                    self.record = '|||'
                    return {"message": messages, "section": 0, "input": 0, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                else:
                    messages += self.bot_rules[x]['error_message']
                    self.user_section = 0
                    if (self.bot_rules[x]['error_callback'] == True):
                        return {"message": messages, "section": self.user_section, "input": 0, "retry": 1, "record": self.record.encode('utf-8').encode('base64')}
                    else:
                        return {"message": messages, "section": self.user_section, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                            
        elif (mark_consultation == True):
            if not self.input_value == 0:
                if (self.input_value == 1):
                    prev_sec = self.user_section
                    self.user_section = self.user_sentence
                elif (self.input_value == 2):
                    prev_sec = self.user_section
                    self.user_section = self.user_sentence
                elif (self.input_value == 3):
                    continue_or_return = self.user_sentence
            else:
                messages += self.bot_rules[x]['example_message'] 
                return {"message": messages, "section": self.user_section, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
            if not (self.input_value == 2 or self.input_value == 3):
                if len(self.user_sentence) < 6:
                    now = datetime.datetime.now()
                    self.user_sentence += "-" + str(now.year)
                if (self.is_date(self.user_sentence) == True):
                    exception_dates = ""
                    exception_dates += self.bot_rules[x]['config']['exception_dates'] + ",".replace(" ", "")
                    if self.bot_rules[x]['config']['holidays'] == True:
                        exception_dates += "01/01,10/02,11/02,13/02,14/02,20/03,30/03,01/04,21/04,01/05,13/05,31/05,12/06,21/06,12/08,07/09,23/09,12/10,15/10,28/10,02/11,15/11,20/11,21/12,24/12,25/12,31/12"


                    exceptions_split = exception_dates.split(',')
                    exist = False
                    
                    for p in range(0, len(exceptions_split)):
                        if len(exceptions_split[p]) > 0:
                            exceptions_split[p] = exceptions_split[p].replace('/', '-')
                            if self.user_sentence.count(exceptions_split[p]) > 0:
                                exist = True

                    current_date = datetime.datetime.strptime(self.user_sentence, "%d-%m-%Y").strftime('%Y-%m-%d')

                    weekday = datetime.datetime.strptime(self.user_sentence, "%d-%m-%Y")
                    
                    today = datetime.datetime.now().strftime('%Y-%m-%d')

                  
                    if (current_date < today):
                        exist = True

                    else:
                        date_week = self.get_weekday(weekday).lower()
                        if self.bot_rules[x]['config'].get(date_week):
                            if not (self.bot_rules[x]['config'][date_week] == True):
                                exist = False
                                
                        else:
                            exist = True
                    if (exist == False):
                        dateopen_message = self.bot_rules[x]['dateopen_message'].replace("{%date%}", self.user_sentence.replace('-', '/'))
                        dateopen_message = dateopen_message.encode('utf-8')
                        messages += dateopen_message
                        times = self.bot_rules[x]['config']['query_hours'].replace(' ', '') + ","
                        times_replace = times.split(',')
                        cr = 1
                        for t in range(0, len(times_replace)):
                            if len(times_replace[t]) > 0:
                                time_split = times_replace[t].split('-')
                                
                                time_append = self.bot_rules[x]['config']['query_time']       
                                time_start = datetime.datetime.strptime(time_split[0], '%H:%M').strftime('%H:%M')
                                time_end = datetime.datetime.strptime(time_split[1], '%H:%M').strftime('%H:%M')
                                time_start_raw = datetime.datetime.strptime(time_split[0], '%H:%M')

                                while (time_start < time_end):
                                    messages += "\n" + self.bot_rules[x]['style_choice'].replace('{number}', self.convert_option(cr)).replace('{option}', time_start).encode('utf-8') 
                                    cr += 1

                                    time_start_raw += datetime.timedelta(minutes=int(time_append))
                                    time_start = time_start_raw.strftime('%H:%M')
                                
                        self.append_record('date', self.user_sentence)
                        return {"message": messages, "section": prev_sec, "input": 2, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}

         
                    
                    else:
                        messages += self.bot_rules[x]['datefull_message']
                        if (self.bot_rules[x]['error_callback'] == True):
                            return {"message": messages, "section": prev_sec, "input": 0, "retry": 1, "record": self.record.encode('utf-8').encode('base64')}
                        else:
                            return {"message": messages, "section": prev_sec, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}

                else:
                    messages += self.bot_rules[x]['error_message']
                    if (self.bot_rules[x]['error_callback'] == True):
                        return {"message": messages, "section": prev_sec, "input": 0, "retry": 1, "record": self.record.encode('utf-8').encode('base64')}
                    else:
                        return {"message": messages, "section": prev_sec, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                

            if (self.input_value == 2):
                error = False
                noerror = False
                try:
                    times = self.bot_rules[x]['config']['query_hours'].replace(' ', '') + ","
                    times_replace = times.split(',')
                    cr = 1
                    for t in range(0, len(times_replace)):
                        if len(times_replace[t]) > 0:
                            time_split = times_replace[t].split('-')
                            
                            time_append = self.bot_rules[x]['config']['query_time']       
                            time_start = datetime.datetime.strptime(time_split[0], '%H:%M').strftime('%H:%M')
                            time_end = datetime.datetime.strptime(time_split[1], '%H:%M').strftime('%H:%M')
                            time_start_raw = datetime.datetime.strptime(time_split[0], '%H:%M')

                            while (time_start < time_end):
                                if (cr == int(self.user_sentence)):
                                    self.append_record('time', str(time_start))
                                    noerror = True
                                cr += 1
                                time_start_raw += datetime.timedelta(minutes=int(time_append))
                                time_start = time_start_raw.strftime('%H:%M')
                    if (noerror == False):
                        error = True
                except:
                    error = True

                if (error == False):
                    confirmation_message = self.bot_rules[x]['confirmation_message'].replace("{%date%}", self.obtain_record('date').replace('-','/')).replace("{%time%}", self.obtain_record('time'))
                    confirmation_message = confirmation_message.encode('utf-8')
                    messages += confirmation_message
                    messages += "\n" + self.convert_option(1).encode('utf-8') + " - Select this date\n" + self.convert_option(2).encode('utf-8') + " - Select other date\n" + self.convert_option(3).encode('utf-8') + " - Return to Home"
                    return {"message": messages, "section": prev_sec, "input": 3, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                else:
                    messages += self.bot_rules[x]['error_message']
                    if (self.bot_rules[x]['error_callback'] == True):
                        return {"message": messages, "section": prev_sec, "input": 0, "retry": 1, "record": self.record.encode('utf-8').encode('base64')}
                    else:
                        return {"message": messages, "section": prev_sec, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                
                    
            elif (self.input_value == 3):
                if (continue_or_return == "1"):
                    self.user_section = self.bot_rules[x]['functions']['goto']
                    return {"message": messages, "section": self.user_section, "input": 0, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                elif (continue_or_return == "2"):
                    self.user_section = self.bot_rules[x]['id']
                    self.remove_record('date')
                    self.remove_record('time')
                    return {"message": messages, "section": self.user_section, "input": 0, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                elif (continue_or_return == "3"):
                    self.user_section = self.bot_rules[x]['id']
                    self.record = '|||'
                    return {"message": messages, "section": 0, "input": 0, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                else:
                    messages += self.bot_rules[x]['error_message']
                    self.user_section = 0
                    if (self.bot_rules[x]['error_callback'] == True):
                        return {"message": messages, "section": self.user_section, "input": 0, "retry": 1, "record": self.record.encode('utf-8').encode('base64')}
                    else:
                        return {"message": messages, "section": self.user_section, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}

        elif (wait_input == True): 
            prev_sec = self.user_section
            self.user_section = self.bot_rules[x]['functions']['goto']
            if self.input_value == 0:
                return {"message": messages, "section": prev_sec, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
            else:
                advance = True
                typeinput = self.bot_rules[x]['type']
                try:
                    pass
                except:
                    advance = False

                
                if (advance == False):
                    messages += self.bot_rules[x]['error_message']
                    self.user_section = prev_sec
                    if (self.bot_rules[x]['error_callback'] == True):
                        return {"message": messages, "section": self.user_section, "input": 0, "retry": 1, "record": self.record.encode('utf-8').encode('base64')}
                    else:
                        return {"message": messages, "section": self.user_section, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}

                if self.bot_rules[x].get('save_has'):
                    self.append_record(self.bot_rules[x]['save_has'], self.user_sentence)
                
                return {"message": False, "section": self.user_section, "input": 0, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}

        elif (api_information == True):
            prev_sec = self.user_section
            self.user_section = self.bot_rules[x]['functions']['goto']
            get_url = self.bot_rules[x]['rest_url']

            rest_message = self.bot_rules[x]['rest_message']

            error_message = self.bot_rules[x]['error_message']

            try:
                rest_value = self.rest_information(get_url)
                total_vars = rest_message.count('{%')
                if total_vars > 0:
                    all_vars = rest_message.split('{%')
                    for t in range (1, (total_vars+1)):
                        var = all_vars[t].split('%}')
                        var = var[0]
                        rest_message = rest_message.replace('{%'+var+'%}', str(rest_value[var]))
                messages += rest_message
            except:
                messages += error_message
            return {"message": messages, "section": self.user_section, "input": 0, "retry": 1, "record": self.record.encode('utf-8').encode('base64')}        

        elif (api_integration == True):
            if self.bot_rules[x].get('rest_url_vars'):
                prev_sec = self.user_section
                self.user_section = self.bot_rules[x]['functions']['goto']    
                total_inputs = len(self.bot_rules[x]['rest_url_vars'])
                if (self.input_value < total_inputs):
                    if not (self.input_value == 0):
                        next_input = self.input_value + 1
                        prev_input = self.input_value - 1
                        self.append_record('var_rest_'+self.bot_rules[x]['rest_url_vars'][prev_input]['input_string']+'', self.user_sentence)
                        messages += self.bot_rules[x]['rest_url_vars'][self.input_value]['question']
                        return {"message": messages, "section": prev_sec, "input": next_input, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                    else:
                        messages += self.bot_rules[x]['rest_url_vars'][self.input_value]['question']
                        return {"message": messages, "section": prev_sec, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                else:
                    prev_input = self.input_value - 1
                    self.append_record('var_rest_'+self.bot_rules[x]['rest_url_vars'][prev_input]['input_string']+'', self.user_sentence)
                    if (self.bot_rules[x]['method'] == "GET"):
                        params = "?"
                    else:
                        params = json.loads('{}')
                    for h in range(0, total_inputs):
                        name = self.bot_rules[x]['rest_url_vars'][h]['input_string']
                        value = self.obtain_record('var_rest_'+self.bot_rules[x]['rest_url_vars'][h]['input_string']+'')
                        if (self.bot_rules[x]['method'] == "GET"):
                            params += name + "=" + value + "&"
                        else:
                            params[name] = value
                        self.remove_record('var_rest_'+self.bot_rules[x]['rest_url_vars'][h]['input_string']+'')
                    if (self.bot_rules[x]['method'] == "GET"):
                        params = params[:-1]

                    rest_message = self.bot_rules[x]['rest_message']
                    error_message = self.bot_rules[x]['error_message']
                    get_url = self.bot_rules[x]['rest_url']
                    try:
                        if (self.bot_rules[x]['method'] == "GET"):
                            rest_value = self.rest_information(get_url + params)
                        else:
                            rest_value = self.post_rest_information(get_url, params)
                        total_vars = rest_message.count('{%')
                        if total_vars > 0:
                            all_vars = rest_message.split('{%')
                            for t in range (1, (total_vars+1)):
                                var = all_vars[t].split('%}')
                                var = var[0]
                                rest_message = rest_message.replace('{%'+var+'%}', str(rest_value[var]))
                        messages += rest_message
                    except:
                        messages += error_message
                    
                    return {"message": messages, "section": self.user_section, "input": 0, "retry": 1, "record": self.record.encode('utf-8').encode('base64')}            
                    
        elif (self.bot_rules[x]['sec_type'] == "info"):
            self.user_section = self.bot_rules[x]['functions']['goto']
            return {"message": messages, "section": self.user_section, "input": 0, "retry": 1, "record": self.record.encode('utf-8').encode('base64')}
        else:
            if not self.input_value == 0:
                prev_sec = self.user_section
                self.user_section = self.user_sentence
            else:
                return {"message": messages, "section": self.user_section, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
        try:
            f = int(self.user_section) - 1
        except:
            messages += self.bot_rules[x]['error_message']
            if (self.bot_rules[x]['error_callback'] == True):
                return {"message": messages, "section": prev_sec, "input": 0, "retry": 1, "record": self.record.encode('utf-8').encode('base64')}
            else:
                return {"message": messages, "section": prev_sec, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
        try:
            if len(self.bot_rules[x]['options'][f]['functions']) > 0:

                for d in range (0, len(self.bot_rules[x]['options'][f]['functions'])):
                    if self.bot_rules[x]['options'][f]['functions'].get('goto'):
                        self.user_section = int(self.bot_rules[x]['options'][f]['functions']['goto'])
                        if self.bot_rules[x].get('save_has'):
                            self.append_record(self.bot_rules[x]['save_has'], self.bot_rules[x]['options'][f]['name'])
                        return {"message": messages, "section": self.user_section, "input": 0, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}

                    elif self.bot_rules[x]['options'][f]['functions'].get('close') > 0:
                        if self.bot_rules[x]['options'][f]['functions']['close'] == True:
                            self.user_section = 0
                            return {"message": messages, "section": self.user_section, "input": 0, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}
                            
        except:
            messages += self.bot_rules[x]['error_message']
            self.user_section = x
            if (self.bot_rules[x]['error_callback'] == True):
                return {"message": messages, "section": self.user_section, "input": 0, "retry": 1, "record": self.record.encode('utf-8').encode('base64')}
            else:
                return {"message": messages, "section": self.user_section, "input": 1, "retry": 0, "record": self.record.encode('utf-8').encode('base64')}



        
    def __del__(self):
        #DESTRUCT ALL OBJETS AFTER REQUEST
        self.bot_rules = None
        self.user_section = None
        self.user_sentence = None
        self.input_value = None
        self.retry = None
        self.record = None
        return False

