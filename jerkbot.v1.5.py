#!/usr/bin/python
import datetime
import time

import praw
import random
import re
import jerkinbox
import archive

from prawcore.exceptions import NotFound
from praw.models import MoreComments
from requests.exceptions import HTTPError

reddit = praw.Reddit('jerkbot')
subreddit = reddit.subreddit('fitnesscirclejerk')

def main():
    for submission in subreddit.new(limit=5):
        if skip(submission):
            continue

        if hasattr(submission, 'crosspost_parent'):
            submission.reply('Nice crosspost you ' + generate_insult() + '.')

            with open('jerks.txt', 'a') as f:
                f.write(submission.id + ',null\n')

            continue
        
        # print('submission: ' + submission.id)
        jerk = get_jerk(submission)
        comments = get_comments(jerk)
        archive_url = archive_jerk(jerk, comments)
        prev_jerks = get_prev_jerks(jerk)

        post_reply(submission, jerk.author.name, archive_url, prev_jerks)

        new_jerk = submission.id + ',' + jerk.author.name
        with open('jerks.txt', 'a') as f:
            f.write(new_jerk + '\n')        

def read_file(file):
    with open(file, 'r') as f:
        array = f.read()
        array = array.split('\n')
        array = list(filter(None, array))

    return array

# skip submission if URL has one of the keywords or is a self-post
def is_jerk(submission):
    skip_str = [
        '/user/',
        'imgur',
        'i.redd',
        'v.redd',
        'jpg',
        'jpeg',
        'gif',
        'png',
        'mp4',
        'youtu.be',
        'youtube.com',
        'imgflip'
    ]

    for s in skip_str:
        if s in submission.url:
            return False
    
    if submission.is_self:
        return False

    return True

# check if submission has been processed already
def jerked(submission):
    jerks = read_file('jerks.txt')

    if any(submission.id in s for s in jerks):
        return True

    return False

# check if submitted jerk is deleted
def is_deleted(submission):
    jerk = get_jerk(submission)

    if hasattr(jerk, 'selftext'):
        if jerk.selftext == '[removed]' or jerk.selftext == '[deleted]':
            return True
    else:
        if jerk.body == '[removed]' or jerk.body == '[deleted]':
            return True

    return False

# skip submission if it doesn't meet reqs
def skip(submission):
    if jerked(submission):
        return True
    if hasattr(submission, 'crosspost_parent'):
        return False
    if not is_jerk(submission):
        return True    
    if is_deleted(submission):
        return True

    return False

# check if submission is a post or a comment
def get_jerk(submission):
    try:
        jerk = reddit.comment(url=submission.url)
    except:
        jerk = reddit.submission(url=submission.url)

    return jerk

def get_comments(jerk):
    comments = []
    if hasattr(jerk, 'url'):
        jerk.comments.replace_more()

        for top_level_comment in jerk.comments[:10]:
            comments.append(top_level_comment)
    else:
        refresh_counter = 0
        ancestor = jerk
        while not ancestor.is_root and refresh_counter < 3:
            ancestor = ancestor.parent()
            if refresh_counter % 9 == 0:
                ancestor.refresh()
            refresh_counter += 1
        ancestor.replies.replace_more()
        comments.append(ancestor)

    return comments

def archive_jerk(jerk, comments):
    archive_basedir = '/var/www/html/jerkbot.icu/public_html/repo'
    archive_output = "{basedir}/{post_id}.html".format(basedir=archive_basedir, post_id=jerk.id)
    archive_url = ''
 
    try:
        the_post = jerk if hasattr(jerk, 'selftext') else jerk.submission
        with open(archive_output, 'w', encoding='UTF-8') as html_file:
            try:
                archive.parse_post(jerk.id, html_file, the_post, comments)
                archive_url = 'https://jerkbot.icu/repo/' + jerk.id
            except NotFound:
                print('User not found with Reddit API.  Most likely deleted.')
    except HTTPError:
        print('Unable to Archive Post: Invalid PostID or Log In Required (see line 157 of script)')

    return archive_url

def get_prev_jerks(jerk):
    op_insults = read_file('op_insults.txt')
    jerks = read_file('jerks.txt')
    prev_jerks = []

    for row in jerks:
        if jerk.author.name in row:
            row = row.split(',')
            post_id = row[0]
            prev_jerks.append(post_id)

    prev_jerks_n = len(prev_jerks)

    if prev_jerks_n > 0:
        plural = 'time' if prev_jerks_n == 1 else 'times'
        prev_jerks_message = '\n\nThis ' + random.choice(op_insults) + ' has been jerked ' +  str(prev_jerks_n) + ' ' + plural + ':\n\n'
        
        for link in prev_jerks:
            link = 'https://redd.it/' + link 
            prev_jerks_message += '* ' + link + '\n\n'
    else:
        prev_jerks_message = ''

    return prev_jerks_message

def post_reply(submission, op, archive_url, prev_jerks):
    message = 'Nice archive you ' + generate_insult() + '. Fortunately, I\'m not as worthless as you are.\n\n'

    if submission.author.name == 'pendlayrose':
        message = 'Long live duckie! Accept this archive, supreme overlord.\n\n'
    
    if not archive_url:
        message = 'Nice archive you ' + generate_insult() + '. Unfortunately, I can\'t archive this shit either, so I am as worthless as you are.'

        if submission.author.name == 'pendlayrose':
            message = 'Forgive me, overlord, I can not archive this jerk.'
        
        submission.reply(message)
    else:
        submission.reply(message
        + 'op: ' + op + '\n\n'
        + 'archive: ' + archive_url + '\n\n***' + prev_jerks)

def generate_insult():
    list_a = []
    list_b = []

    with open("insults.csv", "r") as f:
        for line in f:
            words = line.split(",")
            list_a.append(words[0])
            if words[1]:
                list_b.append(words[1])

    word1 = random.choice(list_a)
    word2 = random.choice(list_a)
    word3 = random.choice(list_b)

    if word2 == word1:
        while word2 == word1:
            word2 = random.choice(list_a)

    return word1 + ' ' + word2 + ' ' + word3.strip()

# run main
if __name__ == '__main__':
    main()