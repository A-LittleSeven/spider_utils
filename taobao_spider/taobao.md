## 淘宝爬虫

主要实现功能：淘宝selenium登录

```python
self.options  = Options()
# self.chrome_options.add_argument('--headless')
self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
self.brow = webdriver.Chrome(chrome_options = self.options)
```

给selenium加上参数

windows使用chromedriver.exe, linux使用chromedriver代替自己的driver

走流程