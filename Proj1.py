import CYKParse
import Tree
import ForexSymbols as fs
requestInfo = {
        'currency_1': '',
        'currency_2': '',
        'amount': '',
        'date': '',
        'feature': ''
}
haveGreeted = False
amountInitialized=False
dateInitialized=False
currency_1_initialized=False
currency_2_initialized=False# Given the collection of parse trees returned by CYKParse, this function returns the one corresponding to the complete sentence.
setCurrency2=False
pivotRequested=False
giveRecommendation=False
feature=''


def getSentenceParse(T):
    sentenceTrees = { k: v for k,v in T.items() if k.startswith('S/0') }
    completeSentenceTree = max(sentenceTrees.keys())
    return T[completeSentenceTree]
# Processes the leaves of the parse tree to pull out the user's request.
def updateRequestInfo(Tr):
    
    global amountInitialized
    global dateInitialized
    global requestInfo
    global currency_1_initialized
    global currency_2_initialized
    global setCurrency2
    global pivotRequested
    global feature
    global giveRecommendation

    """
    LOOP TWICE; IN THE FIRST LOOP FIGURE OUT WHETHER BOTH THE CURRENCIES ARE PROVIDED
    THE DATE IS PROVIDED, AND/OR THE CONVERSION AMOUNT IS PROVIDED?
    """    
    for leaf in Tr.getLeaves():
        if fs.checkProfileFeature(leaf[1]) != 'NA':
           feature=fs.checkProfileFeature(leaf[1])     
        elif leaf[0] == 'Amount': 
            requestInfo['amount'] = leaf[1] 
            amountInitialized=True 
            
        elif setCurrency2 is False and leaf[0] == 'Forex':
            requestInfo['currency_1'] = leaf[1]
            setCurrency2=True
            currency_1_initialized=True
            
        elif leaf[0] == 'Forex' and setCurrency2:
            requestInfo['currency_2'] = leaf[1]      
            currency_2_initialized=True
            
        elif leaf[0]=='Date':
            requestInfo['date'] = leaf[1]            
            dateInitialized=True
            
        if leaf[1].lower() in ['pivots', 'pivot', 'indicators', 'support', 'resistance']:
            pivotRequested=True
            
        if leaf[1].lower() in ['recommendation', 'recommended', 'strategy', 'prediction', 'forecast', 'advice']:
            giveRecommendation=True
            
    if currency_2_initialized==False and feature != 'NA': #single forex symbol provided, only possible operation is to get profile features       
        requestInfo['feature']=feature
            
# This function contains the data known by our simple chatbot
#def performConversion(c1, c2, amount=1, date=None):
#    if location == 'Irvine':
#          if time == 'now' or time=='today': # today = now
#            return '68'
#          elif time == 'tomorrow':
#            return '70'
#          elif time=='yesterday': 
#            return '65'            
#          else: 
#            return 'unknown' 
#        #Added Tustin
#    elif location == 'Tustin':
#        if time == 'now' or time=='today': 
#            return '72'
#        elif time == 'tomorrow':
#            return '78'
#        elif time=='yesterday': # added yesterday
#            return '84' 
#        #Added Pasadena
#    elif location == 'Pasadena':
#        if time == 'now' or time=='today':
#            return '66'
#        elif time == 'tomorrow':
#            return '67'
#        elif time=='yesterday':
#           return '82' 
#    else:
#        return 'unknown'

# Format a reply to the user, based on what the user wrote.

def reply():
    global requestInfo
    global haveGreeted  
    
    if not haveGreeted:
        print("Hello, what forex conversion query would you like to run?")
        haveGreeted = True
        
    if requestInfo['currency_1']=='' and requestInfo['currency_2']=='':
        print("Please select a pair of forex currencies from the list below for conversion")
        print(fs.forexPair)
        
    if currency_1_initialized and currency_2_initialized==False and requestInfo['feature'] != 'NA':
        c1=requestInfo['currency_1']
        response=fs.getProfileFeatures(c1, feature)
        if feature in ['coins', 'banknotes']:
            print("The {} of {} are {}".format(feature, c1, response))
        else: 
            print("The {} of {} is {}".format(feature, c1, response))
    elif currency_1_initialized and currency_2_initialized:
        c1,c2= requestInfo['currency_1'], requestInfo['currency_2']           
        if pivotRequested:
            p, s, r = fs.getPivots(c1 + '/' + c2)
            print('{} is the pivot price of {} to {} based on a support level {} and resistance level {}'.format(p, c1, c2, s, r))
        if giveRecommendation:
            print("The trading strategy based on the moving average is: ", fs.recommendationMA(c1+'/'+c2))
        else:
            amount=float(requestInfo['amount']) if amountInitialized else 1.0
            date=requestInfo['date'] if dateInitialized else None
            conversion=fs.binaryForexConversion(c1, c2, amount, date)
            if date is None:
                print('The latest conversion data suggests that as of this moment {} {} in {} is {}'.format(amount, c1, c2, conversion))
            else: 
                print('The conversion rate of {} {} in {} was {} on {}'.format(amount, c1, c2, conversion, date))
        reset()
        
def reset():    
    global amountInitialized
    global dateInitialized
    global currency_1_initialized
    global currency_2_initialized
    global setCurrency2
    global pivotRequested
    global feature
    global giveRecommendation
    global requestInfo
    
    amountInitialized=False
    dateInitialized=False
    currency_1_initialized=False
    currency_2_initialized=False
    setCurrency2=False
    pivotRequested=False
    feature=''
    giveRecommendation=False
    requestInfo = {
        'currency_1': '',
        'currency_2': '',
        'amount': '',
        'date': '',
        'feature': ''
}
    
# A simple hard-coded proof of concept.
def main():
    global requestInfo
    T, P = CYKParse.CYKParse(['what', 'is','the','recommended', 'advice', 'for', 'USD', 'to', 'PKR'], CYKParse.getGrammarWeather())
    sentenceTree=(getSentenceParse(T))
    updateRequestInfo(sentenceTree)
    reply()
    
    T, P = CYKParse.CYKParse(['what','are', 'the', 'banknotes', 'of', 'USD'], CYKParse.getGrammarWeather())
    sentenceTree=(getSentenceParse(T))
    updateRequestInfo(sentenceTree)
    reply()
    
    T, P = CYKParse.CYKParse(['what','are', 'the', 'pivots', 'and', 'recommendation', 'for', 'USD', 'to', 'PKR'], CYKParse.getGrammarWeather())
    sentenceTree=(getSentenceParse(T))
    updateRequestInfo(sentenceTree)
    reply()
    
    T, P = CYKParse.CYKParse(['what','is', 'the', 'value', 'of', '40', 'USD', 'in', 'INR'], CYKParse.getGrammarWeather())
    sentenceTree=(getSentenceParse(T))
    updateRequestInfo(sentenceTree)
    reply()

main()