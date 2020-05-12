![LATA Framework](/docs/images/lata-title-2.png)

## Instalación

### Antes de empezar

**Java Development Kit** (JDK) permite que se pueda ejecutar y compilar código Java, ya que es indispensable ya que los dispositivos Android están basados en este lenguaje, además
de proveer herramientas como **Android Debug Bridge** (ADB) y **uiautomatorviewer** lo permitirá el desarrollo del framework, puedes descargar el JDK más adecuado al sistema
operativo de tu equipo desde la [página oficial](https://www.oracle.com/java/technologies/javase-jdk8-downloads.html) de ORACLE.

**Android Studio** provee de las herramientas para emular un dispositivo Android en caso de no contar con alguno, puedes instalarlo desde su [página oficial](https://developer.android.com/studio).

> Es importante establecer las variables de entorno de acuerdo al sistema operativo de tu equipo para el **JDK** y **Android Studio**

### Pre-requisitos

- Java Development Kit 8
    * Android Debug Bridge
- Android Studio
    * SDK Platforms
        + Instalar el API del dispositivo que se necesite, de preferencia mayor o igual a Android 7.0 (Nougat) API 24
    * SDK Tools
        + Android Emulator
        + Android SDK Platforms-Tools
        + Android SDK Tools
- Python 2.7
    * [uiautomator](https://pypi.org/project/uiautomator/)
- Dispositivo Android
    * En ajustes se debe de habilitar el [modo desarrollador](https://www.kingoapp.com/root-tutorials/how-to-enable-usb-debugging-mode-on-android.htm) para poder ejecutar los procesos desde el framework en Python
    * > El dispositivo debe de estar conectado por medio de un cable USB al equipo antes de iniciar el framework
    * Para emular un dispositivo Android
        + Abrir Android Studio
        + Tools -> AVD Manager
            - Create Virtual Device
            - Seleccionar el hardware y system image que usted prefiera y continuar
            - AVD Manager instalará los paquetes necesarios e iniciará el emulador
        + Si ya existe un dispositivo virtual, ejecutar desde línea de comando:
            - Para mostrar los dispositivos instalados:
                ``` 
                emulator -list-avds
                ``` 
            - Para iniciar el dispositivo virtual:
                ```
                emulator -avd Nombre_del_dispositivo
                ```

### Información del ambiente

- Pixel 2 - Android 9.0 Pie API 28
- Redmi Note 8 - Android 9.0 Pie API 28

## Uso

* Descargar o clonar el repositorio de GitHub.
* Editar el archivo data-test.json:
    - wifies: lista que describe la secuencia de encendido (1) y apagado (0).
    - phones: lista números telefónicos al se realizara una llamada.
    - operations: lista de operaciones a evaluar, junto con el resultado esperado. 
* El dispositivo debe de estar conectado al equipo antes de comenzar el test.
* Ejecutar en una terminal en raíz del proyecto el siguiente comando:
    ```
    $ pyhton main.py
    ```
* A continuación se mostrará en consola el resultado de los test en secuencia:
    - Se mostrará con un punto **“.”**, los test que resultaron exitosos
    - Se mostrará con una **“F”**, los test que resultaron con un error 
* Al ejecutar el test, se crea un archivo de texto de acuerdo a la versión del framework en el directorio output_test, donde podrá consultar información más detallada de la ejecución.