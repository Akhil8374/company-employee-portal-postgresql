# HRMS Testing Guide

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Migrations

```bash
python manage.py migrate
```

## Execute All Tests

```bash
python manage.py test
```

## Run Coverage

```bash
coverage run manage.py test
```

## Coverage Report

```bash
coverage report
```

## HTML Coverage

```bash
coverage html
```

Open

```
htmlcov/index.html
```

## Fixtures

```bash
python manage.py loaddata fixtures/departments.json
python manage.py loaddata fixtures/users.json
python manage.py loaddata fixtures/employees.json
```