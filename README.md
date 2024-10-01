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


### API Endpoints

Here are the available API endpoints and instructions on how to use them:

1. **Signup**
   - URL: `POST http://127.0.0.1:8000/signup`
   - Body: 
     ```json
     {
       "username": "your_username",
       "password": "your_password",
       "email": "your_email@example.com"
     }
     ```
   - Expected response: User creation confirmation

2. **Login**
   - URL: `POST http://127.0.0.1:8000/login`
   - Body:
     ```json
     {
       "username": "your_username",
       "password": "your_password"
     }
     ```
   - Expected response: Authentication token

3. **Logout**
   - URL: `POST http://127.0.0.1:8000/logout`
   - Headers: `Authorization: token your_auth_token`
   - Expected response: Logout confirmation

4. **Change Password**
   - URL: `POST http://127.0.0.1:8000/change_pass`
   - Headers: `Authorization: token your_auth_token`
   - Body:
     ```json
     {
       "old_password": "your_old_password",
       "new_password": "your_new_password"
     }
     ```
   - Expected response: Password change confirmation

5. **Get All Apps**
   - URL: `GET http://127.0.0.1:8000/app/`
   - Headers: `Authorization: token your_auth_token`
   - Expected response: List of all apps

6. **Create App**
   - URL: `POST http://127.0.0.1:8000/app/`
   - Headers: `Authorization: token your_auth_token`
   - Body:
     ```json
     {
       "name": "Your App Name",
       "description": "Your App Description"
     }
     ```
   - Expected response: Created app details

7. **Update App**
   - URL: `PUT http://127.0.0.1:8000/app/{app_id}/`
   - Headers: `Authorization: token your_auth_token`
   - Body:
     ```json
     {
       "name": "Updated App Name",
       "description": "Updated App Description"
     }
     ```
   - Expected response: Updated app details

8. **Get Specific App**
   - URL: `GET http://127.0.0.1:8000/app/{app_id}/`
   - Headers: `Authorization: token your_auth_token`
   - Expected response: Specific app details

9. **Update App Subscription**
   - URL: `PUT http://127.0.0.1:8000/app/sub/{app_id}/`
   - Headers: `Authorization: token your_auth_token`
   - Body:
     ```json
     {
       "plan": "STANDARD"
     }
     ```
   - Expected response: Updated subscription details

Note: Replace `your_auth_token`, `your_username`, `your_password`, `your_email@example.com`, `{app_id}`, and other placeholder values with actual data when making requests.

