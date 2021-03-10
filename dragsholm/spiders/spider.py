import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import DragsholmItem
from itemloaders.processors import TakeFirst
from scrapy.http import FormRequest
import json

pattern = r'(\xa0)?'

class DragsholmSpider(scrapy.Spider):
	name = 'dragsholm'
	base_url = 'https://www.dragsholmsparekasse.dk'

	def start_requests(self):
		yield FormRequest("https://www.dragsholmsparekasse.dk/api/sdc/news/search",
			formdata={"page": "0",
					  "filterType": "categories",
			 			"filterValues": ["Bolig", "Om sparekassen", "Pension", "Forsikring", "Investering", "Selvbetjening"]},
			callback=self.parse
						)

	def parse(self, response):
		data = json.loads(response.text)
		for key in data['results']:
			url = key['url']
			full_url = self.base_url +url
			yield response.follow(full_url,self.parse_post)

		for page in range(data['totalPages']+1):
			yield FormRequest("https://www.dragsholmsparekasse.dk/api/sdc/news/search",
							  formdata={"page": str(page),
										"filterType": "categories",
										"filterValues": ["Bolig", "Om sparekassen", "Pension", "Forsikring",
														 "Investering", "Selvbetjening"]},
							  callback=self.parse
							  )

	def parse_post(self, response):
		date = response.xpath('//time/text()').get().strip()
		title = response.xpath('//h2/text()').get()
		content = response.xpath('//div[@class="text-module-b__content"]//text() | //div[@class="text-module-a frame rich-text  "]/div[@class="frame__cell"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=DragsholmItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
