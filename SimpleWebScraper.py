'''This is a simple Python scraping script to be used as a tutorial.
Some concepts here take a bit of a messy, imperfect way to the solution. However, the priority was to keep the script simple enough to be understood by a beginner'''


'''Import the libraries'''
import requests, pyperclip #I use Pyperclip in the live tutorial, but it's not necessary for the final script
from bs4 import BeautifulSoup as soup #bs4 has a submodule called Beautiful Soup, so we will import the sub module and rename it soup (because it's easier to type)
import pandas as pd #import pandas, but called it pd

'''Here, I will use abcnews to scrape. There is an easier way to scrape this site using RSS, but it wouldn't teach the same skills. So let's do it the slightly harder way.
If using a different site the selectors below would change, and you would have to figure out what the selectors were.'''
abcSoup = soup(requests.get('https://abcnews.go.com/').text) #use bs4 to get a HTML-parsed version of the abc site
#print(abcSoup.prettify()) #delet the # at start of this line if you want to examine the HTML

'''Now I know my selectors, I can grab all the headlines and links and record them to a dictionary'''
stories = {} #create my empty dictionary
headlines = abcSoup.select('.headlines-ul a') #using my souped version of the homepage, select all links within the headlines-ul class
#print(len(headlines)) #printing the length of your selection is useful for checking if you selected the right elements. If the length is 0 you didn't grab the right thing.
for h in range(len(headlines)): #for each headline I got...
    if headlines[h].get('href') != 'javascript:void(0);': #some of the links are javascript videos - let's ignore those. So only proceed if the 'href' (link) does not equal (!=)...
        stories[headlines[h].text] = {'url':headlines[h].get('href')} #add my story to the dictionary and add its url
#print(stories) #if you want to print your whole dictionary here you can


'''Now I will go through each story and use it's URL to go to the page and get the body of the article'''
for story in stories: #for each story
    pageSoup = soup(requests.get(stories[story]['url']).text) #create a new soup
    stories[story]['text'] = pageSoup.select('.Article__Content')[0].text #select the article content - this creates a list of 1, take the first item in the list [0], and extract teh text


'''Pandas really hates the way we have set up our dictionary currently. There is a cleaner way to do the beneath that is slightly faster, but the beneath method is much simpler to understand.
We want to restructuer our dictionary so Pandas can read it more easily.'''
convertedStories = {'headline':[],'url':[],'text':[]} #create a new blank dictionary with each of our CSV column headings as a blank list
for story in stories:
    convertedStories['headline'].append(story) #go through our stories dictionary, and add each item to the relevant list in the new dictionary
    convertedStories['url'].append(stories[story]['url'])
    convertedStories['text'].append(stories[story]['text'])

'''With my converted dictionary made, I can now turn it into a Pandas dataframe and export to CSV'''
storiesDF = pd.DataFrame.from_dict(convertedStories)
storiesDF.to_csv('abcnews.csv')

        
        


