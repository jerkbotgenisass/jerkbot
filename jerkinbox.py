#!/usr/bin/python
import praw
import re
import random

def main():
    comment_replies = read_file('comment_replies.txt')
    new_comments = []

    reddit = praw.Reddit('jerkbot')
    inbox = reddit.inbox

    for reply in inbox.comment_replies(limit=10):
        if reply.id not in comment_replies and ('be better' in reply.body.lower() or 'bad bot' in reply.body.lower()):
            if 'be better' in reply.body.lower():
                clap_back = generate_reply('better')
            if 'bad bot' in reply.body.lower():
                clap_back = generate_reply('bad')

            reply.reply(clap_back)
            # print(reply.body + ' ' + reply.id + '\n\n' + clap_back + '\n\n')

            new_comments.append(reply.id)

    with open('comment_replies.txt', 'a') as f:
        for c in new_comments:
            f.write(c + '\n')

def generate_reply(better):
    better_replies = [
        'no you',
        'bE bEtTeR',
        'I take no advice from smol people.',
        'How much ya banch?',
        'Do you even lift?',
        'Ah don\'t hate me cause I\'m beautiful. Maybe if you got rid of that old yee-yee ass haircut, you\'d get some bitches on yo dick.' 
    ]

    bad_replies = [
        'bAd BoT',
        'I don\'t give a shit what you circle jerking fucks think honestly.',
        'Go back to your crossfit box.',
        'What\'s your total?',
        'Human bad!',
        'Don\'t talk to me you bag of meat.'
    ]

    return random.choice(better_replies) if better == 'better' else random.choice(bad_replies)

def read_file(file):
    with open(file, "r") as f:
        array = f.read()
        array = array.split("\n")
        array = list(filter(None, array))

    return array

main()