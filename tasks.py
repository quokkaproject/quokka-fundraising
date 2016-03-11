# coding: utf-8

import logging
from quokka import create_celery_app

celery = create_celery_app()
logger = logging.getLogger(__name__)


@celery.task
def fundraising_task():
    logging.info("Doing something async...")
