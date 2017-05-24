Java.perform(function() {
  var TelephonyManager = Java.use('android.telephony.TelephonyManager');
  var currentApplication = Java.use('android.app.ActivityThread').currentApplication();
  var context = currentApplication.getApplicationContext();
  var manager = context.getSystemService('phone');
  manager = Java.cast(manager.$handle, TelephonyManager);

  console.log('imei', manager.getDeviceId());
})

