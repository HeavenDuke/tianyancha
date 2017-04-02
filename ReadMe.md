# TianYanCha_Spider
一个爬取[天眼查](http://www.tianyancha.com)的企业信息的爬虫，遍历机制是根据企业名称进行搜索，企业名称保存在`name_list.txt`中，来自[黄页88](http://www.huangye88.com/)，其爬虫代码见[Yellow_Page](https://github.com/Range0122/yellow_page)。
## Scrapy + Selenium + Phantomjs
由于目标网页中需要抓取的数据采用了JS渲染，通过普通的request无法抓到，所以使用了`selenium` + `phantomjs`  
目前只是做了在搜索了企业名称之后对于展示了企业详细信息的网站的url的获取，后续将更新抓取详细信息的代码。
## 更新
### 17.03.20
* 因为浏览器环境对内存和CPU的消耗都非常严重，模拟浏览器环境的爬虫代码要尽可能避免，相比之下，效率更高的方式是通过分页网页的代码，找到网页请求得到数据的url，可以通过伪装header的方式直接从源取得数据，通常是以json的格式返回数据。  
* 分析天眼查的网页，发现有几个数据包都是通过json返回回来的，非常简洁整齐，简直让爬虫垂涎三次。然后发现**cookies**里面有*_utm*、*token*、*paaptp*这三个参数每次都会变，然而根本找不出它们之间的算法，即使原模原样包装好header也获取不到json数据。  
* 在网上找了很多关于天眼查爬虫的列子，一月份的帖子url跟现在的已经有了区别，中间加了`v2`应该是更新过了反爬虫机制 ，意外还发现他们在招反爬虫工程师。

![Paste_Image.png](http://upload-images.jianshu.io/upload_images/4218178-b4795016379278ea.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
 
* 所以没办法还是先用`selenium`+`phantomjs`，虽然效率很低，但还是先把事情做成了再考虑后续优化的事情吧。  
* 天眼查访问次数稍微多一点，就会出现滑动验证码，所以还要改ip代理，不得不说这是我目前见过的反爬虫机制最强的一个网站了。
真是一场`（月薪 -1.5K VS 15K+）`的较量。  
* 遇到一个很奇怪的问题，我之前使用`Scrapy-Splash`渲染JS的时候也遇到过。就是爬取的JS的数据很不稳定，有时候能抓到JS数据，有时候又莫名其妙根本拿不到，之前我一直以为是`Slash`自身的问题，结果发现`selenium`+`phantomjs`现在也出了这种问题，并且尝试多次都莫名其妙抓不到数据了。没办法只好回过头去尝试从[国家企业信用信息公示网站](http://www.gsxt.gov.cn/index.html)，结果更强的是url中根本不包含searchword，每次搜索都有滑动验证码，虽然github上有现成的破解代码，但是成功率也不是特别理想。另外每次post都会传geetest挑战值什么的，尝试直接在打开url之后再请求，爬取结果直接返回**403 forbidden**

### 17.03.21 
* JS抓不到数据的问题，网页应该是先加载基本元素再请求JS，所以如果抓取速度太快根本来不及渲染JS就只把基本的html返回了，解决方法是在`driver.get(url)`之后`time.sleep(10)`，等待JS加载完成之后再获取html，但这样做会导致效率低一些。  
* 跑的时候每次都会出现`KeyError`，仔细查看了 `item`和`pipeline`之后并没有发现任何拼写上的问题，最初以为是`ItemLoader`的问题，然后又去读了官方文档，并没有任何错误，但是每次跑程序的时候死活都会报错。最后发现是Item里面少了括号。`Scrapy.Field()` **而不是** `Scrapy.Field`。细节出错简直 *drove me crazy*  
* 修改了MiddleWare，选用PhantomJS来解析Request，并且这个网站还有一个反爬虫的机制：因为PhantomJS这样的无界面浏览器除了程序员基本没什么人用，所以如不过进行`User-Agent`伪装的话，网站就会返回一个随机的错误的数据回来。  
* 接下来就是上Tor改IP代理，天眼查对IP的数据流量还是比较敏感的，稍不注意就直接上验证码封IP，实在是不想搞geetest验证码。然后就是继续补充完相应的数据条目，整体来看还是比较复杂的，部分数据的翻页也是很棘手的一个事情。

### 17.03.22
* 在网上看到有的大牛说，爬虫运行次数多了之后内存占用增多，原因是PhantomJS的进程没有随着爬虫的关闭一起关闭，需要`driver.quit()`，所以早上添加了相关代码，并测试通过。  
* 修改了xpath上的一些问题，将网站大部分的基本信息都爬下来了，并且保存为xml的格式。

### 17.03.23
* 完善了基本信息的相关条目，目前比较严重的问题还是JS渲染失败，即使将`sleep()`的等待时间上调到10~20s还是会出现抓取不到搜索列表中的url，以及企业详情页面解析失败的情况。  
* 由于遍历的方式是通过搜索企业名称，所以下一步准备添加相关的日志管理，保存出错的网址、企业名称。  
* 再一次让我感到摸不着头脑的是，早上十点的时候对五十个企业的基本信息进行了爬取，排除一部分搜索之后确实不存在的企业，剩下的企业在解析详细页面的时候全部出错。一直刚才十二点五十，我打印出来的html源代码跟我之前看到的结构全然不同，尽管里面关于企业的基本信息都存在，但是这样一来就要重写xpath，在尝试写了一个xpath之后，意外发现html的代码又变成了我之前看到的模样，也就是说我之前写的xpath又能够跑的通了，实在是令人费解为何返回的回来的html有时候会抽风。难道也是一种反爬虫的机制吗？  
* 最后就是因为搜索页面中企业的url也需要从JS的数据中来获取，所以不得不多使用一次`selenium`+`phantomjs`这实在是太低效了。  
* 最新出现的问题：写了个测试，如果搜索页面为空，打印出来，我一点开看，确实为空，然后我手动输入相同的搜索内容，搜索结果存在。  
* 下午没有中午的那种搜索页面出问题的情况，就是手动输入内容搜索和程序搜索的结果不同，程序搜索的企业列表为空，应该是网站自己那边抽风了，或者说也可能是采取了相应的反爬虫措施。  
* 截至目前，已经完成了基本信息的爬取，下一步将会对日志系统进行完善，以及程序中关于正则表达式处的修正，接着就是整个企业背景的信息了，加油！

### 17.03.24
* 从搜索结果页面抓取企业详细信息的url采用了正则表达式，所以新增了列表的去重。  
* 在`middleware`中添加了一些超时机制。另外还添加了使用ip代理的代码，还未启用，由于在网上抓取到的所谓高匿代理很不稳定，并且需要定期更新，所以下一步的打算是学习一下tor，或者直接去买一些ip建立可用的ip池并进行模块化管理。  
* 新增了关于主要人员的一些信息的爬取。  
* 对面网页又开始抽风搜索不到数据，考虑是否将获得搜索页面的方式从简单的url拼凑改成模拟用户输入内容、然后点击搜索按钮,也就是将获取url这个部分分割出来单独做成一个爬虫，这样一来`tyc_spider`的任务就是直接从文件中读取url然后进行详细信息的爬取，减少了对于搜索等页面判断的任务。

### 17.03.25
* 新增`search.py`，从指定文件中读取企业名称，然后在天眼查首页模拟用户输入点击进行搜索，将所有获取到的企业url去重，并且保存。  
* 重写了`tyc_spider`，现在爬虫将直接从指定文件中读取企业的url，然后获取相关的数据，并保存为xml格式。  
* 最后，一个头疼的问题，网页回返回两种可能结构的html，所以需要配置不同的xpath，之前处理的方式是两种xpath写在同一句中，当时是可行的，检测到任意一种符合规则的数据都能抓取到，现在貌似... gg (那我还能说什么呢)  
* KeyError：former_name          I DONT KNOW WHY

### 17.03.26
* 根据返回的不同形式的html结构新增多个xpath，并修正了逻辑运算的语句。  
* 之前的KeyError是因为ItemLoader传过去的是空值，到目前为止第二小部分企业背景-主要人员的信息就已经抓取完成。样本见最新的data.xml

### 17.03.27
* 这实在是让人很难受。之前一直以为是反爬虫机制才导致随机返回两种不同结构的html，直到今天早上跑了两边死活抓不到股东信息，然后就把爬下来的html格式化之后仔细看，意外发现一个东西—— `wap`，瞬间就想到之前`user_agent`里面有Android的字段，很明显是因为伪装的header让对方误以为是移动端在访问，返回回来的html结构自然不同，然后验证，果然如此。  
* 从反爬虫的角度来说，大量的`user_agent`，可以模拟从PC端、移动端多方访问，但是这样一来就要对数据进行不同格式的处理，并且还会遇到有些数据在移动端根本不会返回回来的问题，比如目前正在抓取的股东信息，移动端返回回来的数据为空。  
* 如此看来，目前的策略是先注释掉`user_agent`中的移动端，只模拟PC端，先把数据尽可能地抓取下来。甚好！  
* 修复了关于item中元素判空的问题，item中元素是列表所要要用` == ['None']` 而不是 ` == 'None' `  
* 新增了注册地址、经营范围等项目的判空  
* 新增了对股东信息的抓取。（代码一次跑通~~~开心！！！）  
* 由于抓取对外投资信息的时候需要翻页，但是翻页的操作目前只能做到在`selenium.webdriver`中实现，所以就再次尝试了直接访问json页面，结果成功了，不需要经过任何的验证识别。  
* 目前的新思路是将爬虫分两类，一类爬取js无法直接获取的数据，另一类专门访问可以直接获取的json数据。真是发现了新大陆呀！希望json在爬虫访问的时候不会出现问题。

### 17.03.28
* 在`middleware`中做了相关的逻辑判断，根据传入的url来判断是否需要使用js解析，否则使用常规方式获取html（针对可以直接访问获得的json数据）。
* 在`webdriver`中添加了点击企业经营范围的“详情”以获得完整的数据。
* 再一次被user_agent坑了，选择浏览器头的时候要慎重，有些头(fire fox)根本没办法click，一使用click方法就报错。
* 大改前最后一个版本，提交以作备份。思路是：js抓取主页面之后，生成一个config文件，保存页面中各个项目的信息（是否存在，页数等），使用`request.meta`在不同函数之间传送数据。
* 因为之前误以为是反爬虫机制写了两套xpath导致代码很乱，并且有一部分数据可以直接从json获取的已经写好了用`webdriver`，所以明天把代码重构一下，然后开始下一阶段的任务。

### 17.03.29
* 重构了之前的爬取企业基本信息部分的代码。后面的代码仍然感觉越写越乱，主要是很多地方都需要进行逻辑判断或者try语句防止报错，很难做到更加简洁。
* 新增对主要人员的json格式数据抓取
* 新增对股东信息的json格式数据抓取
* 新增对对外投资的json格式数据抓取
* 对于json信息的抓取很好做，目前遇到的另一个问题是翻页的问题，还不是很明白`make_request_by_url`的原理
* **颈椎不舒服。**

### 17.03.30
* 修正了主要人员、股东信息、对外投资的逻辑错误导致的传入元素为空的问题。

### 17.04.02
* 新增对变更记录的json格式数据抓取
* 新增对企业年报的json格式数据抓取
* 新增对分支机构的json格式数据抓取
* 由于企业年报的详细信息中项目过多，并且可能需要大量的JS渲染，所以暂时决定后续单独写一个Scrapy进行爬取，目前只获取了对应年份的年报的url
* 新增对融资历史的json格式数据抓取
* 新增对核心团队的json格式数据抓取
* 新增对企业业务的json格式数据抓取