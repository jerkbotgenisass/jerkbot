#!/usr/bin/python
import datetime
import time

import praw
from prawcore.exceptions import NotFound
from requests.exceptions import HTTPError



def write_header(f, posttitle):
    f.write('<!DOCTYPE html>\n<html>\n<head>\n')
    f.write('\t<meta charset="utf-8"/>\n')
    f.write('\t<link type="text/css" rel="stylesheet" href="' + path_to_css + '"/>\n')
    f.write('\t<title>' + posttitle + '</title>\n')
    f.write('</head>\n<body>\n')

def parse_post(jerk_hl, f, post_object, comments):
    write_header(f, post_object.title)
    # post_object.comments.replace_more()
    post_author_name = ''
    try:
        post_author_name = post_object.author.name
        post_author_exists = 1
    except AttributeError:
        post_author_exists = 0
    f.write('<div class="title">\n')
    if post_object.is_self:
        # The post is a self post
        f.write(post_object.title)
        f.write('\n<br/><strong>')
    else:
        # The post is a link post
        f.write('<a id="postlink" href="' + post_object.url)
        f.write('">')
        f.write(post_object.title)
        f.write('</a>\n<br/><strong>')
    if post_author_exists:
        f.write('Posted by <a id="userlink" href="https://www.reddit.com/' + post_object.author._path)
        f.write('">')
        f.write(post_author_name)
        f.write('</a>. </strong><em>')
    else:
        f.write('Posted by [Deleted]. </strong><em>')
    f.write('Posted at ')
    post_date = time.gmtime(post_object.created_utc)
    f.write(str(post_date.tm_hour) + ':')
    f.write(str(post_date.tm_min) + ' UTC on ')
    f.write(monthsList[post_date.tm_mon - 1] + ' ')
    f.write(str(post_date.tm_mday) + ', ' + str(post_date.tm_year))
    f.write('. ' + str(post_object.score))
    if post_object.is_self:
        f.write(' Points. </em><em>(self.<a id="selfLink" href="https://www.reddit.com/')
    else:
        f.write(' Points. </em><em>(<a id="selfLink" href="https://www.reddit.com/')
    f.write(post_object.subreddit._path)
    f.write('">' + post_object.subreddit.display_name)
    if post_object.is_self:
        f.write('</a>)</em><em>')
    else:
        f.write('</a> Subreddit)</em><em>')
    f.write(' (<a id="postpermalink" href="https://www.reddit.com')
    f.write(post_object.permalink)
    f.write('">Permalink</a>)</em>\n')
    if post_object.is_self and post_object.selftext_html:
        f.write('<div class="post">\n')
        f.write(post_object.selftext_html)
        f.write('</div>\n')
    elif post_object.is_self:
        f.write('<div class="post">\n')
        f.write('')
        f.write('</div>\n')
    else:
        f.write('<div class="post">\n<p>\n')
        f.write(post_object.url)
        f.write('</p>\n</div>\n')
    f.write('</div>\n')
    # for comment in post_object._comments:
    for comment in comments:
        parse_comment(jerk_hl, f, comment, post_author_name, post_author_exists)
    f.write('<hr id="footerhr">\n')
    f.write('<div id="footer"><em>Archived on ')
    f.write(str(datetime.datetime.utcnow()))
    f.write(' UTC</em></div>')
    f.write('\n\n</body>\n</html>\n')

def parse_comment(jerk_hl, f, reddit_comment, post_author_name, post_author_exists, is_root=True):
    comment_author_name = ''
    highlight = 'background-color: #f7cfc0e0;' if reddit_comment.id == jerk_hl else ''
    try:
        comment_author_name = reddit_comment.author.name
        comment_author_exists = 1
    except AttributeError:
        comment_author_exists = 0
    if is_root:
        f.write('<div id="' + str(reddit_comment.id))
        f.write('" class="comment" style="' + highlight + '">\n')
    else:
        f.write('<div id="' + str(reddit_comment.id))
        f.write('" class="comment" style="margin-bottom:10px;margin-left:0px; ' + highlight + '">\n')
    f.write('<div class="commentinfo">\n')
    if comment_author_exists:
        if post_author_exists and post_author_name == comment_author_name:
            f.write('<a href="https://www.reddit.com/' + reddit_comment.author._path)
            f.write('" class="postOP-comment">' + comment_author_name + '</a>')
        else:
            f.write('<a href="https://www.reddit.com/' + reddit_comment.author._path)
            f.write('">' + comment_author_name + '</a>')
    else:
        f.write('<strong>[Deleted]</strong>')
    f.write(' <em>')
    f.write('Posted at ')
    post_date = time.gmtime(reddit_comment.created_utc)
    f.write(str(post_date.tm_hour) + ':')
    f.write(str(post_date.tm_min) + ' UTC on ')
    f.write(monthsList[post_date.tm_mon - 1] + ' ')
    f.write(str(post_date.tm_mday) + ', ' + str(post_date.tm_year))
    f.write('<a href=https://www.reddit.com')
    f.write(reddit_comment.permalink)
    f.write("> (Permalink) </a>")
    f.write('</em></div>\n')
    if reddit_comment.body_html:
        f.write(reddit_comment.body_html)
    else:
        f.write(reddit_comment.body)
    for reply in reddit_comment.replies:
        parse_comment(jerk_hl, f, reply, post_author_name, post_author_exists, False)
    f.write('</div>\n')

r = praw.Reddit('jerkbot')
path_to_css = '/style.css'
monthsList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']