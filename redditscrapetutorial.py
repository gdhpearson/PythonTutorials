'''A simple script to scrape Reddit data with PRAW and one to scrape with PSAW

These scripts are not the most efficient version possible, but do the job well enough, and are designed to be easily understood by those new to Python.'''

'''First of all import all the necessary libraries'''
import praw, time
import datetime as dt
import pandas as pd
from praw.models import MoreComments


'''This allows praw to access Reddit, you will need your own credentials for this to work'''
reddit = praw.Reddit(client_id='', #CLIENT ID, THE SHORTER ONE ON REDDIT'S API 
                     client_secret='', #SECRET ID, THE LONGER ONE ON REDDIT'S API
                     user_agent= '',#NAME OF YOUR API AGENT
                     #these two should only be needed if you need an account to see the data
                     #username= '', #YOUR REDDIT USERNAME
                     #password='', #YOUR REDDIT PASSWORD
                    )


'''create empty dictionaries where we will save our information from'''
postDictionary = {}
commentDictionary = {}

'''now to get the information'''
sub = reddit.subreddit("coronavirus") #set the subreddit
posts = sub.new(limit=500) #this gets the 500 most recent posts, can also sort by top, hot etc.


'''We have now downloaded our posts, so now we need to loop through and extract relevant information
Praw has some great documentation and you can find all the features for all posts and comments at https://praw.readthedocs.io/en/latest/code_overview/praw_models.html'''
for submission in posts: #for every submission we downloaded
    postDictionary[submission] = {'submissionDate':submission.created_utc,
                         'author':submission.author,
                         'votes':submission.score,
                         'url':submission.url,
                         'commsNum':submission.num_comments,
                         'body':submission.selftext} #add it to our empty dictionary and then record this information
    submission.comments.replace_more(limit=0) #reddit has this weird issue with large comment trees, this gets around it
    for comment in submission.comments.list(): #for each comment within each submission
        commentDictionary[submission] = {'submissionDate':comment.created_utc,
                                      'author':comment.author,
                                      'votes':comment.score,
                                      'url':submission.url,
                                         'commsNum':submission.num_comments,
                                         'body':comment.body} #add the following information

        
'''Currently the date/time is recorded as a UNIX timestamp which is unreadable, so let's make it something we can understand'''
for submission in postDictionary:
    postDictionary[submission]['submissionDateReadable'] = dt.datetime.fromtimestamp(postDictionary[submission]['submissionDate']).strftime('%Y-%m-%d %H:%M%S')

for comment in commentDictionary:
    commentDictionary[comment]['submissionDateReadable'] = dt.datetime.fromtimestamp(commentDictionary[comment]['submissionDate']).strftime('%Y-%m-%d %H:%M%S')


'''We want to convert the data to a Pandas dataframe, but Pandas doesn't like the way our data is structured right now, so let's change it
Pandas would like our data in lists.'''
listOfInfo = ['submissionDate','submissionDateReadable','author','votes','url','commsNum','body'] #this is a list of all our variables, we can loop through to get them

postCollection = {'id':[]} #create emoty dicts with the one var that is not in our list above
commentCollection = {'id':[]}

#add the empty lists for each item to the two empty dicts
for i in range(len(listOfInfo)):
    postCollection[listOfInfo[i]] = []
    commentCollection[listOfInfo[i]] = []

#for each submission and comment go through and add the post and comment info
for submission in postDictionary:
    postCollection['id'].append(submission)
    for i in range(len(listOfInfo)):
        postCollection[listOfInfo[i]].append(postDictionary[submission][listOfInfo[i]])

for comment in commentDictionary:
    commentCollection['id'].append(comment)
    for i in range(len(listOfInfo)):
        commentCollection[listOfInfo[i]].append(commentDictionary[comment][listOfInfo[i]])

#now we just need to convert to a dataframe and export to CSV
postDF = pd.DataFrame.from_dict(postCollection)
commentDF = pd.DataFrame.from_dict(commentCollection)
postDF.to_csv('posts.csv')
commentDF.to_csv('comments.csv')

'''NOW AGAIN WITH PSAW
PSAW is a wrapper for the Pushshift API. It has the advantage of beng straightforward and allowing you to download huge amount of data and is not limited by Reddit's own search capabilities.
The downside is it's less customisable and the documentation is non-existant.'''

'''import the libraries'''
from psaw import PushshiftAPI
import praw
import datetime as dt
import pandas as pd

'''This allows psaw to access Reddit, you will need your own credentials for this to work'''
reddit = praw.Reddit(client_id='', #CLIENT ID, THE SHORTER ONE ON REDDIT'S API 
                     client_secret='', #SECRET ID, THE LONGER ONE ON REDDIT'S API
                     user_agent= '',#NAME OF YOUR API AGENT


'''We will set the start time and end time of our search here and convert it to a UNIX timestamp so PSAW can read it.'''
startTime = int(dt.datetime(2020,7,1).timestamp())
endTime = int(dt.datetime(2020,8,1).timestamp())
api = PushshiftAPI(reddit)


'''Now we simply pull the relevant data from PSAW'''
postGen = api.search_submissions(subreddit='coronavirus', after=startTime, before=endTime)
podtDF = pd.DataFrame([submission.__dict__ for submission in postGen])
commentGen = api.search_submissions(subreddit='coronavirus',after=startTime,before=endTime)
commentDF = pd.DataFrame([comment.__dict__ for comment in commentGen])

'''And save to CSV'''
postDF.to_csv('psawPosts.csv')
commentDF.to_csv('psawComments.csv')
