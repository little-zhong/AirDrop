function call_FridaActivity3() {
    Java.perform(function () {
        Java.choose("com.faceunity.app_ptag.entity.SaveAvatarParam", {
            onMatch: function (instance) {
                console.log(instance.getApiKey());
                console.log(instance.getApiSecret());
            },
            onComplete: function () {
            }
        });
    })
}