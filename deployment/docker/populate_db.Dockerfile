FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script and requirements file into the container
COPY ../../src/support_sphere_py /app/support_sphere_py

# Define ARGs for environment variables that will be passed at build time
ARG DB_HOST
ARG DB_PORT
ARG DB_USERNAME
ARG DB_PASSWORD
ARG DB_NAME
ARG SUPABASE_KONG_HOST
ARG SUPABASE_KONG_PORT
ARG JWT_ANON_KEY

# Below ENV values are overridden when running the via K8s Job else the above arg values are used.
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV DB_USERNAME=${DB_USERNAME}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_NAME=${DB_NAME}
ENV SUPABASE_KONG_HOST=${SUPABASE_KONG_HOST}
ENV SUPABASE_KONG_PORT=${SUPABASE_KONG_PORT}
ENV JWT_ANON_KEY=${JWT_ANON_KEY}


# Install any necessary dependencies
RUN pip install --no-cache-dir ./support_sphere_py

# Command to run the Python script
ENTRYPOINT ["sh", "-c", "python3 ./support_sphere_py/tests/resources/scripts/role_based_access_control.py && python3 ./support_sphere_py/tests/resources/scripts/update_db_sample_data.py"]