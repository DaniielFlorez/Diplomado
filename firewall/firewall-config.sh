#!/bin/bash

# Borrar reglas anteriores
iptables -F

# Permitir tráfico entrante a puertos específicos (e.g., web-app en el puerto 5000, Nginx en el puerto 80)
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 5000 -j ACCEPT

# Permitir tráfico de la red interna de Docker
iptables -A INPUT -i lo -j ACCEPT

# Registrar cualquier otro tráfico no autorizado
iptables -A INPUT -j LOG --log-prefix "IPTables-Rejected: " --log-level 4

# Bloquear cualquier otro tráfico no autorizado
iptables -A INPUT -j DROP

# Mantener el contenedor en ejecución
sleep infinity