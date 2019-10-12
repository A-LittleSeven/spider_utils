## 淘宝爬虫

- 非headless

主要实现功能：淘宝selenium登录

```python
self.options  = Options()
# self.chrome_options.add_argument('--headless')
self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
self.brow = webdriver.Chrome(chrome_options = self.options)
```

给selenium加上参数改变浏览器的特征

windows使用chromedriver.exe, linux使用chromedriver代替自己的driver

- headless

headless模式下，会检测更多的特征因此需要修改一部分浏览器特征避免被淘宝的反爬虫机制检测：

```python
self.brow.get(self.lgnLink)
# wait for js to Exec
time.sleep(10)
# inject
self.brow.execute_script(open("./myFunc.js").read())
```

使用selenium执行代码替换一些参数改变浏览器特征



