import scrapy
import tutorial.items
import re

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    # headers = {
        # "Accept":"*/*",
        # "Accept-Encoding":"gzip, deflate, sdch",
        # "Accept-Language":"zh-CN,zh;q=0.8",
        # "Cache-Control":"max-age=0",
        # "Connection":"keep-alive",
        # "Host": "www.xxxxxx.com",
        # "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
    # }
    raw_url = 'http://www.csdata.org/p/issue/'
    base_url = 'http://www.csdata.org'

    def start_requests(self):
        yield scrapy.Request(url=self.raw_url, callback=self.parse,dont_filter = True)

    def parse(self, response):
        
        netware = response.selector.xpath('//div[contains(@class,"journal_div")]//a/@href').extract()
        #self.log('文章网址：%s' % netware)
        #self.log('搜索到了: %s' % len(netware))
        
        netware = ['http://www.csdata.org/p/issue/47/','http://www.csdata.org/p/issue/63/','/p/issue/71/']
        
        for i in range(2,len(netware)):
            #self.log(self.base_url + netware[i])
            s = self.base_url + netware[i]
            yield scrapy.Request(url=s, callback=self.parseChild,dont_filter = True,meta={'url':s})
        
    def parseChild(self,response):
        netware = response.selector.xpath('//div[contains(@class,"all_papers_div2")]//a/@href').extract()
        #self.log('文章网址：%s' % netware)
        #self.log('搜索到了: %s' % len(netware))

        netware = ['/p/78/']

        for i in range(len(netware)):
            #self.log(self.base_url + netware[i])
            s = self.base_url + netware[i]
            yield scrapy.Request(url=s, callback=self.parseSibling,dont_filter = True,meta={'url':s})

    def parseSibling(self, response):
        #self.log("***********************")
        articleTitle = response.selector.xpath('//header/div/h1')
        articleTitle = articleTitle.xpath('string(.)').extract()[0]
        #self.log('文章标题：%s' % articleTitle)
        articleTag = response.selector.xpath('//a[contains(@data-track-source,"subject-name")]/text()').extract()
        #self.log('文章类别：%s' % articleTag)
        ReceivedTime = response.selector.xpath('//*[@id="content"]/div/div/article/div[1]/header/div/div/div[2]/div/dl/dd[1]/time/@datetime').extract()
        #self.log('文章接收时间：%s' % ReceivedTime)
        AcceptTime = response.selector.xpath('//*[@id="content"]/div/div/article/div[1]/header/div/div/div[2]/div/dl/dd[2]/time/@datetime').extract()
        #self.log('文章接受录用时间：%s' % AcceptTime)
        PublishedTime = response.selector.xpath('//*[@id="content"]/div/div/article/div[1]/header/div/div/div[2]/div/dl/dd[3]/time/@datetime').extract()
        #self.log('文章发表时间：%s' % PublishedTime)
        ReferencesNumber = len(response.selector.xpath('//*[@id="references-content"]/div/ol/li').extract())
        #self.log('文章引用数目：%s' % ReferencesNumber)
        articleURL = response.meta['url']
        #self.log('文章地址：%s' % articleURL)
        Affiliations = response.selector.xpath('//*[@id="author-information-content"]/ol/li/h3/text()').extract()
        Authors = response.selector.xpath('//*[@id="author-information-content"]/ol/li/ul/li/span[2]/text()').extract()
        #Country = Affiliations[0].split(',')[-1]
        fileName = "test.md"
        with open(fileName, 'a',encoding='utf-8') as f:
            # f.write('文章标题：%s' % articleTitle)
            # f.write('\n')
            # f.write('文章类别：%s' % articleTag)
            # f.write('\n')
            #写文章标题
            articleTitle = re.sub(r"\n", r"", articleTitle)
            articleTitle = re.sub(r"\s+",r" ",articleTitle)
            f.write(articleTitle)
            f.write(' ; ')
            #写文章类别
            f.write('/')
            for content in articleTag:
                f.write(content)
                f.write('/')
            f.write(' ; ')
            #写文章接收时间
            if len(ReceivedTime) > 0 :
                f.write(ReceivedTime[0])
            else:
                f.write('empty')
            f.write(' ; ')
            #写文章接受录用时间
            if len(AcceptTime) > 0 :
                f.write(AcceptTime[0])
            else:
                f.write('empty')
            f.write(' ; ')
            #文章在线发表时间
            if len(PublishedTime) > 0:
                f.write(PublishedTime[0])
            else:
                f.write('empty')
            f.write(' ; ')
            #写文章引用文章数目
            f.write(str(ReferencesNumber))
            f.write(' ; ')
            #文章作者
            if len(Authors) > 0 :
                f.write('/')
                for content in Authors:
                    f.write(content)
                    f.write('/')
            else:
                f.write("empty")
            f.write(' ; ')
            #文章机构信息
            if len(Affiliations) > 0:
                affiliation = re.sub(r"\n", r"", Affiliations[0].split(',')[0])
                f.write(affiliation)
            else:
                f.write("empty")
            f.write(" ; ")
            #文章作者国家
            if len(Affiliations) > 0:
                f.write(Affiliations[0].split(',')[-1].strip())
            else:
                f.write("empty")
            f.write(' ; ')
            # 文章所在网址
            f.write(articleURL)
            #输出一个空行
            f.write('\n')
        self.log('Saved file %s' % fileName)
        