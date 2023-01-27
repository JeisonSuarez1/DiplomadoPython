# En este script se ecuentra un sensor de temperatura y humedad DHT11, y un sensor de movimiento PIR que tendran
#como funcion detectar la temperatura y humedad de un centro de redes y enviar una alerta cuando salga del rango
#establecido. Estas alertas seran a través del un led en el prototipo que cambia de color dependiendo la temperatura
#ambiente, sera de color azul si la temperatura es menor a 17 grados centigrados, de color verde si se encuentra 
#entre 17 grados a 27 grados centigrados y de color rojo si es superior a 27 grados centigrados. 
#Adicionalmente se enviaran alertas remotas a través de un correo electronico y de la app de IFTTT.

#A través del sensor de movimiento se controlará el encendido y apagado de las luminarias del cuarto de redes.

#La informacion recolectada sera enviada a la API Thingspeak para llevar un seguimiento y visualizar en tiempo real
#los datos recolectados.

#----------------------------------IMPORTAR MODULOS----------------------------------

from machine import Pin
import network, time, urequests, dht

#----------------------------  PINES USADOS Y CREACIÓN DE OBJETOS  -----------------

#Pines usados para el sensor de movimiento PIR y el relay que prende las luminarias.
sensor_PIR = Pin(23, Pin.IN, Pin.PULL_UP)
relay= Pin(21,Pin.OUT)

#Pines usados para el sensor de temperatura DHT11 y el led de alerta
sensor_DHT22= dht.DHT11 (Pin(15))   # el DHT22 es para simulación en Wokwi
#sensor_DHT11= dht.DHT11 (Pin(15))   # el DHT11 es para pracitica en la protoboard
led_rojo = Pin(2,Pin.OUT)
led_verde = Pin(4,Pin.OUT)
led_azul = Pin(18,Pin.OUT)

#------------------------------ REALIZAR CONEXION A INTERNET ---------------------------


#funcion definida para realizar la conexión a internet
def conectaWifi (red, password): 
      global miRed 
      miRed = network.WLAN(network.STA_IF)      
      if not miRed.isconnected():              #Si no está conectado… 
          miRed.active(True)                   #activa la interface 
          miRed.connect(red, password)         #Intenta conectar con la red 
          print('Conectando a la red', red +"…") 
          timeout = time.time () 
          while not miRed.isconnected():           #Mientras no se conecte.. 
              if (time.ticks_diff (time.time (), timeout) > 10): 
                  return False 
      return True 


#-------------------INICIAR EL LA TOMA DE DATOS CON TODOS LOS VALORES EN 0---------------

sensor_PIR.value(0)
relay.value(0)
led_rojo.value(0)
led_verde.value(0)
led_azul.value(0)

#-------------CONDICIONAL IF PARA CONECTARSE A LA RED WIFI Y EJECUTAR EL PROGRAMA---------

if conectaWifi ("Wokwi-GUEST",""):
 
    print ("Conexión exitosa!") 
    print('Datos de la red (IP/netmask/gw/DNS):', miRed.ifconfig()) 

#-----------------URLS DEL DASHBOARD DE THINGSPEAK Y DE IFTTT PARA ENVIAR LAS ALERTAS------------------

    url_thingspeak = "https://api.thingspeak.com/update?api_key=M0CTAYSGB7NG77CK&field1=0"   
    url_gmail = "https://maker.ifttt.com/trigger/sensor_de_temperatura/with/key/bTaF-lab4QBjVYFmAsFtPl?"


#------------------- ACTIVACIÓN DEL SENSOR DE TEMPERATURA Y HUMEDAD -------------

    while True:

        #el sensor DHT11 físico que estoy usando presenta la condicion que necesita que se ejecute el programa 2 veces seguidas para
        #ser detectado adecuadamente ya que la primera vez genera error, por lo cual se agrega este try para ejecutar 2 veces el .measure()

        try:
            sensor_DHT11.measure()
        except:
            sensor_DHT11.measure()
            temperatura=sensor_DHT11.temperature()
            humedad=sensor_DHT11.humidity()
            estado_sensor_PIR = sensor_PIR.value()

            #prende el led azul si la temperatura es menor a 18 grados centigrados 
            if temperatura < 18:
                print(f"{temperatura}°C Temperatura muy baja, peligro de condensación")
                led_rojo.value(0)
                led_verde.value(0)
                led_azul.value(255)
            #prende el led verde si la temperatura esta entre 18 y 27 grados centigrados
            
            elif temperatura < 27:
                print(f"{temperatura}°C Temperatura adecuada ")
                led_rojo.value(0)
                led_verde.value(255)
                led_azul.value(0)
            #prende el led rojo si la temperatura es superior a 27 grados centigrados
            
            else:
                print(f"{temperatura}°C Temperatura muy alta, bajar temperatura")
                led_rojo.value(255)
                led_verde.value(0)
                led_azul.value(0)
                respuesta1 = urequests.get(url_gmail+"&value1="+str(temperatura)+"&value2="+str(humedad)+"&value3="+str(estado_sensor_PIR)) 
                #url para enviar la alerta en caso de que la temperatura sea demaciado alta.
                respuesta1.close ()
                time.sleep(30) # para no llenar de alertas al usuario se deja un sleep en esta linea, y generar una espera para el 
                                #envio entre notificaciones.

            if humedad < 25:
                print(f"{humedad}°C Humedad muy baja")
            elif humedad < 80:
                print(f"{humedad}°C Humedad adecuada")
            else:
                print(f"{humedad}°C Humedad muy alta")
            print("")
            time.sleep(1)

#------------------------ ACTIVACIÓN DEL SENSOR DE MOVIMIENTO -------------------------

            if estado_sensor_PIR == (0):
                print("No hay movimiento")
                relay.on()
                time.sleep(1)
            else:
                print("Hay movimiento")
                relay.off()
                time.sleep(1)


#----------------------- ENVIO DE INFORMACIÓN A THINGSPEAK -----------------------

            respuesta = urequests.get(url_thingspeak+"&field1="+str(temperatura)+"&field2="+str(humedad)+"&field3="+str(estado_sensor_PIR)) 
            respuesta.close ()

#------------------------SI NO SE LOGRA LA CONEXIÓN A WIFI--------------------------
            
else: 
       print ("Imposible conectar") 
       miRed.active (False)
