# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 20:47:51 2021

@author: Faizan
"""
import json
import requests
import datetime as dt

with open("forexData.txt", 'r') as file:
    data = json.load(file)
forexList = set()
forexPair = set()
profileFeatures = {
    'name': ['name'],
    'country': ['country', 'region', 'area', 'place'],
    'subunit': ['subunit', 'unit'],
    'banknotes':['notes', 'banknotes', 'denominations', 'bills'],
    'coins': ['coins']
    }

for d in data['response']:
    forexPair.add(d['symbol'])
    temp=d['symbol'].split('/')
    forexList.update(temp)

def checkForexSymbol(word):
    return word in forexList


def checkForexPair(word):
    return word in forexPair


def checkProfileFeature(word):
    for feature in profileFeatures:
        if feature.count(word) > 0:
            return feature
    return 'NA'

def updateForexList():
    response = requests.get(
        "https://fcsapi.com/api-v2/forex/list?type=forex&access_key=nSjVeSWxYCDrQhVQoqxzU")
    print(response.status_code)
    forexData = response.json()
    with open("forexData.txt", 'w') as file:
        json.dump(forexData, file)
    print(forexData)

def getProfileFeatures(symbol, feature=None):
    if checkForexSymbol(symbol):
        response = requests.get("https://fcsapi.com/api-v3/forex/profile?symbol={}&access_key=nSjVeSWxYCDrQhVQoqxzU".format(symbol))
        profile = response.json()
        if feature == None or checkProfileFeature(feature) == 'NA':
            return profile["response"][0]
        else:
            return profile["response"][0][checkProfileFeature(feature)]
    else: return "could not process symbol"    

def getPivots(pair):
    if checkForexPair(pair):
        response = requests.get("https://fcsapi.com/api-v3/forex/pivot_points?symbol={}&period=1d&access_key=nSjVeSWxYCDrQhVQoqxzU".format(pair))
        ty = response.json()
        payload=ty["response"]["pivot_point"]['classic']
        pivot=payload["pp"]
        support=payload["R1"]
        resistance=payload["S1"]        
        return pivot, support, resistance
    else: return "could not process pair"  

def recommendationMA(pair):
    if checkForexPair(pair):
        response = requests.get("https://fcsapi.com/api-v2/forex/ma_avg?symbol={}&period=1d&access_key=nSjVeSWxYCDrQhVQoqxzU".format(pair))
        payload = response.json()
        return payload["response"]["oa_summary"]           
    else: return "could not process pair"  
       
def binaryForexConversion(currency_1, currency_2, amount=1, date=None):
    accessKey = "&access_key=nSjVeSWxYCDrQhVQoqxzU"
    pair = currency_1+'/'+currency_2
    if date == None:
        url = "https://fcsapi.com/api-v3/forex/latest?symbol="
        api = url+pair+"&candle=close"+accessKey
    else:
        url = "https://fcsapi.com/api-v3/forex/history?symbol="
        dateInterval = "&period=1d&from="+date+"T12:00&to=" + \
            (dt.date.today().isoformat())+"T12:00"
        api = url+pair+dateInterval+"&candle=close"+accessKey
    response = requests.get(api)
    payloadDict = response.json()
    if date == None:
        convertedAmount = float((payloadDict["response"][0]["c"]))*amount
    else:
        key = list(payloadDict["response"].keys())[0]
        convertedAmount = float(payloadDict["response"].get(key)['c'])*amount
    return convertedAmount

forexList