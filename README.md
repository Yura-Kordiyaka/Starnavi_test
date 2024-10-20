# FastAPI Application

This is a FastAPI application that you can run using Docker. To get the application up and running, follow these steps: 

1. Clone the project repository to your local machine.

2. Navigate to the `app` directory: `cd app`

3. Create a `.env` file with the following variables:
   ```plaintext
   DB_HOST=postgres
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_NAME=postgres
   
   
   DB_TEST_HOST=test_db
   DB_TEST_PORT=5432
   DB_TEST_USER=test_user
   DB_TEST_PASSWORD=test_password
   DB_TEST_NAME=test_db
   
   
   
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_MINUTES=10080
   JWT_SECRET_KEY=narscbjim@$@&^@&%^&RFghgjvbdsha
   JWT_REFRESH_SECRET_KEY=13ugfdfgh@#$%^@&jkl45678902
   AI_API_KEY=AIzaSyD0SvXw9kXySiczpXPrm_8rhz9kRT1eCPY
   
4. Build and run the application using Docker Compose: `docker-compose up --build`
5. Once the application is running, open your web browser and go to the following URL to access the Swagger documentation: [http://0.0.0.0:1715/docs](http://0.0.0.0:1715/docs)


