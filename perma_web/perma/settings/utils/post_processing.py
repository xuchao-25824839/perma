### settings post-checks
# here we do stuff that should be checked or fixed after ALL settings from any source are loaded
# this is called by __init__.py

from celery.schedules import crontab

def post_process_settings(settings):

    # check secret key
    assert 'SECRET_KEY' in settings and settings['SECRET_KEY'] is not None, "Set DJANGO__SECRET_KEY env var!"

    # Deal with custom setting for CELERY_TASK_DEFAULT_QUEUE.
    # Changing CELERY_TASK_DEFAULT_QUEUE only changes the queue name,
    # but we need it to change the exchange and routing_key as well.
    # See http://celery.readthedocs.org/en/latest/userguide/routing.html#changing-the-name-of-the-default-queue
    try:
        default_queue = settings['CELERY_TASK_DEFAULT_QUEUE']
        if default_queue != "celery":
            from kombu import Exchange, Queue
            settings['CELERY_TASK_QUEUES'] = (Queue(default_queue, Exchange(default_queue), routing_key=default_queue),)
    except KeyError:
        # no custom setting for CELERY_TASK_DEFAULT_QUEUE
        pass

    # add the named celerybeat jobs
    celerybeat_job_options = {
        # primary server
        'update-stats': {
            'task': 'perma.tasks.update_stats',
            'schedule': crontab(minute='*'),
        },
        'send-links-to-internet-archives': {
            'task': 'perma.tasks.upload_all_to_internet_archive',
            'schedule': crontab(minute='0', hour='*'),
        },
        'cm-sync': {
            'task': 'perma.tasks.cm_sync',
            'schedule': crontab(hour='3'),
        },
        'send-js-errors': {
            'task': 'perma.tasks.send_js_errors',
            'schedule': crontab(hour='10', minute='0', day_of_week=1)
        },
        'run-next-capture': {
            'task': 'perma.tasks.run_next_capture',
            'schedule': crontab(minute='*'),
        }
    }
    settings['CELERY_BEAT_SCHEDULE'] = dict(((job, celerybeat_job_options[job]) for job in settings.get('CELERYBEAT_JOB_NAMES', [])),
                                           **settings.get('CELERY_BEAT_SCHEDULE', {}))
