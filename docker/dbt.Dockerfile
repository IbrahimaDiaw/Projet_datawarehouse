FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Versions figees a l'exact : le correcteur obtient rigoureusement le meme
# environnement, ce qui est l'argument central de reproductibilite du projet.
# Remarque : dbt-postgres ne borne pas dbt-core, sans epinglage pip installe
# la preversion 2.0 (moteur "Fusion") qui ne supporte pas encore PostgreSQL.
RUN pip install --no-cache-dir dbt-core==1.12.3 dbt-postgres==1.11.0

WORKDIR /usr/app
ENTRYPOINT ["dbt"]
CMD ["--version"]
