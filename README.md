# App Subscription Platform

A backend app based on Django and Django Rest Framework deployed on Docker.

## Getting Started

### Prerequisites

- Python 3.9+
- pip
- Docker(for containerized deployment)

### Local Setup

1. Clone the repository:
   ```
   git clone https://github.com/MuhammadUsaid/AppSubcriptionPlatform.git
   cd AppSubcriptionPlatform
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```
   python manage.py migrate
   ```

4. Start the development server:
   ```
   python manage.py runserver
   ```

   The app should now be running at `http://localhost:8000`.

### Running Tests

To run the tests for the API:

1. Run the following command:
```
python manage.py test api
```

### Deployment on Docker

1. Build:
```
docker-compose build
```

2. Run the container:
```
docker-compose up
```
The app will be running at `http://0.0.0.0:8000`
