FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script and requirements file into the container
COPY ../../src/support_sphere_py /app/support_sphere_py
COPY ../../deployment/values.dev.yaml /app/deployment/values.dev.yaml

# Install any necessary dependencies
RUN pip install --no-cache-dir ./support_sphere_py

# Command to run the Python script
ENTRYPOINT ["sh", "-c", "python3 ./support_sphere_py/tests/resources/scripts/role_based_access_control.py && python3 ./support_sphere_py/tests/resources/scripts/update_db_sample_data.py"]