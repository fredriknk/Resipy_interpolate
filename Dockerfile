# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

RUN apt-get update && apt-get install -y libx11-6 libgl1-mesa-glx libxrender1 build-essential cmake libboost-all-dev

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements_versioned.txt
RUN pip install -r requirements_versioned.txt \
    pip install Cython  \
    cd /usr/local/lib/python3.8/site-packages/resipy/ \
    python setup.py build_ext --inplace  \
    cd /app

# Run main.py when the container launches
CMD ["python", "./main.py"]