# GUÍA DE DESPLIEGUE - CellHub en EC2 (AWS Academy)

## Arquitectura del sistema
```
┌─────────────────────────────────────────────────────────────┐
│ EC2 Instance (t2.micro o mayor)                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────┐  ┌──────────────┐  ┌────────────────┐       │
│  │  Nginx    │  │ Docker       │  │ Docker Volumes │       │
│  │ Gateway   ├──┤ Compose      ├──┤ (data, logs)   │       │
│  │ (Port 80) │  │              │  │                │       │
│  └───────────┘  └──────────────┘  └────────────────┘       │
│       ↓              ↓                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Django + DRF  │  Flask Payments  │  Redis/Celery  │   │
│  │  Postgres      │  Nginx routing   │  Logging       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Requisitos previos (AWS Academy)
- **EC2 Instance**: Ubuntu 22.04 LTS o Amazon Linux 2, tipo `t2.micro` (1 GB RAM, 1 vCPU mínimo)
- **Security Group**: Reglas de entrada:
  - SSH (22) desde tu IP o 0.0.0.0/0
  - HTTP (80) desde 0.0.0.0/0
  - HTTPS (443) opcional
- **GitHub repo**: Repositorio privado o público accesible (configurar SSH key o personal access token)
- **IAM Role** (opcional): Para acceso a S3, CloudWatch, Secrets Manager en producción

## Opción 1: Auto-deployment (Recomendado)

### 1.1 Crear instancia EC2 en AWS Academy

```bash
# En AWS Console:
1. Ir a EC2 → Instances → Launch Instance
2. Seleccionar "Ubuntu 22.04 LTS" o "Amazon Linux 2"
3. Tipo: t2.micro (free tier)
4. Security Group: crear nuevo o seleccionar existente
   - Inbound:
     - SSH (22) - source: My IP o 0.0.0.0/0
     - HTTP (80) - source: 0.0.0.0/0
5. Keypair: crear nueva o usar existente
6. Storage: 8 GB (default)
7. En "Advanced details" → "User data": pegar contenido de user-data.sh
8. Launch instance
```

### 1.2 Esperar a que se auto-configure (3-5 minutos)

El script `user-data.sh` ejecutará:
- Actualizar paquetes del sistema
- Instalar Docker y docker-compose
- Clonar repositorio de GitHub
- Ejecutar `docker compose build`
- Ejecutar `docker compose up -d`
- Ejecutar migraciones de BD
- Cargar datos de ejemplo (seed_data.py)

### 1.3 Verificar que los servicios están corriendo

```bash
# SSH a la instancia
ssh -i /ruta/a/tu/keypair.pem ubuntu@EC2_PUBLIC_IP

# Dentro de la instancia
docker ps
# Debería mostrar: nginx, django_web, flask_payment_service, postgres, redis, celery_worker

# Verificar health endpoint
curl http://localhost/health/
# Respuesta esperada: {"status":"up"}

# Ver logs
docker compose logs django_web
docker compose logs celery_worker
```

### 1.4 Acceder a la aplicación

- **Frontend**: http://EC2_PUBLIC_IP/
- **API Docs**: http://EC2_PUBLIC_IP/api/docs/
- **Admin**: http://EC2_PUBLIC_IP/admin/ (crear superuser primero)
- **Health**: http://EC2_PUBLIC_IP/health/
- **System Info**: http://EC2_PUBLIC_IP/api/v1/system/info/

## Opción 2: Manual deployment

Si prefieres configurar paso a paso:

### 2.1 Conectar a la instancia

```bash
ssh -i keypair.pem ubuntu@EC2_PUBLIC_IP  # Ubuntu
ssh -i keypair.pem ec2-user@EC2_PUBLIC_IP  # Amazon Linux 2
```

### 2.2 Instalar dependencias

```bash
# Ubuntu 22.04
sudo apt-get update
sudo apt-get install -y docker.io docker-compose git curl

# Amazon Linux 2
sudo yum update -y
sudo yum install -y docker git curl
sudo amazon-linux-extras install -y docker
sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2.3 Agregar usuario al grupo docker (sin sudo)

```bash
sudo usermod -aG docker $(whoami)
# Logout y login para aplicar cambios
```

### 2.4 Clonar y configurar repositorio

```bash
mkdir -p /opt/cellhub
cd /opt/cellhub
git clone https://github.com/YOUR_USER/cellhub.git .

# Crear archivo .env
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=tu-clave-secreta-aqui
ALLOWED_HOSTS=*
CELERY_BROKER_URL=redis://redis:6379/0
EOF

# Configurar permisos
sudo chown -R $USER:$USER /opt/cellhub
```

### 2.5 Construir y lanzar servicios

```bash
cd /opt/cellhub
docker compose build
docker compose up -d

# Esperar ~10 segundos
sleep 10

# Ejecutar migraciones
docker compose exec django_web python manage.py migrate

# Cargar datos de ejemplo (opcional)
docker compose exec django_web python seed_data.py

# Crear superuser (interactivo)
docker compose exec django_web python manage.py createsuperuser
```

### 2.6 Verificar servicios

```bash
docker compose ps
docker compose logs -f nginx
```

## Opción 3: Monitoreo en segundo plano

```bash
# Ver logs en tiempo real
docker compose logs -f

# Logs de un servicio específico
docker compose logs -f django_web
docker compose logs -f celery_worker

# Ver estadísticas de contenedores
docker stats

# Reiniciar servicios
docker compose restart

# Detener (sin eliminar)
docker compose stop

# Reanudar
docker compose start

# Apagar completamente
docker compose down  # ⚠️ Eliminará volúmenes si no usas -v
```

## Verificación post-deployment

### 3.1 Endpoints de prueba

```bash
# Health check
curl http://EC2_IP/health/

# System info
curl http://EC2_IP/api/v1/system/info/

# Swagger UI
curl http://EC2_IP/api/docs/

# Listar productos
curl http://EC2_IP/api/v1/products/

# Status de servicios (debe retornar conectado)
curl http://EC2_IP/api/v1/system/info/ | jq '.broker'
```

### 3.2 Acceso a admin

```bash
# Dentro de la instancia
docker compose exec django_web python manage.py createsuperuser
# Ingresa: email, contraseña

# En el navegador
http://EC2_IP/admin/
```

### 3.3 Verificar Celery worker

```bash
# Dentro del contenedor django_web
docker compose exec django_web python manage.py shell

>>> from celery import current_app
>>> current_app.control.inspect().active()
# Debe retornar información de tareas activas
```

## Troubleshooting

### Contenedores no inician

```bash
docker compose logs -f
# Buscar "error" o "exception"

# Reconstruir desde cero
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Puerto 80 en uso

```bash
# Encontrar proceso usando puerto 80
sudo lsof -i :80

# Si es Nginx conflictivo, parar y remover
docker compose down
sudo systemctl stop nginx  # si está instalado localmente
docker compose up -d
```

### Migraciones fallo

```bash
docker compose logs django_web | grep -i migrate

# Manualmente
docker compose exec django_web python manage.py makemigrations
docker compose exec django_web python manage.py migrate --run-syncdb
```

### Redis no conecta

```bash
# Verificar que Redis está corriendo
docker ps | grep redis

# Verificar conectividad
docker compose exec django_web redis-cli -h redis ping
# Debe retornar: PONG
```

### Celery worker no procesa tareas

```bash
# Ver logs del worker
docker compose logs celery_worker

# Verificar que el broker está configurado correctamente
docker compose exec django_web python manage.py shell
>>> from django.conf import settings
>>> print(settings.CELERY_BROKER_URL)

# Si cambias la config, reiniciar worker
docker compose restart celery_worker
```

## Variables de entorno importantes (.env)

```bash
# Django
DEBUG=False  # En producción: False
SECRET_KEY=tu-clave-secreta-12345678901234567890
ALLOWED_HOSTS=*  # En producción: especificar IPs/dominios

# Celery/Redis
CELERY_BROKER_URL=redis://redis:6379/0

# Base de datos (por defecto SQLite en contenedor)
# Para RDS: postgresql://user:pass@rds-endpoint:5432/cellhub_db

# Configuración de email (si necesitas notificaciones vía email)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@cellhub.local

# Variables de idioma
LANGUAGE_CODE=es-co
```

## Producción - Consideraciones

1. **SSL/TLS**: Usar Nginx con certificado (Let's Encrypt + certbot)
2. **Secrets Manager**: Guardar `SECRET_KEY` en AWS Secrets Manager
3. **RDS**: Usar PostgreSQL en RDS en lugar de contenedor SQLite
4. **S3**: Almacenar imágenes de productos en S3, no en EC2
5. **CloudWatch**: Configurar logs y métricas
6. **Auto-scaling**: Usar ASG (Auto Scaling Group) si necesitas múltiples instancias
7. **Load Balancer**: ALB (Application Load Balancer) si escalas horizontalmente

## Despliegue en múltiples AZs (Opcional)

Para alta disponibilidad, replicar esta arquitectura en múltiples instancias EC2:
- Usar RDS Multi-AZ para BD
- Usar ElastiCache para Redis (Multi-AZ)
- ALB distribuyendo tráfico entre EC2s
- Route 53 para DNS y failover

## Support y documentación

- Django docs: https://docs.djangoproject.com/
- DRF docs: https://www.django-rest-framework.org/
- Docker Compose: https://docs.docker.com/compose/
- Celery: https://docs.celeryproject.io/
- AWS Academy: https://aws.amazon.com/training/awsacademy/

---

**Última actualización**: Mayo 2026
**Versión**: 1.0.0
