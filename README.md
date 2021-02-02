# random-recommendation
docker build -t recommendation:latest .
docker run -it -p 5000:5000 -v "/local/directory/for/trained_models:/app/trained_models" -e TZBACKEND_URL=url_for_tzbackend recommendation