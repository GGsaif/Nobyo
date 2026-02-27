# Django E-commerce Website - Production Ready

A production-ready Django e-commerce platform with modern features, security hardening, and deployment configurations.

## Features

- **Product Management**: Categorized product listings with search and filtering
- **Shopping Cart**: Session-based cart with real-time updates
- **User Authentication**: Secure registration, login, and password reset
- **Order Management**: Complete checkout process with delivery zones
- **Admin Panel**: Comprehensive admin interface for managing products and orders
- **Production Ready**: Docker, Gunicorn, Nginx, Redis caching, and security hardening

## Tech Stack

- **Backend**: Django 5.0+, Python 3.11+
- **Database**: PostgreSQL (production), SQLite (development)
- **Caching**: Redis
- **Server**: Gunicorn with Nginx reverse proxy
- **Containerization**: Docker & Docker Compose
- **Static Files**: WhiteNoise with compression

## Prerequisites

- Docker & Docker Compose (recommended)
- Python 3.11+ (for local development)
- PostgreSQL 15+ (for production)
- Redis (optional, for caching)

## Quick Start (Development)

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Nobyo
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Build and run**
   ```bash
   docker-compose up --build
   ```

4. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Access the application**
   - Website: http://localhost:8000
   - Admin: http://localhost:8000/admin

### Option 2: Manual Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with DEBUG=True
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Production Deployment

### Pre-Deployment Checklist

- [ ] Set `DEBUG=False` in environment
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up PostgreSQL database
- [ ] Configure `CSRF_TRUSTED_ORIGINS`
- [ ] Set up email service (SMTP)
- [ ] Configure Redis for caching (optional)
- [ ] Set up SSL/TLS certificates
- [ ] Configure static file serving
- [ ] Set up error tracking (Sentry - optional)

### Deployment Options

#### Option 1: VPS with Docker (Recommended)

1. **Prepare your VPS**
   ```bash
   # Install Docker and Docker Compose
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

2. **Clone and configure**
   ```bash
   git clone <your-repo-url>
   cd Nobyo
   cp .env.production.example .env
   # Edit .env with production values
   ```

3. **Deploy with production compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

4. **Run migrations**
   ```bash
   docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
   ```

5. **Collect static files**
   ```bash
   docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
   ```

6. **Create superuser**
   ```bash
   docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
   ```

#### Option 2: Render.com (PaaS)

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Create Web Service on Render**
   - Connect your GitHub repository
   - Runtime: Python 3
   - Build Command:
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - Start Command:
     ```bash
     gunicorn --config gunicorn_config.py core.wsgi:application
     ```

3. **Add Environment Variables**
   - `PYTHON_VERSION`: `3.11.0`
   - `SECRET_KEY`: (generate secure key)
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `your-app.onrender.com`
   - `DATABASE_URL`: (from Render PostgreSQL)
   - `CSRF_TRUSTED_ORIGINS`: `https://your-app.onrender.com`

4. **Add PostgreSQL Database**
   - Create PostgreSQL database on Render
   - Copy `DATABASE_URL` to environment variables

## Environment Variables

### Required

- `SECRET_KEY`: Django secret key (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Space-separated list of allowed hosts
- `DATABASE_URL`: PostgreSQL connection string

### Optional

- `CSRF_TRUSTED_ORIGINS`: Comma-separated list of trusted origins (e.g., `https://yourdomain.com`)
- `REDIS_URL`: Redis connection string for caching
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: Email configuration
- `GUNICORN_WORKERS`: Number of Gunicorn workers (default: CPU cores * 2 + 1)

## Security Features

- ✅ CSRF protection with trusted origins
- ✅ Secure cookies (HTTPS only in production)
- ✅ XSS protection headers
- ✅ Content type sniffing protection
- ✅ Clickjacking protection
- ✅ HSTS (HTTP Strict Transport Security)
- ✅ SQL injection protection (Django ORM)
- ✅ Password validation
- ✅ Session security

## Performance Optimizations

- ✅ Database query optimization with `select_related` and `prefetch_related`
- ✅ Redis caching for sessions and data
- ✅ Static file compression with WhiteNoise
- ✅ Pagination for large datasets
- ✅ Database connection pooling
- ✅ Gunicorn with multiple workers
- ✅ Nginx reverse proxy with gzip compression

## Monitoring & Logging

- Application logs stored in `logs/django.log`
- Rotating file handler (15MB per file, 10 backups)
- Error notifications via email (production)
- Console logging (development)
- Request/response logging

## Maintenance

### Backup Database

```bash
# Docker
docker-compose exec db pg_dump -U postgres nobyo_db > backup.sql

# Restore
docker-compose exec -T db psql -U postgres nobyo_db < backup.sql
```

### View Logs

```bash
# Application logs
tail -f logs/django.log

# Docker logs
docker-compose logs -f web
```

### Update Dependencies

```bash
pip install -r requirements.txt --upgrade
python manage.py migrate
python manage.py collectstatic --noinput
```

## Troubleshooting

### Static files not loading

```bash
python manage.py collectstatic --noinput
# Ensure STATIC_ROOT and STATIC_URL are configured correctly
```

### Database connection errors

- Check `DATABASE_URL` format
- Ensure PostgreSQL is running
- Verify database credentials

### Permission errors in Docker

```bash
# Fix file permissions
docker-compose exec web chown -R django:django /app
```

## Development

### Running Tests

```bash
python manage.py test
```

### Code Quality Checks

```bash
# Check for deployment issues
python manage.py check --deploy

# Check for missing migrations
python manage.py makemigrations --check --dry-run
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions, please open an issue on GitHub.
