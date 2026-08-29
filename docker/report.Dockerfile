FROM python:3.11-slim

# Dependances systeme de WeasyPrint (rendu Pango/Cairo), polices, et pandoc
# pour la generation de la version Word.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b \
        libjpeg62-turbo libopenjp2-7 libffi8 \
        fonts-dejavu fonts-liberation \
        pandoc \
    && rm -rf /var/lib/apt/lists/*

# pydyf doit etre epingle : WeasyPrint 62.3 appelle une API que pydyf 0.12 a
# supprimee (AttributeError sur Stream.transform). Meme lecon que pour dbt :
# une dependance non bornee casse la reproductibilite.
RUN pip install --no-cache-dir \
        weasyprint==62.3 \
        pydyf==0.11.0 \
        markdown==3.7

WORKDIR /work
CMD ["python", "docs/build_report.py"]
