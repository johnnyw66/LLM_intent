docker run -d \
  --name mqtt-broker \
  -p 1883:1883 \
  eclipse-mosquitto \
  sh -c "echo -e 'listener 1883\nallow_anonymous true' > /mosquitto/config/mosquitto.conf && mosquitto -c /mosquitto/config/mosquitto.conf"

