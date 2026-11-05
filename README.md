
# Tecoff Digital

**A modular Django-based web platform for business management, digital catalogs, and website functionality.**

## Overview

Tecoff Digital is a web application built with Django, designed around a modular architecture. The project brings together account management, catalog functionality, dashboard interfaces, and website-related components in a single platform.

Its structure separates different areas of the application into dedicated modules, making the codebase easier to organize, maintain, and extend.

## Features

- **Account Management:** Functionality related to user accounts and access.
- **Catalog Management:** A dedicated module for managing digital catalog content.
- **Dashboard:** Dashboard interfaces for application management.
- **Website Management:** Components for website-related functionality.
- **Modular Architecture:** Separate Django applications for different functional areas.
- **Reusable Templates and Assets:** Shared templates and static resources across the application.

## Project Structure

```text
tecoffdigital/
├── accounts/        # Account-related functionality
├── catalog/         # Catalog management
├── dashboard/       # Dashboard interfaces
├── presentation/    # Presentation-related components
├── website/         # Website functionality
├── game/            # Game-related module
├── config/          # Project configuration
├── assets/          # Static assets
├── templates/       # Shared HTML templates
├── manage.py
├── requirements.txt
└── README.md
```

## Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript, Django Templates
- **Architecture:** Modular Django applications

## Getting Started

### Prerequisites

- Python 3.x
- pip
- Git

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/sajjadseifi/tecoffdigital.git
   cd tecoffdigital
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   On Windows:

   ```bash
   .venv\Scripts\activate
   ```

   On macOS and Linux:

   ```bash
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

5. Create an administrator account:

   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:

   ```bash
   python manage.py runserver
   ```

The application will be available at:

```text
http://127.0.0.1:8000/
```

Before running the project, review the settings in the `config/` directory and configure environment-specific values, including database settings, as needed.

## Project Goals

Tecoff Digital explores a modular approach to building web platforms, with an emphasis on separating application responsibilities, organizing reusable components, and supporting future feature expansion.

## Author

**Sajjad Seifi**

- GitHub: [@sajjadseifi](https://github.com/sajjadseifi)

## License

No license has been specified for this repository.
