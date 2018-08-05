#!/bin/bash
apt-get update
apt-get install -y mosquitto mosquitto-clients openssl
touch /etc/mosquitto/passwd
mosquitto_passwd -b /etc/mosquitto/passwd mosquitto passw0rd
cat > /etc/mosquitto/conf.d/default.conf <<- "EOF"
allow_anonymous false
password_file /etc/mosquitto/passwd
EOF

echo "********** Securing Mosquitto **********"
openssl genrsa -aes256 -passout pass:passw0rd -out m2mqtt_ca.key 2048 -batch
openssl req -new -sha256 -x509 -days 3650 -key m2mqtt_ca.key -passin pass:passw0rd -out m2mqtt_ca.crt -subj "/C=GB/ST=Bournemouth/L=Bournemouth/O=MakeBournemouth/OU=vPiP/CN=makebournemouth.com" -batch
openssl genrsa -out m2mqtt_srv.key 2048 -batch
openssl req -new -sha256 -out m2mqtt_srv.csr -key m2mqtt_srv.key -passin pass:passw0rd -subj "/C=GB/ST=Bournemouth/L=Bournemouth/O=MakeBournemouth/OU=vPiP/CN=vpipBroker.local" -batch
openssl x509 -req -in m2mqtt_srv.csr -CA m2mqtt_ca.crt -CAkey m2mqtt_ca.key -CAcreateserial -passin pass:passw0rd -out m2mqtt_srv.crt -days 3650
rm m2mqtt_srv.csr
mv m2mqtt_ca.* /etc/mosquitto/ca_certificates
mv m2mqtt_srv.* /etc/mosquitto/certs
cat > /etc/mosquitto/conf.d/security.conf <<- "EOF"
port 8883
cafile /etc/mosquitto/ca_certificates/m2mqtt_ca.crt
certfile /etc/mosquitto/certs/m2mqtt_srv.crt
keyfile /etc/mosquitto/certs/m2mqtt_srv.key
tls_version tlsv1.2
EOF
systemctl restart mosquitto.service
