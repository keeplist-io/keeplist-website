FROM python:3.12.4-alpine

ARG BUILD_ENVIRONMENT=prod
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}
ARG APP_HOME=/app
WORKDIR ${APP_HOME}

ENV DJANGO_SETTINGS_MODULE="a_core.settings-prod"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN addgroup --system django \
  && adduser --system --ingroup django django

# Make entrypoint executable
COPY --chown=django:django ./docker/prod/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//g' /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY --chown=django:django ./docker/prod/start.sh /start.sh
RUN sed -i 's/\r$//g' /start.sh
RUN chmod +x /start.sh


COPY --chown=django:django . ${APP_HOME}
RUN chown django:django ${APP_HOME}
USER django

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]

