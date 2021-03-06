# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
import datetime
from articlespider.items import JobBoleArticleItem,ArticleItemLoader
from scrapy.loader import ItemLoader

from articlespider.utils.common import get_md5

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        # 获取文章列表页中的url并交给解析函数进行具体字段的解析
        # 获取下一页URL并交给scrapy进行下载，下载完成后交给parse函数

        post_nodes =  response.css("#archive .floated-thumb .post-thumb a")

        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url,post_url), meta={"front_image_url":image_url},callback=self.parse_detail)
        # 提取下一页URL并交给scrapy下载,只爬一页就把这注释掉
        next_urls = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_urls:
            yield Request(url=parse.urljoin(response.url,next_urls), callback=self.parse)

    def parse_detail(self,response):
        article_item = JobBoleArticleItem()


        # 提取文章的具体字段
        # front_image_url = response.meta.get("front_image_url","") #文章封面图
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first("")
        # create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace("·","").strip()
        # praise_nums = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract_first("")
        # fav_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract_first("")
        # match_re = match_re = re.match(r".*?(\d+).*",fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        #
        # comment_nums = response.xpath("//a[contains(@href,'#article-comment')]/span/text()").extract()[0]
        # match_re = match_re = re.match(r".*?(\d+).*", comment_nums)
        # if match_re:
        #     comment_nums =int( match_re.group(1))
        # else:
        #     comment_nums = 0
        #
        # content = response.xpath("//div[@class='entry']").extract()[0]
        #
        # copyright = response.xpath("//div[@class='copyright-area']/a/text()").extract()[0]
        #
        # tag_list = tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)
        #
        # article_item["url_object_id"] = get_md5(response.url)
        # article_item["title"] = title
        # article_item["url"] = response.url
        # try:
        #     create_date = datetime.datetime.strptime(create_date,"%Y/%m/%d").date()
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()
        # article_item["create_date"] = create_date
        # article_item["front_image_url"] = [front_image_url]
        # article_item["praise_nums"] = praise_nums
        # article_item["comment_nums"] = comment_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["tags"] =tags
        # article_item["copyright"] = copyright
        # article_item["content"] = content


        # 通过item loader加载item
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        item_loader = ArticleItemLoader(item = JobBoleArticleItem(),response=response)
        item_loader.add_xpath("title",'//div[@class="entry-header"]/h1/text()')
        item_loader.add_xpath("create_date",'//p[@class="entry-meta-hide-on-mobile"]/text()')
        item_loader.add_value("front_image_url",[front_image_url])
        item_loader.add_xpath("praise_nums",'//span[contains(@class,"vote-post-up")]/h10/text()')
        item_loader.add_xpath("comment_nums","//a[contains(@href,'#article-comment')]/span/text()")
        item_loader.add_xpath("fav_nums",'//span[contains(@class,"bookmark-btn")]/text()')
        item_loader.add_xpath("tags","//p[@class='entry-meta-hide-on-mobile']/a/text()")
        item_loader.add_xpath("copyright","//div[@class='copyright-area']/a/text()")
        item_loader.add_xpath("content","//div[@class='entry']")
        item_loader.add_value("url",response.url)
        item_loader.add_value("url_object_id",get_md5(response.url))

        article_item = item_loader.load_item()
        yield article_item
