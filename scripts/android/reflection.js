Java.perform(function() {
  var Activity = Java.use('android.app.Activity');
  var Field = Java.use('java.lang.reflect.Field');
  var Method = Java.use('java.lang.reflect.Method');

  console.log(Activity.$classWrapper.__fields__.map(function(field) {
    return Java.cast(field, Field)
  }));

  console.log(Activity.$classWrapper.__methods__.map(function(method) {
    return Java.cast(method, Method)
  }));
})

