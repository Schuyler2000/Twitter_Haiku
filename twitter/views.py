from django.shortcuts import render
from django.http import HttpResponse
# from dotenv.main import dotenv_values
import tweepy
import random
from pysyllables import get_syllable_count
import re
import asyncio
import language_tool_python
tool = language_tool_python.LanguageTool('en-US')

acc_token = "REDACTED"
acc_token_secret = "REDACTED"
consumer_api_key = "REDACTED"
consumer_api_key_secret = "REDACTED"

auth = tweepy.OAuthHandler(consumer_api_key, consumer_api_key_secret)
auth.set_access_token(acc_token, acc_token_secret)
api = tweepy.API(auth)

list_of_user_IDs = ["alpha_convert",
                    "MobyDickatSea", 
                    "KDTrey5", 
                    "nytimes",
                    "BarackObama",
                    "DalaiLama",
                    "marwilliamson",
                    "thepublicdomain",
                    "DannyDeVito",
                    "AndrewYang",
                    "TheEconomist",
                    "Pontifex",
                    "OverheardAtWes",
                    "samuelbbeckett",
                    "billburr",
                    "GSElevator",
                    "Shakespeare",
                    "ChipotleTweets",
                    "mroth78",
                    "Snowden",
                    "PlatoQuote",
                    "marekgibney",
                    "funnyhumour",
                    "pattonoswalt",
                    "BorisJohnson",
                    "GovChristie",
                    "POTUS",
                    "BukayoSaka87",
                    "rexparker",
                    "GreatestQuotes",
                    "HeaneyDaily",
                    "BillGates",
                    "E_Dickinson",
                    "EE_Cummings",
                    "Daily_Bible",
                    "JewishTweets",
                    "SHAQ",
                    "divacupzone"
                    ]
        
def count_syllables_from_string(t):
    """
    counts syllables in a string of words
    """
    count = 0
    list_t = t.split()
    list_new_t = list(map(lambda i: (re.sub('[^a-zA-Z0-9]', "", i)), list_t))
    for w in list_new_t:
        if get_syllable_count(w) == None:
            count += 100
        else:
            count += get_syllable_count(w)
    return count

def syllable_count_found(t, n):

    """"
    checks to see if there is a sub array with n amount of syllables and stops when found
    """

    total_syllables = count_syllables_from_string(t)
    list_origin_t = t.split()
    list_new_t = list_origin_t

    if total_syllables < n:
        return False
    for i in range(len(list_new_t) - 1):
        for j in range(i + 1, len(list_new_t)):
            slice_i_j = count_syllables_from_string(" ".join(list_new_t[i:j]))
            if slice_i_j == n:
                return True
            if slice_i_j > n: 
                break
    return False


def shorten_to_n_syllables(t, n, length_of_last_word):
    """
    finds all the substrings of t where each substring is exactly n syllables and the final word has at least 
    length_of_last_word letters
    """
    curr = count_syllables_from_string(t)
    list_origin_t = t.split()
    list_new_t = list_origin_t

    if curr < n:
        raise Exception('There should be at least curr amount of syllables')

    ideal_subarrays = []
    possible_subarrays = []
    
    for i in range(len(list_new_t) - 1):
        for j in range(i + 1, len(list_new_t)):
            slice_i_j = count_syllables_from_string(" ".join(list_new_t[i:j]))
            if slice_i_j == n:
                possible_subarrays.append((i,j))
                if len(list_new_t[j - 1]) >= length_of_last_word:
                    ideal_subarrays.append((i,j))
            if slice_i_j > n: 
                break

    if possible_subarrays == []:
        raise Exception('There are no subarrays with correct # of syllables')
    
    if len(ideal_subarrays) > 0:
        rand_slice_ij = random.randint(0, len(ideal_subarrays) - 1)
        (i,j) = ideal_subarrays[rand_slice_ij]
        return (" ".join(list_origin_t[:i]), " ".join(list_origin_t[i:j]), " ".join(list_origin_t[j:]))
    
    else:
        rand_slice_ij = random.randint(0, len(possible_subarrays) - 1)
        (i,j) = possible_subarrays[rand_slice_ij]
        return (" ".join(list_origin_t[:i]), " ".join(list_origin_t[i:j]), " ".join(list_origin_t[j:]))

async def find_tweets(userid, syllables_n):
    """
    finds a random tweet from a user
    """

    num_of_tweets = 50

    auth = tweepy.OAuthHandler(consumer_api_key, consumer_api_key_secret)
    auth.set_access_token(acc_token, acc_token_secret)
    api = tweepy.API(auth)
    

    loop = asyncio.get_running_loop()
    def get_tweets(userid, num_of_tweets):
        return api.user_timeline(screen_name=userid, count=num_of_tweets, include_rts=False, tweet_mode="extended")

    tweets = await loop.run_in_executor(None, get_tweets, userid, num_of_tweets)
    tweetList = []
    for tweet in tweets:
        if syllable_count_found(tweet.full_text, syllables_n):
            tweetList.append(tweet.full_text)
    random.shuffle(tweetList)
    if len(tweetList)>10:
         return tweetList[:10]
    return tweetList

### VIEWS ###
def makeHaiku(listOfTweets1, listOfTweets2, listOfTweets3):
    tweet_index = random.randint(0, len(listOfTweets1) - 1)
    haiku_1 = shorten_to_n_syllables(listOfTweets1[tweet_index], 5, 1)
    is_bad_rule = lambda rule: (rule.category == 'SEMANTICS') or (rule.category == 'GRAMMAR')

    curr=(50,[])
    for t in listOfTweets2:
        t_new = shorten_to_n_syllables(t, 7, 1)
        text = haiku_1[1] + t_new[1]
        matches = tool.check(text)
        matches = [rule for rule in matches if is_bad_rule(rule)]
        if len(matches) < curr[0]:
            curr = (len(matches), t_new)
    haiku_2 = curr[1]
    
    curr=(50,[])
    for t in listOfTweets3:
        t_new = shorten_to_n_syllables(t, 5, 4)
        text = haiku_1[1] + haiku_2[1] + t_new[1]
        matches = tool.check(text)
        matches = [rule for rule in matches if is_bad_rule(rule)]
        if len(matches) < curr[0]:
            curr = (len(matches), t_new)
    haiku_3 = curr[1]
    return(haiku_1, haiku_2, haiku_3)

async def index(request):
    unique_random_ids = []
    while len(unique_random_ids) < 3:
        add = random.randint(0, (len(list_of_user_IDs) - 1))
        user_id = list_of_user_IDs[add]
        try:
            u=api.get_user(screen_name=user_id)
            if user_id in unique_random_ids:
                continue
            else:
                unique_random_ids.append(user_id)
        except Exception:
            pass 

    User_id1 = unique_random_ids[0]
    User_id2 = unique_random_ids[1]  
    User_id3 = unique_random_ids[2]

    tweets_text_1_handler = find_tweets(User_id1, 5)
    tweets_text_2_handler = find_tweets(User_id2, 7)
    tweets_text_3_handler = find_tweets(User_id3, 5)

    (listOfTweets1, listOfTweets2, listOfTweets3) = await asyncio.gather(
        tweets_text_1_handler, tweets_text_2_handler, tweets_text_3_handler
    )
    
    (haiku_1, haiku_2, haiku_3) = makeHaiku(listOfTweets1, listOfTweets2, listOfTweets3)

    ans = {
        "id1": User_id1,
        "id2": User_id2,
        "id3": User_id3,
        "haiku1": haiku_1[1],
        "haiku2": haiku_2[1],
        "haiku3": haiku_3[1],
        "tweet_1_A": haiku_1[0],
        "tweet_1_B": haiku_1[1],
        "tweet_1_C": haiku_1[2],
        "tweet_2_A": haiku_2[0],
        "tweet_2_B": haiku_2[1],
        "tweet_2_C": haiku_2[2],
        "tweet_3_A": haiku_3[0],
        "tweet_3_B": haiku_3[1],
        "tweet_3_C": haiku_3[2],
    }
    return render(request, 'style.html', ans)
    
# poetry run manage.py runserver