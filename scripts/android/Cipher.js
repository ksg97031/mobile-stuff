Java.perform(function() {
  var Cipher = Java.use('javax.crypto.Cipher');
  var getInstance = Cipher.getInstance.overload('java.lang.String');
  var oldImp = getInstance.implementation;

  getInstance.implementation = function(cipher) {
    console.log('cipher', cipher)
    return oldImp(cipher)
  }
})
