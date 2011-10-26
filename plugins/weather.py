
# Taken from skybot (https://github.com/rmmh/skybot/)

from plugin import Plugin
from lxml import etree

class Weather(Plugin):
	def __init__(self, dong, conf):
		super(Weather, self).__init__(dong, conf)
		
	def fetch_weather(self, callback, who, loc):
		"""<weather location> returns the weather for that location. Not providing a location makes it returns the weather of your last used location."""
		
		# Check if we already have that user in the DB
		table = self.dong.db.tables['weather']
		q = self.dong.db.session.query(table).filter(getattr(table.c, 'user') == who)
		
		# Fetch cached location if not provided
		if not loc:
			try:
				loc = q.all()[0][1]
			except:
				return self.__doc__
		else:
			db_loc = q.all()
			if db_loc:
				self.dong.db.update('weather', {'user': who}, {'location': loc})
			else:
				self.dong.db.insert('weather', {'user': who, 'location': loc})
		
		xml = self.get_xml('http://www.google.com/ig/api', {'weather': loc})
		return self.process_xml(xml)
		
	def process_xml(self, xml):
		if xml is None:
			return None
		
		xml = xml.find('weather')
		
		if xml.find('problem_cause') is not None:
			return None
		
		try:
			info = dict((e.tag, e.get('data')) for e in xml.find('current_conditions'))
			info['city'] = xml.find('forecast_information/city').get('data')
			info['high'] = xml.find('forecast_conditions/high').get('data')
			info['low'] = xml.find('forecast_conditions/low').get('data')
			
			output = '%(city)s: %(condition)s, %(temp_f)sF/%(temp_c)sC (H:%(high)sF'\
					', L:%(low)sF), %(humidity)s, %(wind_condition)s.' % info
		except:
			return None
		
		return output
		
		
		
		