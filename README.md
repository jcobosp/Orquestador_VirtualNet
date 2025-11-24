# Orquestador VirtualNet

**Orquestador VirtualNet** es una herramienta de automatización diseñada para crear, configurar y gestionar de forma integral un entorno virtualizado completo utilizando **QEMU/KVM**, **libvirt**, redes virtuales basadas en bridges de Linux y scripts de orquestación en **Python**.

El sistema permite desplegar en segundos una topología funcional compuesta por:

- Un **cliente**
- Un **router + balanceador de carga** (HAProxy)
- Varios **servidores web** (Apache)
- Dos **LAN virtuales** interconectadas mediante el nodo balanceador

Toda la infraestructura (máquinas virtuales, discos, redes, servicios y rutas) se genera de forma automática y reproducible desde una interfaz de línea de comandos.

---

## Funcionalidades principales

### Aprovisionamiento automático de máquinas virtuales
Orquestador VirtualNet crea máquinas virtuales mediante:
- Generación de discos **QCOW2** desde una imagen base
- Construcción dinámica de definiciones XML para libvirt
- Asignación automática de interfaces de red
- Creación y gestión de bridges virtuales (`LAN1` y `LAN2`)

### Configuración automática de red
Cada VM recibe:
- Dirección IP estática
- Hostname configurado
- Rutas y puerta de enlace
- Entradas completas en `/etc/hosts`
- Ficheros de red autogenerados

### Nodo balanceador + router totalmente automatizado
El nodo `LB` se configura automáticamente como:
- **Router** entre dos redes virtuales (LAN1 ↔ LAN2)
- **Balanceador de carga** mediante **HAProxy**, distribuyendo tráfico HTTP entre los servidores web

### Servidores web totalmente configurados
Los servidores (`S1` … `SN`) incluyen:
- Apache2 funcionando desde el arranque
- Página `index.html` generada automáticamente
- Configuración lista para recibir tráfico a través de LB

### Gestión completa del ciclo de vida
El sistema permite:
- Crear
- Arrancar
- Parar
- Monitorizar
- Liberar (borrar completamente)

todas las máquinas y redes del entorno.

---

## Arquitectura del entorno

```
                 10.11.1.0/24 (LAN1)
      +--------------------------------------+
      |                                      |
   Cliente (10.11.1.2)    LB (10.11.1.1 / 10.11.2.1)
      |                      |
      +----------------------+----------------------+
                             |
                     10.11.2.0/24 (LAN2)
                 +-----------+-----------+----- ...
                 |           |           |
               S1           S2          S3   ... SN
```

---

## Estructura del proyecto

```
.
├── auto-p2.py           # Script principal de orquestación
├── lib_mv.py            # Librería para gestionar máquinas virtuales
├── auto-p2.json         # Configuración del despliegue (num_serv, debug)
├── plantilla-vm-pc1.xml # Plantilla XML base para VM
└── README.md
```

---

## Configuración (`auto-p2.json`)

Ejemplo:

```json
{
  "num_serv": 3,
  "debug": true
}
```

- `num_serv` → número de servidores web (1 a 5)
- `debug` → activa/desactiva el modo de depuración

---

## Requisitos

### Sistema anfitrión
- Linux con:
  - **KVM / QEMU**
  - **libvirt** + herramientas `virsh`
  - `virt-manager`
  - Utilidades `qemu-img`, `virt-copy-in`, `virt-edit`, `virt-cat`, `virt-ls`
- Python 3 con:
  - `lxml`
  - `logging`

---

## Uso del sistema

### 1️. Crear todo el entorno
```
python3 auto-p2.py crear
```

Acciones automáticas:
- Creación de todas las máquinas virtuales
- Generación de definiciones XML
- Construcción de `LAN1` y `LAN2`
- Configuración de red, servicios y rutas
- Instalación de HAProxy (balanceador)
- Instalación de Apache (servidores)

---

### 2️. Arrancar todas las máquinas
```
python3 auto-p2.py arrancar
```

Abre consolas virtuales y arranca todos los nodos.

---

### 3️. Monitorizar el entorno
```
python3 auto-p2.py monitor
```

Muestra:
- Estado de cada VM
- Estadísticas de CPU
- Conectividad entre nodos

---

### 4️. Parar todas las máquinas
```
python3 auto-p2.py parar
```

---

### 5️. Eliminar completamente el escenario
```
python3 auto-p2.py liberar
```

Borra:
- Definiciones XML
- Discos QCOW2
- Ficheros temporales
- Bridges virtuales

---

## Capacidades demostradas en este proyecto

- Automatización avanzada de infraestructuras virtualizadas
- Control programático de QEMU/KVM y libvirt
- Manipulación de XML para plantillas de máquinas virtuales
- Ingeniería de redes Linux (bridges, enrutamiento, gateways)
- Orquestación de servicios (Apache, HAProxy)
- Desarrollo de herramientas de infraestructura mediante Python

---


