# Code for CS 171, Winter, 2021
from dateutil.parser import parse
import datetime as dt
import Tree
import json
import ForexSymbols as fs
verbose = False

def printV(*args):
   if verbose:
     print(*args)

# A Python implementation of the AIMA CYK-Parse algorithm in Fig. 23.5 (p. 837).
def CYKParse(words, grammar):
    T = {}
    P = {}
    # Instead of explicitly initializing all P[X, i, k] to 0, store
    # only non-0 keys, and use this helper function to return 0 as needed.
    def getP(X, i, k):
        key = str(X) + '/' + str(i) + '/' + str(k)
        if key in P:
            return P[key]
        else:
            return 0
    # Insert lexical categories for each word
    #
    for i in range(len(words)):
        for X, p in getGrammarLexicalRules(grammar, words[i]):
            P[X + '/' + str(i) + '/' + str(i)] = p
            T[X + '/' + str(i) + '/' + str(i)] = Tree.Tree(X, None, None, lexiconItem=words[i])
    printV('P:', P)
    printV('T:', [str(t)+':'+str(T[t]) for t in T])
    
    
    # Construct X_i:j from Y_i:j + Z_j+i:k, shortest spans first
    for i, j, k in subspans(len(words)):
        for X, Y, Z, p in getGrammarSyntaxRules(grammar): 
            #Condition added to check when X if of the form X-> Y[P]
            # rightChild of all atomic syntatic categories will be None
                if Z==None: # if X->Y[p]-> X.rightChild==None
                    #the comparison will split words over j
                    # and compare both sequences of words, i:k and j+1:k, to match with Category Y
                    PYZ = getP(Y, i, j) * p
                    if PYZ > getP(X, i, j):
                        printV('     inserting from', i, '-', k, ' ', X, '->',Y,  T[Y+'/'+str(i)+'/'+str(j)],
                            'because', PYZ, '=', getP(Y, i, j), '*', p, '>', getP(X, i, j), '=',
                            'getP(' + X + ',' + str(i) + ',' + str(j) + ')')
                        P[X + '/' + str(i) + '/' + str(j)] = PYZ
                        #Tree class constructor and functions have been modified to support the C1F implementation
                        # The rightChild paramter will be set to None by default if it is not provided when instantiating a Tree object
                        T[X + '/' + str(i) + '/' + str(j)] = Tree.Tree(X, T[Y+'/'+str(i)+'/'+str(j)])
                    # checking words j+1:k 
                    if getP(Y, j+1, k) * p > getP(X, j+1, k): 
                        T[X + '/' + str(j+1) + '/' + str(k)]=Tree.Tree(X, T[Y+'/'+str(j+1)+'/'+str(k)])
                        P[X + '/' + str(j+1) + '/' + str(k)] = getP(Y, j+1, k) * p

                else:
                    printV('i:', i, 'j:', j, 'k:', k, '', X, '->', Y, Z, '['+str(p)+']', 
                    'PYZ =' ,getP(Y, i, j), getP(Z, j+1, k), p, '=', getP(Y, i, j) * getP(Z, j+1, k) * p)
                    PYZ = getP(Y, i, j) * getP(Z, j+1, k) * p
                    if PYZ > getP(X, i, k):
                        printV('     inserting from', i, '-', k, ' ', X, '->', T[Y+'/'+str(i)+'/'+str(j)], T[Z+'/'+str(j+1)+'/'+str(k)],
                            'because', PYZ, '=', getP(Y, i, j), '*', getP(Z, j+1, k), '*', p, '>', getP(X, i, k), '=',
                            'getP(' + X + ',' + str(i) + ',' + str(k) + ')')
                        P[X + '/' + str(i) + '/' + str(k)] = PYZ
                        T[X + '/' + str(i) + '/' + str(k)] = Tree.Tree(X, T[Y+'/'+str(i)+'/'+str(j)], T[Z+'/'+str(j+1)+'/'+str(k)])             
    printV('T:', [str(t)+':'+str(T[t]) for t in T])
    return T, P


# Python uses 0-based indexing, requiring some changes from the book's
# 1-based indexing: i starts at 0 instead of 1
def subspans(N):
    for length in range(2, N+1):
        for i in range(N+1 - length):
            k = i + length - 1
            for j in range(i, k):
                yield i, j, k

# These two getXXX functions use yield instead of return so that a single pair can be sent back,
# and since that pair is a tuple, Python permits a friendly 'X, p' syntax
# in the calling routine.
def getGrammarLexicalRules(grammar, word):  
    if  fs.checkProfileFeature(word.lower()) != 'NA':
        yield 'Adverb', 0.05
        
    if fs.checkForexSymbol(word):
        yield 'Forex', 0.25
        
    try:
        dt.date.fromisoformat(word)
        yield 'Date', 0.1   
        
    except Exception: 
            pass
        
    for rule in grammar['lexicon']:
        if rule[1] == word:
            yield rule[0], rule[2]
    try:
        float(word)
        yield 'Amount', 0.1
    except Exception: 
            pass


def getGrammarSyntaxRules(grammar):
    
    rulelist = []
    for rule in grammar['syntax']:
         yield rule[0], rule[1], rule[2], rule[3]
    
# 'Grammar' here is used to include both the syntax part and the lexicon part.
# E0 from AIMA, ps. 834.  Note that some syntax rules were added or modified 
# to shoehorn the rules into Chomsky Normal Form. 
def getGrammarE0():
    return {
        'syntax' : [
            ['S', 'NP', 'VP', 0.9 * 0.45 * 0.6],
            ['S', 'Pronoun', 'VP', 0.9 * 0.25 * 0.6],
            ['S', 'Name', 'VP', 0.9 * 0.10 * 0.6],
            ['S', 'Noun', 'VP', 0.9 * 0.10 * 0.6],
            ['S', 'NP', 'Verb', 0.9 * 0.45 * 0.4],
            ['S', 'Pronoun', 'Verb', 0.9 * 0.25 * 0.4],
            ['S', 'Name', 'Verb', 0.9 * 0.10 * 0.4],
            ['S', 'Noun', 'Verb', 0.9 * 0.10 * 0.4],
            ['S', 'S', 'Conj+S', 0.1],
            ['Conj+S', 'Conj', 'S', 1.0],
            ['NP', 'Article', 'Noun', 0.25],
            ['NP', 'Article+Adjs', 'Noun', 0.15],
            ['NP', 'Article+Adjective', 'Noun', 0.05],
            ['NP', 'Digit', 'Digit', 0.15],
            ['NP', 'NP', 'PP', 0.2],
            ['NP', 'NP', 'RelClause', 0.15],
            ['NP', 'NP', 'Conj+NP', 0.05],
            ['Article+Adjs', 'Article', 'Adjs', 1.0],
            ['Article+Adjective', 'Article', 'Adjective', 1.0],
            ['Conj+NP', 'Conj', 'NP', 1.0],
            ['VP', 'VP', 'NP', 0.6 * 0.55],
            ['VP', 'VP', 'Adjective', 0.6 * 0.1],
            ['VP', 'VP', 'PP', 0.6 * 0.2],
            ['VP', 'VP', 'Adverb', 0.6 * 0.15],
            ['VP', 'Verb', 'NP', 0.4 * 0.55],
            ['VP', 'Verb', 'Adjective', 0.4 * 0.1],
            ['VP', 'Verb', 'PP', 0.4 * 0.2],
            ['VP', 'Verb', 'Adverb', 0.4 * 0.15],
            ['Adjs', 'Adjective', 'Adjs', 0.8],
            ['PP', 'Prep', 'NP', 0.65],
            ['PP', 'Prep', 'Pronoun', 0.2],
            ['PP', 'Prep', 'Name', 0.1],
            ['PP', 'Prep', 'Noun', 0.05],
            ['RelClause', 'RelPro', 'VP', 0.6],
            ['RelClause', 'RelPro', 'Verb', 0.4],
    
        ],
        'lexicon' : [
            ['Noun', 'stench', 0.05],
            ['Noun', 'breeze', 0.05],
            ['Noun', 'wumpus', 0.05],
            ['Noun', 'pits', 0.05],
            ['Noun', 'dungeon', 0.05],
            ['Noun', 'frog', 0.05],
            ['Noun', 'balrog', 0.7],
            ['Verb', 'is', 0.1],
            ['Verb', 'feel', 0.1],
            ['Verb', 'smells', 0.1],
            ['Verb', 'stinks', 0.05],
            ['Verb', 'wanders', 0.65],
            ['Adjective', 'right', 0.1],
            ['Adjective', 'dead', 0.05],
            ['Adjective', 'smelly', 0.02],
            ['Adjective', 'breezy', 0.02],
            ['Adjective', 'green', 0.81],
            ['Adverb', 'here', 0.05],
            ['Adverb', 'ahead', 0.05],
            ['Adverb', 'nearby', 0.02],
            ['Adverb', 'below', 0.88],
            ['Pronoun', 'me', 0.1],
            ['Pronoun', 'you', 0.03],
            ['Pronoun', 'I', 0.1],
            ['Pronoun', 'it', 0.1],
            ['Pronoun', 'she', 0.67],
            ['RelPro', 'that', 0.4],
            ['RelPro', 'which', 0.15],
            ['RelPro', 'who', 0.2],
            ['RelPro', 'whom', 0.02],
            ['RelPro', 'whoever', 0.23],
            ['Name', 'Ali', 0.01],
            ['Name', 'Bo', 0.01],
            ['Name', 'Boston', 0.01],
            ['Name', 'Marios', 0.97],
            ['Article', 'the', 0.4],
            ['Article', 'a', 0.3],
            ['Article', 'an', 0.05],
            ['Article', 'every', 0.05],
            ['Prep', 'to', 0.2],
            ['Prep', 'in', 0.1],
            ['Prep', 'on', 0.05],
            ['Prep', 'near', 0.10],
            ['Prep', 'alongside', 0.55],
            ['Conj', 'and', 0.5],
            ['Conj', 'or', 0.1],
            ['Conj', 'but', 0.2],
            ['Conj', 'yet', 0.2],
            ['Digit', '0', 0.1],
            ['Digit', '1', 0.1],
            ['Digit', '2', 0.1],
            ['Digit', '3', 0.1],
            ['Digit', '4', 0.1],
            ['Digit', '5', 0.1],
            ['Digit', '6', 0.1],
            ['Digit', '7', 0.1],
            ['Digit', '8', 0.1],
            ['Digit', '9', 0.1]
        ]
    }

# To experiment with the 'garden path' sentence 'the old man the boat' 
def getGrammarGardenPath():
    return {
        'syntax' : [
            ['S', 'NP', 'VP', 0.25],
            ['S', 'Noun', 'VP', 0.25],
            ['S', 'NP', 'Verb', 0.25],
            ['S', 'Noun', 'Verb', 0.25],
            ['NP', 'Article', 'Noun', 0.4],
            ['NP', 'Article+Adjs', 'Noun', 0.2],
            ['NP', 'Article+Adjective', 'Noun', 0.4],
            ['Article+Adjs', 'Article', 'Adjs', 1.0],
            ['Article+Adjective', 'Article', 'Adjective', 1.0],
            ['Adjs', 'Adjective', 'Adjs', 0.8],
            ['VP', 'Verb', 'NP', 1.0],
        ],
        'lexicon' : [
            ['Noun', 'man', 0.5],
            ['Noun', 'old', 0.4],
            ['Noun', 'boat', 0.1],
            ['Verb', 'man', 0.1],
            ['Verb', 'sail', 0.1],
            ['Verb', 'think', 0.8],
            ['Adjective', 'old', 0.1],
            ['Adjective', 'young', 0.1],
            ['Adjective', 'red', 0.8],
            ['Article', 'the', 0.4],
            ['Article', 'a', 0.3],
            ['Article', 'an', 0.05],
            ['Article', 'every', 0.05]
        ]
    }

# To experiment with 'I saw a man with my telescope' 
def getGrammarTelescope():
    return {
        'syntax' : [
            ['S', 'Pronoun', 'VP', 1],
            ['VP', 'Verb', 'NP', 0.6],
            ['VP', 'Verb', 'NP+AdverbPhrase', 0.4],
            ['NP', 'Article', 'Noun', 0.3],
            ['NP', 'Adjective', 'Noun', 0.3],
            ['NP', 'NP', 'AdjectivePhrase', 0.4],
            ['NP+AdverbPhrase', 'NP', 'AdverbPhrase', 1.0],
            ['AdverbPhrase', 'Preposition', 'NP', 1.0],
        ],
        'lexicon' : [
            ['Pronoun', 'I', 1.0],
            ['Noun', 'man', 0.8],
            ['Noun', 'telescope', 0.2],
            ['Verb', 'saw', 1.0],
            ['Article', 'the', 0.7],
            ['Article', 'a', 0.3],
            ['Adjective', 'my', 1.0],
            ['Preposition', 'with', 1.0],
         ]
    }

# Sample sentences:
# Hi, I am Peter. I am Peter. Hi, my name is Peter. My name is Peter.
# What is the temperature in Irvine? What is the temperature in Irvine now? 
# What is the temperature in Irvine tomorrow? 

# NounPhrase has been extended by using C1F and other rules to encompass the NP+AdverbPhrase category
def getGrammarWeather():
    body= {
        'syntax' : [
            ['S', 'Greeting', 'S', 0.25],            
            ['S', 'NP', 'VP', 0.50],
                #['S', 'Pronoun', 'VP', 0.25], subset of S->NPVP[p]  
            ['S', 'WQuestion', 'VP', 0.25],
            ['NP', 'Noun', None,  0.15], #C1F Rule: NP-> Noun[0.15]
            ['NP', 'Forex', None, 0.1], #C1F Rule: NP-> Name[0.1]
            ['NP', 'NP', 'Forex', 0.05],
            ['NP', 'Forex', 'DatePhrase', 0.1],
            ['NP', 'Pronoun',None, 0.1], #C1F Rule: NP-> Pronoun[0.1]
            ['NP', 'Date', None, 0.1],
            ['NP', 'NP', 'AdverbPhrase', 0.15],  
            ['NP', 'Forex', 'AdverbPhrase', 0.15],  

                #  ['NP+AdverbPhrase', 'NP', 'AdverbPhrase', 0.2], # NP-> NPAP
                #  ['NP+AdverbPhrase', 'Noun', 'AdverbPhrase', 0.2], NP -> NP[Noun]AP
                #  ['NP+AdverbPhrase', 'Noun', 'Adverb', 0.2],#NP->NP[Noun]AP[Adverb]
                #  ['NP+AdverbPhrase', 'NP', 'Adverb', 0.15], # NP->NPAP[Adverb]
            ['NP', 'Article', 'NP', 0.1],
            ['NP', 'Amount', 'NP', 0.2],
            ['NP', 'Adjective', 'NP', 0.1],
            ['NP', 'AdverbPhrase', 'NP', 0.2],
                #  ['NP+AdverbPhrase', 'Adverb', 'Noun', 0.05], NP->AP[Adverb]NP[Noun]
                #  ['NP+AdverbPhrase', 'Adverb', 'NP+AdverbPhrase', 0.05], 
                #  ['NP+AdverbPhrase', 'Adverb', 'NP', 0.05], NP->AP[Adverb][NP]
                #  ['NP+AdverbPhrase', 'AdverbPhrase', 'NP', 0.2], #NP -> APNP     
                #  ['NP+AdverbPhrase', 'AdverbPhrase', 'Noun', 0.05], NP->APNP[Noun]
                
            ['AdverbPhrase', 'Adverb', None,  0.2], #C1F, AP-> Adverb[0.2]          
            ['AdverbPhrase', 'Adverb', 'AdverbPhrase', 0.2],
            ['AdverbPhrase', 'AdverbPhrase', 'Adverb', 0.3],
            ['AdverbPhrase', 'Preposition', 'AdverbPhrase', 0.3],
            ['VP', 'Verb', 'NP', 0.80],
                # ['VP', 'Verb', 'Name', 0.2], NP->Noun
                # ['VP', 'Verb', 'NP+AdverbPhrase', 0.3], #NP covers all cases for NP+AP, NP+AP is a subset of NP                     
            ['VP', 'Verb', None, 0.20], # C1F rule, VP->Verb[p]
            ['VP', 'AdverbPhrase', 'VP', 0.2],
            ['AdverbPhrase', 'Preposition', 'NP', 0.3], #Added for part 5 for types 'in' 'city'
            ['NP', 'Preposition', 'AdverbPhrase', 0.10],
            ['NP', 'AdverbPhrase', 'DatePhrase', 0.3], #Added for part 5 for types 'in' 'city'
            ['DatePhrase', 'Preposition', 'Date', 1.0], # Part 5 Added NP-> PrepAP for phrases like 'than *city*'
################################################# PHASE 3 ############################################
################################################# GRAMMAR RULES ############################################
            ],
        'lexicon' : [
            ['Greeting', 'hi', 0.5],
            ['Greeting', 'hello', 0.5],
            ['WQuestion', 'what', 0.3],
            ['WQuestion', 'when', 0.25],
            ['WQuestion', 'which', 0.25],
            ['WQuestion', 'how', 0.25],
            ['WQuestion', 'Will', 0.20], # added for 5
            ['Verb', 'am', 0.4],
            ['Verb', 'is', 0.3],
            ['Verb', 'are', 0.1],
            ['Verb', 'be', 0.2], # added for 5
            ['Name', 'Peter', 0.1],
            ['Name', 'Sue', 0.1],
            ['Name', 'Irvine', 0.3],
       
            #['RealNumber', 10, 0.25], # added for phase 3 
            ['Pronoun', 'I', 1.0],
            ['Noun', 'man', 0.2],
            ['Noun', 'name', 0.2],
            ['Adverb', 'recommendation', 0.1],
            ['Adverb', 'strategy', 0.1],
            ['Adverb', 'pivots', 0.1],
            ['Article', 'the', 0.7],
            ['Adverb', 'value', 0.1],
            ['Adverb', 'worth', 0.1],
            ['Adverb', 'prediction', 0.1],
            ['Adverb', 'forecast', 0.1],
            ['Adverb', 'advice', 0.1],
            ['Adverb', 'recommended', 0.1],
            ['Adverb', 'and', 0.15], # added for Phase 3                
            ['Article', 'of', 0.1],
            ['Article', 'a', 0.3],
            ['Article', 'for', 0.25],
            ['Adjective', 'my', 1.0],
            ['Adverb', 'now', 0.2],
            ['Adverb', 'today', 0.2], # added for 5
            ['Adverb', 'tomorrow', 0.2], #added for 5
            ['Adverb', 'hotter', 0.2], # added for 5
            ['Adverb', 'yesterday', 0.2],
            ['Adverb', 'much', 0.2],
            #['Adverb', 'USD', 0.25], # added for 5
            #['Adverb', 'PKR', 0.25], # added for 5
            ['Preposition', 'with', 0.25],
            ['Preposition', 'in', 0.20],
            ['Preposition', 'than', 0.20], # added for 5
            ['Preposition', 'to', 0.05], # added for Phase 3
            ['Preposition', 'on', 0.15], # added for Phase 3  
            ['Preposition', 'for', 0.15], # added for Phase 3                
         ],
    }
    return body
    
# Unit testing code
if __name__ == '__main__':
    #verbose = True
    #CYKParse(['hi', 'I', 'is'], getGrammarWeather())
    #CYKParse(['the', 'wumpus', 'is', 'dead'], getGrammarE0())
    #CYKParse(['the', 'old', 'man', 'sail', 'the', 'boat'], getGrammarGardenPath())
    #CYKParse(['I', 'saw', 'a', 'man', 'with', 'my', 'telescope'], getGrammarTelescope())
    #CYKParse(['my', 'name', 'is', 'Peter'], getGrammarWeather())
    #CYKParse(['hi', 'I', 'am', 'Peter'], getGrammarWeather())
    #CYKParse(['what', 'is', 'the', 'temperature', 'in', 'Irvine'], getGrammarWeather())
    #CYKParse(['what', 'is', 'the', 'temperature', 'in', 'Irvine', 'now'], getGrammarWeather())
    #CYKParse(['what', 'is', 'the', 'temperature', 'now', 'in', 'Irvine'], getGrammarWeather())
    #CYKParse(['Will', 'tomorrow', 'be', 'hotter', 'than', 'today','in', 'Irvine'], getGrammarWeather())
    #CYKParse(['what', 'is', 'the', 'value', 'of', '40', 'USD', 'in', 'PKR', 'in', '2008'], getGrammarWeather())
    #CYKParse(['what', 'is', 'the', 'value', 'of', '40', 'USD', 'in', 'PKR', 'in', '2008'], getGrammarWeather())
   # CYKParse(['what','is', 'the', 'value', 'of', '40', 'USD', 'in', 'PKR'], getGrammarWeather())
      
    print(CYKParse(['what', 'are','the','recommended', 'advice', 'and', 'pivots', 'for', 'USD', 'to', 'PKR'], getGrammarWeather()))