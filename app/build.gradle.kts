plugins {
    id("com.android.application")
}

android {
    namespace = "com.lifeincredit.game"
    compileSdk = 36

    defaultConfig {
        // Унікальний ID застосунку в Google Play. Після першого завантаження змінити не можна.
        applicationId = "com.lifeincredit.game"
        minSdk = 26
        targetSdk = 36
        versionCode = 10        // збільшуй на 1 перед кожним новим завантаженням у Play
        versionName = "3.3-beta"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
