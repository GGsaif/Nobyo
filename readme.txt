========================================================================
NOBYO - E-COMMERCE WEBSITE SETUP & RUN WALKTHROUGH
========================================================================

This guide provides an exact, step-by-step walkthrough of how to set up
and run the Nobyo Django application on local environment.

------------------------------------------------------------------------
STEP 1: PREREQUISITES
------------------------------------------------------------------------
- Python 3.11+ installed (Verified Python 3.14.3 on system)
- Pip package manager installed

------------------------------------------------------------------------
STEP 2: ENVIRONMENT CONFIGURATION
------------------------------------------------------------------------
Ensure a `.env` file exists in the root directory (d:\Nobyo\.env).

Sample `.env` content for local development:
------------------------------------------------------------------------
DEBUG=True
SECRET_KEY=django-insecure-dev-key-12345
ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
------------------------------------------------------------------------

------------------------------------------------------------------------
STEP 3: INSTALL DEPENDENCIES
------------------------------------------------------------------------
Run the following command in PowerShell / Terminal at the project root:

    python -m pip install "python-dotenv" "Pillow" "whitenoise" "django-compressor" "dj-database-url"

Note: If using Python 3.14+, use the above command rather than strict 
pinned versions in requirements.txt to automatically install compatible 
pre-built binary wheels (e.g., Pillow 12+).

------------------------------------------------------------------------
STEP 4: RUN SYSTEM CHECKS
------------------------------------------------------------------------
Verify that Django and all dependencies are properly configured:

    python manage.py check

------------------------------------------------------------------------
STEP 5: APPLY DATABASE MIGRATIONS
------------------------------------------------------------------------
Apply the SQLite database migrations:

    python manage.py migrate

------------------------------------------------------------------------
STEP 6: SUPERUSER CREDENTIALS
------------------------------------------------------------------------
Superuser account has been created for admin access:
- Username: Gsaif
- Password: 1234

To create another superuser manually:
    python manage.py createsuperuser

------------------------------------------------------------------------
STEP 7: START THE DEVELOPMENT SERVER
------------------------------------------------------------------------
Launch the Django local development server on port 8000:

    python manage.py runserver 8000

------------------------------------------------------------------------
STEP 8: ACCESS THE APPLICATION
------------------------------------------------------------------------
Open your browser and navigate to:
- Website:    http://127.0.0.1:8000/
- Admin Panel: http://127.0.0.1:8000/admin/ (Login with Gsaif / 1234)

========================================================================
