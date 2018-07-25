# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi
import codecs
import json
import MySQLdb
import MySQLdb.cursors

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

class JsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('article.json','w',encoding="utf-8")
    def process_item(self,item,spider):
        lines = json.dumps(dict(item),ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item
    def spider_closed(self):
        self.file.close()

class MysqlPipeline(object):
    # 采用同步机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect('192.168.44.130','root','root','article_spider',charset="utf8",use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self,item,spider):
        insert_sql = """
            insert into jobbole_article(title,create_date,url,url_object_id,front_image_url,praise_nums,fav_nums,comment_nums,copyright,tags,content)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql,(item["title"],item["create_date"],item["url"],item["url_object_id"],item["front_image_url"],item["praise_nums"],item["fav_nums"],item["comment_nums"],item["copyright"],item["tags"],item["content"]))
        self.conn.commit()


class MysqlTwistedPipeline(object):
    def __init__(self,dbpool):
        self.dbpool = dbpool
    @classmethod
    def from_settings(cls,settings):
        dbparms = dict(
        host = settings["MYSQL_HOST"],
        db = settings["MYSQL_DBNAME"],
        user = settings["MYSQL_USER"],
        passwd = settings["MYSQL_PASSWORD"],
        charset = 'utf8',
        cursorclass = MySQLdb.cursors.DictCursor,
        use_unicode = True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparms)
        return cls(dbpool)

    def process_item(self,item,spider):
        #  使用Twitsed将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error)

    def handle_error(self,failure):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self,cursor,item):
#         执行具体的插入
        insert_sql = """
                            insert into jobbole_article(title,create_date,url,url_object_id,front_image_url,praise_nums,fav_nums,comment_nums,copyright,tags,content)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """
        cursor.execute(insert_sql, (
        item["title"], item["create_date"], item["url"], item["url_object_id"], item["front_image_url"], item["praise_nums"],
        item["fav_nums"], item["comment_nums"], item["copyright"], item["tags"], item["content"]))


class JsonExporterPipeline(object):
    # 调用scrapy提供的json export 导出json文件
    def __init__(self):
        self.file = open('articleexporter.json','wb')
        self.exporter = JsonItemExporter(self.file,encoding = "utf-8",ensure_ascii=False)
        self.exporter.start_exporting()
    def close_spider(self):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self,item,spider):
        self.exporter.export_item(item)
        return item

class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok,value in results:
                image_file_path = value["path"]

            item["front_image_path"] = image_file_path

        return item


