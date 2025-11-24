#!/usr/bin/python3
import logging
from lxml import etree
import subprocess
import os 

log = logging.getLogger('auto-p2')

direccion_actual = os.getcwd()
nombre_user = "jesus.cobos"

class MV:

 def __init__(self, nombre):
    self.nombre = nombre
    log.info('init MV ' + self.nombre)

 def crear_mv (self, imagen, interfaces_red, router, path_inicial, num_servidores):

    log.debug("crear_mv " + self.nombre)
    subprocess.call(['qemu-img', 'create', '-f', 'qcow2', '-b', imagen, f'{self.nombre}.qcow2'])
    log.debug(f"Imagen de {self.nombre} ({self.nombre}.qcow2) creada con éxito.")
    subprocess.call(['cp', f'{path_inicial}/plantilla-vm-pc1.xml', f'{self.nombre}.xml'])
    if(interfaces_red == 'if1'):
       LAN= "LAN1"
    elif (interfaces_red == "if2"):  
       LAN= "LAN2"

    if (router):
        tree = etree.parse(f'{self.nombre}.xml') 		   #carga el fichero xml
        root = tree.getroot() 		               #obtenemos el nodo raíz
        estructura = etree.ElementTree(root)    	#guardamos la estructura del fichero XML

        name = root.find("name")	#buscamos la etiqueta 'name'
        name.text = self.nombre		#le cambiamos el nombre al componente referido (lb)

        devdisksource = root.find("./devices/disk/source")	      #buscamos la ruta de la imagen
        devdisksource.set("file", f'/mnt/tmp/{nombre_user}/{self.nombre}.qcow2')	#dentro de file, metemos nuestra imagen

        devintsource = root.find("./devices/interface/source") 	#buscamos la interfaz
        devintsource.set("bridge", 'LAN1')				            #en el bridge le ponemos LAN1

        etiquetadevices = root.find('devices')							                           #vamos a crear otra etiqueta dentro de devices
        etiquetainterface = etree.SubElement(etiquetadevices, 'interface', type='bridge')	   #nueva etiqueta tipo bridge

        etiquetasource = etree.SubElement(etiquetainterface, 'source', bridge = "LAN2")	#creamos las etiquetas interiores con LAN2
        etiquetamodel = etree.SubElement(etiquetainterface, 'model', type = "virtio")

        estructura.write(f"{self.nombre}.xml")
        log.debug(f"Fichero {self.nombre}.xml modificado correctamente.")	
        
    else :
        tree= etree.parse(f"{self.nombre}.xml")		#carga el fichero xml
        root=tree.getroot()			         #obtenemos el nodo raíz
        estructura = etree.ElementTree(root)	#guardamos la estructura del fichero XML

        name = root.find('name')
        name.text = self.nombre

        devdisksource = root.find("./devices/disk/source")
        devdisksource.set("file",f"/mnt/tmp/{nombre_user}/{self.nombre}.qcow2")

        devintsource = root.find("./devices/interface/source")
        devintsource.set("bridge",LAN)	      #el c1 está solo conectado a LAN1

        estructura.write(f"{self.nombre}.xml")
        log.debug(f"Fichero {self.nombre}.xml modificado correctamente.")
    subprocess.call(f"sudo virsh define {self.nombre}.xml", shell=True)      #Creamos la máquina de forma persistente
    subprocess.call(f"touch /mnt/tmp/{nombre_user}/hostname",shell =True)         #Creamos el fichero hostname en la ruta proporcionada
    subprocess.call(f"echo {self.nombre} > /mnt/tmp/{nombre_user}/hostname",shell =True)      #Escribe self en hostname
    log.info(f"Fichero hostname actualizado con éxito en /mnt/tmp/{nombre_user}")
    subprocess.call(f"sudo virt-copy-in -a {self.nombre}.qcow2 /mnt/tmp/{nombre_user}/hostname /etc",shell =True)  #Copiamos el fichero de hostname en /etc sobreescribiéndolo
    log.debug(f"Fichero hostname actualizado con éxito para {self.nombre} en /etc")
    subprocess.call(f"touch /mnt/tmp/{nombre_user}/interfaces",shell =True)   #Creamos el fichero interfaces
    intr = open(f'/mnt/tmp/{nombre_user}/interfaces',"w")

    # Para la configuracion del fichero  interfaces
    direcciones_ip = {
    'c1': {'address': '10.11.1.2', 'gateway': '10.11.1.1'},
    's1': {'address': '10.11.2.31', 'gateway': '10.11.2.1'},
    's2': {'address': '10.11.2.32', 'gateway': '10.11.2.1'},
    's3': {'address': '10.11.2.33', 'gateway': '10.11.2.1'},
    's4': {'address': '10.11.2.34', 'gateway': '10.11.2.1'},
    's5': {'address': '10.11.2.35', 'gateway': '10.11.2.1'},
    'lb': {'eth0': {'address': '10.11.1.1', 'gateway': '10.11.2.1'},
           'eth1': {'address': '10.11.2.1', 'gateway': '10.11.1.1'}}
    }

    if self.nombre in direcciones_ip:
         config = direcciones_ip[self.nombre]
    
         if self.nombre == 'lb':
         # Configuración específica para lb
            intr.write(f"auto lo\niface lo inet loopback\n\nauto eth0\niface eth0 inet static\naddress {config['eth0']['address']}\nnetmask 255.255.255.0\ngateway {config['eth0']['gateway']}\n\nauto eth1\niface eth1 inet static\naddress {config['eth1']['address']}\nnetmask 255.255.255.0\ngateway {config['eth1']['gateway']}\n")
            log.info(f"Fichero interfaces actualizado con éxito en /mnt/tmp/{nombre_user}")

         # --------OPCIONAL: CONFIGURACIÓN DEL HAPROXY para el lb---------------------------------------------------------------------------
            subprocess.call(f"touch /mnt/tmp/{nombre_user}/rc.local", shell = True)
            log.info(f"Fichero rc.local creado con éxito en /mnt/tmp/{nombre_user}")
            subprocess.call(f"chmod +x /mnt/tmp/{nombre_user}/rc.local", shell = True)
            intr2 = open(f'/mnt/tmp/{nombre_user}/rc.local',"w")
            intr2.write("#!/bin/bash \nsudo service haproxy start\nexit 0\n")
            intr2.close()
            subprocess.call(f"sudo virt-copy-in -a {self.nombre}.qcow2 /mnt/tmp/{nombre_user}/rc.local /etc", shell = True)
            log.debug(f"Fichero rc.local actualizado con éxito para {self.nombre} en /etc")

            # Editar el fichero de configuración de HAProxy /etc/haproxy/haproxy.cfg
            # Primero se escribe lo que incluye el fichero haproxy.cfg por defecto
            haproxy_cfg_path = (f"/mnt/tmp/{nombre_user}/haproxy.cfg")
            log.info(f"Fichero haproxy.cfg creado con éxito en /mnt/tmp/{nombre_user}")
            with open(haproxy_cfg_path, "w") as haproxy_cfg:
               haproxy_cfg.write("global\n	log /dev/log	local0\n	log /dev/log	local1 notice\n	chroot /var/lib/haproxy\n	stats socket /run/haproxy/admin.sock mode 660 level admin expose-fd listeners\n	stats timeout 30s\n	user haproxy\n	group haproxy\n	daemon\n")
               haproxy_cfg.write("\n")
               haproxy_cfg.write("	# Default SSL material locations\n	ca-base /etc/ssl/certs\n	crt-base /etc/ssl/private")
               haproxy_cfg.write("\n")
               haproxy_cfg.write("	# See: https://ssl-config.mozilla.org/#server=haproxy&server-version=2.0.3&config=intermediate\n        ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384\n")
               haproxy_cfg.write("        ssl-default-bind-ciphersuites TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256\n")
               haproxy_cfg.write("        ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets")
               haproxy_cfg.write("\n")
               haproxy_cfg.write("defaults\n	log	global\n	mode	http\n	option	httplog\n	option	dontlognull\n        timeout connect 5000\n        timeout client  50000\n        timeout server  50000\n")
               haproxy_cfg.write("	errorfile 400 /etc/haproxy/errors/400.http\n	errorfile 403 /etc/haproxy/errors/403.http\n	errorfile 408 /etc/haproxy/errors/408.http\n	errorfile 500 /etc/haproxy/errors/500.http\n	errorfile 502 /etc/haproxy/errors/502.http\n	errorfile 503 /etc/haproxy/errors/503.http\n	errorfile 504 /etc/haproxy/errors/504.http\n")

               # Código a añadir al fichero /etc/haproxy/haproxy.cfg
               haproxy_cfg.write("frontend lb\n")
               haproxy_cfg.write("	bind *:80\n")
               haproxy_cfg.write("	mode http\n")
               haproxy_cfg.write("	default_backend webservers\n")
               haproxy_cfg.write("backend webservers\n")
               haproxy_cfg.write(f"	server s1 10.11.2.31:80 check\n")
               if num_servidores >= 2:
                  haproxy_cfg.write(f"	server s2 10.11.2.32:80 check\n") 
               if num_servidores >= 3:
                  haproxy_cfg.write(f"	server s3 10.11.2.33:80 check\n") 
               if num_servidores >= 4:
                  haproxy_cfg.write(f"	server s4 10.11.2.34:80 check\n") 
               if num_servidores >= 5:
                  haproxy_cfg.write(f"	server s5 10.11.2.35:80 check\n") 
               
            # Copiar el fichero de configuración haproxy.cfg al lb en /etc/haproxy
            subprocess.call(f"sudo virt-copy-in -a {self.nombre}.qcow2 {haproxy_cfg_path} /etc/haproxy", shell=True)
            log.debug(f"Fichero haproxy.cfg actualizado con éxito para {self.nombre} en /etc/haproxy")

         else:
         # Configuración para las otras máquinas virtuales
            intr.write(f"auto lo\niface lo inet loopback\n\nauto eth0\niface eth0 inet static\naddress {config['address']}\nnetmask 255.255.255.0\ngateway {config['gateway']}\n")
            log.info(f"Fichero interfaces actualizado con éxito en /mnt/tmp/{nombre_user}")

         # --------OPCIONAL: CONFIGURACIÓN DEL HAPROXY para el s1, s2, s3, s4, s5---------------------------------------------------------------------------  
            if self.nombre != 'c1' :
               #Configuración de los servidores, la página web y el script de arranque del servidor apache2
               subprocess.call(f"touch /mnt/tmp/{nombre_user}/index.html", shell = True)
               log.info(f"Fichero index.html actualizado con éxito en /mnt/tmp/{nombre_user}")
               subprocess.call(f"touch /mnt/tmp/{nombre_user}/rc.local", shell = True)
               subprocess.call(f"chmod +x /mnt/tmp/{nombre_user}/rc.local", shell = True)
               subprocess.call(f"echo {self.nombre} > /mnt/tmp/{nombre_user}/index.html", shell = True)
               intr2 = open(f'/mnt/tmp/{nombre_user}/rc.local',"w")
               intr2.write("#!/bin/bash \nsudo apachectl start\nexit 0\n")
               intr2.close()
               subprocess.call(f"sudo virt-copy-in -a {self.nombre}.qcow2 /mnt/tmp/{nombre_user}/index.html /var/www/html", shell = True)
               log.debug(f"Fichero index.html actualizado con éxito para {self.nombre} en /var/www/html")
               subprocess.call(f"sudo virt-copy-in -a {self.nombre}.qcow2 /mnt/tmp/{nombre_user}/rc.local /etc", shell = True)
               log.debug(f"Fichero rc.local actualizado con éxito para {self.nombre} en /etc")
            
    else:
         log.error(f"Dirección IP no especificada para {self.nombre}")
       
    intr.close()
    # copiar el fichero interfaces al directorio  /etc/network de imagen self.qcow2 utilizada en la MV self 
    subprocess.call(f"sudo virt-copy-in -a {self.nombre}.qcow2 /mnt/tmp/{nombre_user}/interfaces /etc/network",shell =True)              
    log.debug(f"Fichero interfaces actualizado con éxito para {self.nombre} en /etc/network")
    #Para cabiar el contenido del archivo hosts de cada máquina, poniendoles su nombre en vez de cdps cdps
    subprocess.call(f"sudo virt-edit -a {self.nombre}.qcow2 /etc/hosts -e 's/127.0.1.1.*/127.0.1.1 {self.nombre}/'",shell =True)       
    log.debug(f"Fichero hosts modificado correctamente para {self.nombre} en /etc")
    if(router):
      subprocess.call(f"sudo virt-edit -a {self.nombre}.qcow2 /etc/sysctl.conf -e 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/'",shell =True)
      
    log.info(f"Configuración de {self.nombre} realizada con éxito.\n")

 def arrancar_mv (self):
    log.debug(f"arrancar_mv {self.nombre}")
    subprocess.call(f"sudo virsh start {self.nombre}",shell =True)
    log.info(f"Máquina {self.nombre} arrancada correctamente.")      # Arrancamos la maquina
    
 def mostrar_consola_mv (self):
    log.debug(f"mostrar_mv {self.nombre}")
    subprocess.call(f"xterm -rv -sb -rightbar -fa monospace -fs 10 -title {self.nombre} -e 'sudo virsh console {self.nombre}' &", shell=True)      # Arrancamos la consola textual

 def parar_mv (self):
    log.debug(f"parar_mv {self.nombre}")
    subprocess.call(["sudo", "virsh", "shutdown", f"{self.nombre}"])
    log.info(f"Máquina {self.nombre} parada correctamente.")         # Paramos la maquina

 def liberar_mv (self):
    log.debug(f"liberar_mv {self.nombre}")
    subprocess.call(["sudo", "virsh", "destroy", f"{self.nombre}"])
    subprocess.call(["sudo", "virsh", "undefine", f"{self.nombre}"])
    subprocess.call(["rm", f"{self.nombre}.qcow2", "-f"])
    log.debug(f"Archivo {self.nombre}.qcow2 eliminado correctamente.")
    subprocess.call(["rm", f"{self.nombre}.xml"])
    log.debug(f"Archivo {self.nombre}.xml eliminado correctamente.")
    log.info(f"{self.nombre} liberada correctamente.\n")             # Liberamos la maquina
    