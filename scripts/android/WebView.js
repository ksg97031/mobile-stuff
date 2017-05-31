Java.perform(function() {
  var WebView = Java.use('android.webkit.WebView');
  var CookieManager = Java.use("android.webkit.CookieManager");
  var cookieManager = CookieManager.getInstance();

  var Context = Java.use('android.content.Context');
  var WebViewClient = Java.use('android.webkit.WebViewClient');
  var client = WebViewClient.$new();

  WebViewClient.shouldOverrideUrlLoading.overload('android.webkit.WebView', 'java.lang.String').implementation = function(view, url) {
    var cookie = cookieManager.getCookie.overload("java.lang.String").call(cookieManager, s) || '(empty)';
    console.log('url:', JSON.stringify(s.toString()));
    console.log('cookie:', JSON.stringify(cookie.toString()));

    return true
  };


  WebView.loadUrl.overload("java.lang.String").implementation = function (s) {
    var cookie = cookieManager.getCookie.overload("java.lang.String").call(cookieManager, s) || '(empty)';
    console.log('url:', JSON.stringify(s.toString()));
    console.log('cookie:', JSON.stringify(cookie.toString()));

    this.setWebViewClient(client);
    return this.loadUrl.overload("java.lang.String").call(this, s);
  };

})
