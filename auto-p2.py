# David Calvo Muñoz, Samuel Ignacio Limón Riesgo y Jesús Cobos Pozo
from enum import Enum
import logging
import os
import sys
import json
import subprocess
import time
from lib_mv import MV
from lib_mv import nombre_user

def init_log(valor_debug):
 # Creacion y configuracion del logger
 log = logging.getLogger('auto-p2')  
 ch = logging.StreamHandler(sys.stdout)
 formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
 ch.setFormatter(formatter)
 log.addHandler(ch)
 log.propagate = False 
 if(valor_debug):
    log.setLevel(logging.DEBUG)
 else:
    log.setLevel(logging.INFO)  
 return log 

def cargar_debug():
    json_path = os.path.join(path_inicial, 'auto-p2.json')
    with open(json_path, 'r') as archivo_json:
        configuracion = json.load(archivo_json)

    # Obtener el valor de 'debug' de la configuración
    valor_debug = configuracion.get('debug', False)
    return valor_debug

def cargar_configuracion():
    # Cargar configuración de los servidores desde el archivo JSON
    json_path = os.path.join(path_inicial, 'auto-p2.json')

    try:
        with open(json_path) as json_file:
            config = json.load(json_file)
            num_servidores = config.get('num_serv')

            if num_servidores is None or not isinstance(num_servidores, int) or num_servidores < 1 or num_servidores > 5:
                sys.exit("\033[1;31m" + "\nError: El valor de 'num_serv' en el archivo de configuración no es válido.\nTiene que ser un valor comprendido entre 1 y 5 (incluyendo el 1 y el 5).\n" + "\033[0;m")
                
            return num_servidores

    except FileNotFoundError:
        sys.exit("Error: No se encontró el archivo de configuración 'auto-p2.json'.")
    except json.JSONDecodeError:
        sys.exit("Error: El archivo de configuración 'auto-p2.json' no es un JSON válido.")
    except ValueError as e:
        sys.exit(e)	
   
def pause():
 programPause = input("Press the <ENTER> key to continue...")

def configurar_entorno(): 
    # Si no existe la carpeta con el nombre del usuario en /mnt/tmp se crea y se accede a dicha carpeta, y si ya existe simplemente se accede a ella
    os.chdir("/")
    os.chdir("/mnt/tmp")
    if not os.path.exists(nombre_user):
        os.makedirs(nombre_user)
    os.chdir(nombre_user)
          
def crear(num_servidores):
    imagen_qcow2_inicial = os.path.join(path_inicial, 'cdps-vm-base-pc1.qcow2')
    if os.path.exists(f"{path_inicial}/cdps-vm-base-pc1.qcow2"):
        logger.debug(f"La imagen se encuentra en el directorio {path_inicial}")
    else:
        sys.exit(f"Copia la imagen dentro del directorio {path_inicial}")
    if os.path.exists(f"{path_inicial}/plantilla-vm-pc1.xml"):
        logger.debug(f"La plantilla se encuentra en el directorio {path_inicial}")
    else:
        sys.exit(f"Copia la plantilla dentro del directorio {path_inicial}")
    if os.path.exists(f"{path_inicial}/auto-p2.py"):
        logger.debug(f"El script auto-p2.py se encuentra en el directorio {path_inicial}")
    else:
        sys.exit(f"El script auto-p2.py debe estar en el directorio {path_inicial}")
    if os.path.exists(f"{path_inicial}/lib_mv.py"):
        logger.debug(f"El fichero lib_mv.py se encuentra en el directorio {path_inicial}")
    else:
        sys.exit(f"El fichero lib_mv.py debe estar en el directorio {path_inicial}")
    if os.path.exists(f"{path_inicial}/auto-p2.json"):
        logger.debug(f"El fichero de configuración se encuentra en el directorio {path_inicial}\n")
    else:
        sys.exit(f"El fichero de configuración debe estar en el directorio {path_inicial}")

    c1.crear_mv(imagen_qcow2_inicial, 'if1', False, path_inicial, num_servidores )
    lb.crear_mv(imagen_qcow2_inicial, '', True, path_inicial, num_servidores )
    s1.crear_mv(imagen_qcow2_inicial, 'if2', False, path_inicial, num_servidores )
    if num_servidores >= 2:
        s2.crear_mv(imagen_qcow2_inicial, 'if2', False, path_inicial, num_servidores )    
    if num_servidores >= 3:
        s3.crear_mv(imagen_qcow2_inicial, 'if2', False, path_inicial, num_servidores )
    if num_servidores >= 4:
        s4.crear_mv(imagen_qcow2_inicial, 'if2', False, path_inicial, num_servidores )
    if num_servidores >= 5:  
        s5.crear_mv(imagen_qcow2_inicial, 'if2', False, path_inicial, num_servidores )
                                     
    subprocess.call("sudo brctl addbr LAN1", shell=True)
    subprocess.call("sudo brctl addbr LAN2", shell=True)
    subprocess.call("sudo ifconfig LAN1 up", shell=True)
    subprocess.call("sudo ifconfig LAN2 up", shell=True)
    subprocess.call("sudo ifconfig LAN1 10.11.1.3/24", shell=True)
    logger.info("LAN 1 y LAN 2 configuradas correctamente.")
    subprocess.call("sudo ip route add 10.11.0.0/16 via 10.11.1.1", shell=True)
    logger.info("Host definido correctamente.")
    subprocess.call("HOME=/mnt/tmp sudo virt-manager", shell=True) 

def arrancar(num_servidores):        
     subprocess.call("HOME=/mnt/tmp sudo virt-manager", shell=True) 
     c1.arrancar_mv()
     c1.mostrar_consola_mv()
     lb.arrancar_mv()
     lb.mostrar_consola_mv()
     s1.arrancar_mv()
     s1.mostrar_consola_mv()
     if num_servidores >= 2:
         s2.arrancar_mv()
         s2.mostrar_consola_mv() 
     if num_servidores >= 3:
        s3.arrancar_mv()
        s3.mostrar_consola_mv()
     if num_servidores >= 4:
        s4.arrancar_mv()
        s4.mostrar_consola_mv()
     if num_servidores >= 5:  
        s5.arrancar_mv()
        s5.mostrar_consola_mv()
             
def parar(num_servidores):
     c1.parar_mv()
     lb.parar_mv()
     s1.parar_mv()
     if num_servidores >= 2:
         s2.parar_mv()   
     if num_servidores >= 3:
        s3.parar_mv() 
     if num_servidores >= 4:
        s4.parar_mv() 
     if num_servidores >= 5:  
        s5.parar_mv()
              
       
def liberar(num_servidores):
     c1.liberar_mv()
     lb.liberar_mv()
     s1.liberar_mv()
     if num_servidores >= 2:
         s2.liberar_mv()  
     if num_servidores >= 3:
        s3.liberar_mv() 
     if num_servidores >= 4:
        s4.liberar_mv()
     if num_servidores >= 5:  
        s5.liberar_mv()
    
        # Eliminar los archivos hostname e interfaces
     subprocess.call(["rm", f"/mnt/tmp/{nombre_user}/hostname", "-f"])
     subprocess.call(["rm", f"/mnt/tmp/{nombre_user}/interfaces", "-f"])
     logger.debug(f"Ficheros hostname e interfaces eliminados en /mnt/tmp/{nombre_user}")
        # Eliminar index.html
     subprocess.call(["rm", f"/mnt/tmp/{nombre_user}/index.html", "-f"])
     logger.debug(f"Fichero index.html eliminado correctamente en /mnt/tmp/{nombre_user}")
        # Eliminar rc.local
     subprocess.call(["rm", f"/mnt/tmp/{nombre_user}/rc.local", "-f"])
     logger.debug(f"Fichero rc.local eliminado correctamente en /mnt/tmp/{nombre_user}")
        # Eliminar haproxy.cfg
     subprocess.call(["rm", f"/mnt/tmp/{nombre_user}/haproxy.cfg", "-f"])
     logger.debug(f"Fichero haproxy.cfg eliminado correctamente en /mnt/tmp/{nombre_user}")
        # Deshacer la configuración de LAN1
     subprocess.call("sudo ifconfig LAN1 down", shell=True)
     subprocess.call("sudo brctl delbr LAN1", shell=True)
     logger.info("LAN 1 eliminada correctamente.")
            # Deshacer la configuración de LAN2
     subprocess.call("sudo ifconfig LAN2 down", shell=True)
     subprocess.call("sudo brctl delbr LAN2", shell=True)
     logger.info("LAN 2 eliminada correctamente.")    

def ejecutar_comando_virsh(comando):
    try:
        resultado = subprocess.check_output(["sudo","virsh", comando])
        return resultado.decode("utf-8")
    except subprocess.CalledProcessError as e:
        return f"Error al ejecutar el comando '{comando}': {e}"

def ping(direccion_ip):
    try:
        resultado = subprocess.check_output(["ping", "-c", "3", direccion_ip])
        return resultado.decode("utf-8")
    except subprocess.CalledProcessError as e:
        return f"Error al hacer ping a '{direccion_ip}': {e}"
    
def monitorizar_escenario(num_servidores):
    maquinas_virtuales = ['c1', 'lb', 's1'] # Lista de nombres de máquinas virtuales a monitorizar si o si
    direcciones_ip = {                      # Direcciones IP correspondientes a las máquinas virtuales
        'c1': '10.11.1.2',
        'lb': '10.11.1.1',
        's1': '10.11.2.31',
    }
    # Agregar máquinas virtuales s2, s3, s4 y s5 si existen
    if num_servidores >= 2:
        maquinas_virtuales.append('s2')
        direcciones_ip['s2'] = '10.11.2.32'
    if num_servidores >= 3:
        maquinas_virtuales.append('s3')
        direcciones_ip['s3'] = '10.11.2.33'
    if num_servidores >= 4:
        maquinas_virtuales.append('s4')
        direcciones_ip['s4'] = '10.11.2.34'
    if num_servidores >= 5:
        maquinas_virtuales.append('s5')
        direcciones_ip['s5'] = '10.11.2.35'

    time.sleep(10)
        # Obtener el estado de las máquinas virtuales
    estado_vm = ejecutar_comando_virsh("list --all")
    print("Estado de las máquinas virtuales:")
    print(estado_vm)
        # Iterar sobre las máquinas virtuales y obtener estadísticas de CPU y realizar ping
    for vm_nombre in maquinas_virtuales:
        print(f"\nInformación detallada de la máquina virtual {vm_nombre}:\n")
        print(ejecutar_comando_virsh(f"dominfo {vm_nombre}"))
        print(f"\nResultado del ping a la máquina virtual {vm_nombre}:")
            # Obtener la dirección IP de la máquina virtual
        direccion_ip_vm = direcciones_ip.get(vm_nombre, f"IP_no_definida_para_{vm_nombre}")
        print(ping(direccion_ip_vm))
            # Obtener estadísticas de CPU para cada máquina virtual
        cpu_stats_vm = ejecutar_comando_virsh(f"cpu-stats {vm_nombre}")
        print(f"\nEstadísticas de CPU de la máquina virtual {vm_nombre}:\n")
        print(cpu_stats_vm)
        
    time.sleep(5)       

#----------------------------------FIN DE LAS FUNCIONES-----------------------------------------------------------------------

#------------------OPCIONAL: PARAR y/o ARRANCAR MVs individualmente-----------------------------------------------------------
if len(sys.argv) == 3 :                 
    orden = sys.argv[1]
    nombre = sys.argv[2]
    path_inicial = os.getcwd()   #para obtener el path inicial desde el que se ejecuta el script por primera vez
    configurar_entorno()
    num_servidores = cargar_configuracion()
    valor_debug = cargar_debug()                #carga los detalles de los comentarios
    logger=init_log(valor_debug)  
    logger.debug("logger configurado")
    
    dictionary = {
	"crear": crear,
    "arrancar" : arrancar,
    "parar": parar,
    "liberar": liberar
    
    }
    class MiEnum(Enum):
        c1 = "c1"
        lb = "lb"
        s1 = "s1"
        if num_servidores >= 2:
            s2 = "s2"
            if num_servidores >= 3:
                s3 = "s3"
                if num_servidores >= 4:
                        s4 = "s4"
                        if num_servidores >= 5:
                            s5 = "s5"
            
    if orden in dictionary:
        if nombre in MiEnum.__members__:
            if orden == "arrancar":
                nombre = MV(nombre)
                nombre.arrancar_mv()
                nombre.mostrar_consola_mv()
                
            if orden == "parar":
                nombre = MV(nombre)
                nombre.parar_mv()
                
            if orden == "liberar":
                nombre = MV(nombre)
                nombre.liberar_mv()   
                   
        else: 
            sys.exit("\033[1;31m" + "\nLa máquina para la que quieres ejecutar la orden no existe.\n" + "\033[0;m") 
    else:
        sys.exit("\033[1;31m" + "\nEjecución del script incorrecta. No existe esa orden.\n" + "\033[0;m")

    sys.exit()

#--------------------FUNCIONAMIENTO DEL SCRIPT CON SOLO DOS ARGUMENTOS-------------------------------------------------------------------

# En el caso de que NO se escriba por el terminal en el siguiente formato: python3 auto-p2.py <orden>
if len(sys.argv) != 2 :
	sys.exit("\033[1;31m" + "\nEjecución del script incorrecta. Es obligatorio el siguiente formato: \npython3 auto-p2.py <orden>\n" + "\033[0;m")
# En el caso de que SI se escriba por el terminal en el siguiente formato: python3 auto-p2.py <orden>
else:
	orden = sys.argv[1]         # El sys.argv[1] hace referencia a la <orden>
 
dictionary = {
	"crear": crear,
    "arrancar" : arrancar,
    "parar": parar,
    "liberar": liberar,
    "monitor": monitorizar_escenario
}
path_inicial = os.getcwd()    #para obtener el path inicial desde el que se ejecuta el script por primera vez
configurar_entorno()
num_servidores = cargar_configuracion()     # carga el numero de servidores utilizados
valor_debug = cargar_debug()                # carga los detalles de los comentarios
logger=init_log(valor_debug) 
logger.debug("logger configurado")
c1 = MV('c1')  
lb = MV('lb') 
s1 = MV('s1')
if num_servidores >= 2:
    s2 = MV('s2')
if num_servidores >= 3:
    s3 = MV('s3')
if num_servidores >= 4:
    s4 = MV('s4')
if num_servidores >= 5:  
    s5 = MV('s5')
if orden in dictionary:	          # En el caso de que la orden exista en el diccionario
	dictionary[orden](num_servidores)

else:                             # En el caso de que la orden NO exista en el diccionario
	sys.exit("\033[1;31m" + "\nEjecución del script incorrecta. Es obligatorio el siguiente formato:\npython3 auto-p2.py <orden>\nDonde la <orden> puede ser: crear, arrancar, parar, liberar o monitor.\n" + "\033[0;m")  
    
