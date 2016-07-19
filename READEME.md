## 一.简介

基于 Tornado 的朋友圈消息聚合， twiwei 目前支持 twiter 和 Weibo。  

twiwei 一开始基于 Django， 但是出于频繁的网络 api 调用， Tornado 显然更适合。  
而且 Tornado 对 Websocket 和 Longpoll 的支持， 也为今后可能的实时消息推送创造了可能性。  

## 二.特点

2.1 数据库
数据库用的 SQLAlchemy + PostgreSQL，以后可能会切换到 momoko (异步的数据库驱动)。  

2.2 session
session 是自己基于 redis 写的， 基于 tornadis 这个异步 redis 驱动。  
cookie 是 secure_cookie, 中只会保存用户 id， 或者为匿名用户生成的随机 id。  
用户 id 将作为 redis 中缓存的 session 数据的索引。  

2.3 网络 api 请求
为安全起见 api 调用全部在服务器进行， 以免泄露 token。  
对外发出的 api 请求都是基于 AsyncHttpClient。
或者更准确点， CurlAsyncHTTPClient， 以方便 socks5 代理。  
但是所有 api 请求都是异步的， 所以不用担心阻塞。  
twitter 的 oauth 接口还是第一代的， 所以使用了 requests_oauth 这个库来生成 `Authorization` 头。  
socks5 代理需要 libcurl + c-ares 异步 DNS 解析 + pycurl。  

2.4 前端
前端还是 Jquery + Bootstrap。  

## 三. 跟进

3.1 Session 和 Cookie 管理  
3.2 加入更多的操作： 喜欢>转发>评论>查看作者详情  
3.3 momoko 异步数据库  
3.4 前端主题美化  
