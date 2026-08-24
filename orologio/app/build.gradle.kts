plugins {
  id("com.android.application")
  id("org.jetbrains.kotlin.android")
}

android {
  namespace = "it.manlio.palestraorologio"
  compileSdk = 34

  defaultConfig {
    applicationId = "it.manlio.palestraorologio"
    minSdk = 30            // Wear OS 3, e va bene anche su telefono
    targetSdk = 34
    versionCode = 1
    versionName = "1.0"
  }

  buildTypes {
    release { isMinifyEnabled = false }
  }
  compileOptions {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
  }
  kotlinOptions { jvmTarget = "17" }
}

dependencies {
  // l'unica dipendenza: serve solo per aprire una pagina sul telefono dall'orologio
  implementation("androidx.wear:wear-remote-interactions:1.0.0")
}
