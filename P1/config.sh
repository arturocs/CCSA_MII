#!/bin/sh

# Deshabilitar plugins
docker exec -u www-data servicio_nextcloud01_76067384 php occ app:disable accessibility
docker exec -u www-data servicio_nextcloud01_76067384 php occ app:disable dashboard
docker exec -u www-data servicio_nextcloud01_76067384 php occ app:disable nextcloud_announcements
docker exec -u www-data servicio_nextcloud01_76067384 php occ app:disable photos
docker exec -u www-data servicio_nextcloud01_76067384 php occ app:disable weather_status
docker exec -u www-data servicio_nextcloud01_76067384 php occ app:disable user_status
docker exec -u www-data servicio_nextcloud01_76067384 php occ app:disable survey_client
docker exec -u www-data servicio_nextcloud01_76067384 php occ app:disable support
docker exec -u www-data servicio_nextcloud01_76067384 php occ app:disable recommendations
docker exec -u www-data servicio_nextcloud01_76067384 php occ app:disable updatenotification

# Configurar ldap
docker exec servicio_ldap_76067384 ldapadd -x -D "cn=admin,dc=openstack,dc=org" -w password -c -f /home/user.ldif
docker exec servicio_ldap_76067384 ldappasswd -s arturo -w password -D "cn=admin,dc=openstack,dc=org" -x "cn=arturo,ou=Users,dc=openstack,dc=org"