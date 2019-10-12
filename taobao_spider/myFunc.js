
const setProperty = () => {
  Object.defineProperty(navigator, "languages", {
      get: () => ["zh-CN", "zh"],    
    });
  Object.defineProperty(navigator, 'language', {
      get: () => "zh-CN",
    });
  Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined,
    })
  Object.defineProperty(navigator, 'userAgent', {
      get : () => "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
    })
  Object.defineProperty(navigator, 'appVersion', {
    get : () => "5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
    })
};
setProperty();