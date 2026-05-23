#!/bin/bash
# user-data.sh - Bootstrap script para EC2 (AWS Academy) - Amazon Linux 2
# OS: Amazon Linux 2 (AL2)
# Propósito: Provisionar Docker, clonar repo, e iniciar stack de CellHub
#
# Uso:
#   1. Crear instancia EC2 en AWS Academy (t2.micro o mayor)
#   2. Pegar este script en el campo "User data" al lanzar la instancia
#   3. La instancia se auto-configurará e iniciará los servicios
#   4. Acceder a través de http://EC2_PUBLIC_IP

set -e  # Salir en error
set -x  # Imprimir comandos (para debugging)

# Actualizar paquetes del sistema
yum update -y
yum install -y git curl

# Instalar Docker en Amazon Linux 2
amazon-linux-extras install -y docker
systemctl enable docker
systemctl start docker

# Instalar Docker Compose plugin
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Agregar usuario ec2-user al grupo docker
usermod -aG docker ec2-user

# Crear directorio de deployment
mkdir -p /opt/cellhub
cd /opt/cellhub

# Clonar repositorio (HTTPS; requiere token o repo público)
git clone https://github.com/[YOUR_GITHUB_USER]/cellhub.git . || \
  git clone https://github.com/user/cellhub.git .

# Establecer permisos
chown -R ec2-user:ec2-user /opt/cellhub

# Crear archivo .env para configuración de producción
cat > /opt/cellhub/.env << 'EOF'
# Variables de entorno para CellHub en EC2 (Amazon Linux 2)
DEBUG=False
SECRET_KEY=cambiar-a-clave-secreta-real-en-aws-secrets-manager
ALLOWED_HOSTS=*
CELERY_BROKER_URL=redis://redis:6379/0
DATABASE_URL=sqlite:///db.sqlite3
# Para producción: usar RDS
# DATABASE_URL=postgresql://user:password@rds-endpoint:5432/cellhub_db
EOF

# Construir e iniciar servicios
cd /opt/cellhub
docker-compose build 2>&1 | tee build.log
docker-compose up -d 2>&1 | tee deploy.log

# Esperar a que el servicio Django esté listo
sleep 10

# Ejecutar migraciones
docker-compose exec -T django_web python manage.py migrate 2>&1 | tee migrate.log || true

# Cargar datos de ejemplo (opcional)
docker-compose exec -T django_web python seed_data.py 2>&1 | tee seed.log || true

# Verificar salud
sleep 5
curl -s http://localhost/health/ || echo "Endpoint de salud no disponible aún"
curl -s http://localhost/api/v1/system/info/ || echo "Endpoint de sistema no disponible aún"

# Registrar finalización
echo "Despliegue del stack CellHub completado a las $(date)" >> /var/log/cellhub-bootstrap.log

exit 0
