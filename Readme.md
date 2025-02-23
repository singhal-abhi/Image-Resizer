celery -A my_project_name worker --pool=solo -l info
uvicorn main:app --reload