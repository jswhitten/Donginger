
import re
import twitter
from random import randrange, choice

from plugin import Plugin

class Twit(Plugin):
	def __init__(self, dong, conf):
		super(Twit, self).__init__(dong, conf)
		self.api = twitter.Api(consumer_key=self.conf['consumer_key'],consumer_secret=self.conf['consumer_secret'],access_token_key=self.conf['access_token_key'],access_token_secret=self.conf['access_token_secret'])
		self.replies = open(self.conf['shit_replies']).readlines()
		
	def remove_unicode(self, str):
		newstr = ''
		for c in str:
			if ord(c) > 127: pass
			else: newstr += c
		return newstr

	def get_followers(self):
		derp = []
		try:
			for i in self.api.GetFollowers():
				derp.append(i.screen_name)
			return ', '.join(derp)
		except: return ''
		
	def add_tag(self, callback, who, tag):
		"""Add a tag to the list used by <random tweet>."""
		
		if len(tag) > 2:
			if tag[0] == '#':
				tag = tag[1:]
			tag = tag.strip('\r')
			self.dong.db.insert('twitter_tags', {'name': tag})
			return 'Tag added.'
			
	def del_tag(self, callback, who, tag):
		"""Deletes a tag from the list used by <random tweet>."""
		
		self.dong.db.delete_by_name('twitter_tags', ('name', tag))
		return 'Tag deleted.'
		
	def add_target(self, callback, who, name):
		"""Add a twitter account to the Shitlist."""
		
		if len(name) > 2:
			if name[0] == '@':
				name = name[1:]
			self.dong.db.insert('twitter_hitlist', {'name': name})
			return 'Target added to Shitlist.'
			
	def del_target(self, callback, who, name):
		"""Removes a twitter account from the Shitlist."""
		
		dong.db.delete_by_name('twitter_hitlist', ('name', name))
		return 'Target removed from Shitlist.'
		
	def get_random_tags(self):
		num = randrange(1,4)
		tags = []
		for i in range(1, num):
			rand_tag = self.dong.db.get_random_row('twitter_tags')
			rand_tag = rand_tag[1]

			if rand_tag not in tags:
				if rand_tag[0] == '#':
					tags.append(rand_tag)
				else:
					tags.append('#' + rand_tag)
		if tags:
			return ' '.join(tags)
		else:
			return ''
		
	def random_tweet(self, callback, who, msg):
		"""Posts a tweet to a random members of the Shitlist and appends random tags."""
		
		target = self.dong.db.get_random_row('twitter_hitlist')
		target = target[1]
		tags = self.get_random_tags()
		if tags:
			msg += ' ' + tags
		return self.post_tweet_to(target, msg)
		
	def riot_tweet(self, callback, who, msg):
		"""Tweets the ouput of @riotkrrn. Only works if you're in the same room as Donginger."""
		
		riot = re.search('randtweet (.+)', callback)
		if riot:
			return self.random_tweet(callback, who, riot.group(1))
			
	def post_tweet_to(self, who, msg):
		msg = self.remove_unicode(msg)
		if msg:
			try:
				str = "@%s %s" % (who, msg)
				status = self.api.PostUpdate(str)
				return str
			except Exception,e:
				print "HTTP error: %s" % e

	def post_tweet(self, callback, who, msg):
		"""Posts a direct tweet."""
		
		msg = self.remove_unicode(msg)
		if msg:
			try:
				status = self.api.PostUpdate(msg)
			except Exception,e:
				print "HTTP 500 error: %s" % e
				
	def show_shitlist(self, callback, who, arg):
		"""Shows the full Shitlist (potential random targets of nasty tweets)"""
		
		shitlist = self.dong.db.select_all('twitter_hitlist')
		shit_names = []
		if shitlist:
			for i in shitlist:
				shit_names.append(i[1])
			return ', '.join(shit_names)
			
	def show_tags(self, callback, who, arg):
		"""Shows the full list of random tags that can be appended to random tweets"""
		
		tags = self.dong.db.select_all('twitter_tags')
		tag_names = []
		if tags:
			for i in tags:
				tag_names.append(i[1])
			return ', '.join(tag_names)
			
	def twitter_troll(self, callback, who, arg):
		"""This is a stupid command, to annoy random people on Twitter."""
		
		try:
			shit_user = self.dong.db.get_random_row('twitter_hitlist')
			shit_posts = self.api.GetSearch(term='@' + shit_user[1])
			shit_post = choice(shit_posts)
			
			spost_id = shit_post.id
			spost_user = shit_post.user
			
			reply = "@%s %s %s" % (spost_user.screen_name, choice(self.replies).strip('\n'), self.get_random_tags())
			new_status = self.api.PostUpdate(reply, in_reply_to_status_id=spost_id)
			return reply
		except Exception, e:
			print "twitter_troll: %s" % e
			
	def put_list(self, callback, who, arg):
		arg = arg.split(' ')
		if len(arg) != 3:
			print 'Bad command', arg
			return
		
		if arg[1] != 'in':
			print 'Bad command', arg, "expected 'in'"
			return
		
		twho = arg[0]
		tlist = arg[2]
		
		tl = self.api.CreateList(twho, list, 'public')
		if tl:
			return "List %s created for %s" % (tlist, twho)
		
