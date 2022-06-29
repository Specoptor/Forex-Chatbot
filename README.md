Natural Language Processing Project for CS-171 Winter 

A baseline implemenation of tailor-built lexicon categories as a proof of concept for predicitive analytics, Information Retrieval search engine, and other intelligent systems.

https://github.com/Specoptor/Forex-Chatbot/blob/7bc994c3ba8d4862bfec031a0f49934e63c214df/171,%20Report%20part%204.pdf
for complete implementation & project details

https://github.com/Specoptor/Forex-Chatbot/blob/7bc994c3ba8d4862bfec031a0f49934e63c214df/CYKParse.py (util)
lexicons for classification of Forex & financial terminologies.
Implements text processing, syntex checking, grammar rules derived using CYK Parse;
implementation of some algorithms largely follow from the examples given in the book: Artificial Intelligence, a modern approach. 

https://github.com/Specoptor/Forex-Chatbot/blob/7bc994c3ba8d4862bfec031a0f49934e63c214df/ForexSymbols.py (business logic)
acts as the controller & repository layer to handle api calls, and composable data objects 
parse payload obtained from currency models, preprocess and give structure to data for syntex checking, handle third party integrations, 

https://github.com/Specoptor/Forex-Chatbot/blob/7bc994c3ba8d4862bfec031a0f49934e63c214df/Proj1.py (client interface)

Developed heuristics to mapsearch queries by calling the most probable API callto retrieve the required payload. •Automated text processing bygenerating meaningful       responses from JSON payloads(dialogue generation).
