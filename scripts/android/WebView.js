Java.perform(function () {
    var WebView = Java.use("android.webkit.WebView");
    var CookieManager = Java.use("android.webkit.CookieManager");
    var cookieManager = CookieManager.getInstance();

    WebView.loadUrl.overload("java.lang.String").implementation = function (s) {
        var cookie = cookieManager.getCookie.overload("java.lang.String").call(cookieManager, s) || '(empty)';
        console.log('url:', JSON.stringify(s.toString()));
        console.log('cookie:', JSON.stringify(cookie.toString()));
        this.loadUrl.overload("java.lang.String").call(this, s);
    };

});
