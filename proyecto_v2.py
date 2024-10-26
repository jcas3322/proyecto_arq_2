import os
import termios
import sys
sys.path.insert(0, '/home/julioaguilar/arq2/arq2python/firebase_admin')
sys.path.insert(0, '/home/julioaguilar/arq2/arq2python/google')
sys.path.insert(0, '/home/julioaguilar/arq2/arq2python/cachetools')
import firebase_admin
from firebase_admin import credentials, db

# Inicializa la aplicación de Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://arq2-cffb7-default-rtdb.firebaseio.com/'
})

ref_temp = db.reference('temperatura')
ref_hum = db.reference('humedad')

# Configura el puerto serial manualmente
def config_serial(port, baudrate):
    # Abrimos el archivo de dispositivo (el puerto serial)
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)

    # Obtenemos los atributos del puerto serial
    attrs = termios.tcgetattr(fd)

    # Configuramos la velocidad (baudrate)
    baud = get_baudrate(baudrate)
    attrs[4] = baud  # Configura la velocidad de salida (ospeed)
    attrs[5] = baud  # Configura la velocidad de entrada (ispeed)

    # Configuramos el puerto en modo sin control de flujo
    attrs[2] = attrs[2] | termios.CLOCAL | termios.CREAD  # Activar receptor y setear control local
    attrs[3] = attrs[3] & ~(termios.ICANON | termios.ECHO | termios.ECHOE | termios.ISIG)  # Modo sin buffer

    # Establecemos la configuración del puerto
    termios.tcsetattr(fd, termios.TCSANOW, attrs)

    return fd

# Función para obtener el valor del baudrate correcto
def get_baudrate(baudrate):
    baudrates = {
        9600: termios.B9600,
        19200: termios.B19200,
        38400: termios.B38400,
        57600: termios.B57600,
        115200: termios.B115200
    }
    if baudrate not in baudrates:
        raise ValueError(f"Baudrate {baudrate} no soportado")
    return baudrates[baudrate]

# Función para leer y responder en el puerto serial
def read_serial(fd):
    try:
        # Leer los datos
        while True:
            try:
                data = os.read(fd, 100).decode('utf-8').strip()  # Leemos hasta 100 bytes
                if data:
                    print(f"Recibido: {data}")
                    valores = data.split('-')
                    if len(valores) == 2:
                        temperatura = float(valores[0])
                        humedad = float(valores[1])
                        print(f"Temperatura: {temperatura}, Humedad: {humedad}")
                        ref_temp.set(temperatura)
                        ref_hum.set(humedad)
                        print(f"Base de datos actualizada con exito")

                    # Enviar respuesta
                    response = "Señal recibida\n"
                    os.write(fd, response.encode('utf-8'))
            except OSError:
                pass  # No hay datos disponibles en este momento
    except KeyboardInterrupt:
        print("Saliendo...")
        os.close(fd)  # Cerrar el puerto antes de salir

# Main
if __name__ == "__main__":
    serial_port = '/dev/ttyAMA0'
    baud_rate = 9600

    try:
        # Configuramos el puerto serial
        fd = config_serial(serial_port, baud_rate)
        print(f"Escuchando en {serial_port} a {baud_rate} baudios...")
        # Empezamos a leer los datos y responder
        read_serial(fd)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
