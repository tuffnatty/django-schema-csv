import csv
import re

from django.contrib.postgres.fields import JSONField
from django.core.management.base import AppCommand
from django.db import connection
from django.db.models.fields.related import (
    ManyToOneRel, ManyToManyRel, ManyToManyField,
)


def fix(s):
    return re.sub(r'\s', ' ', s).encode('UTF-8')


class Command(AppCommand):
    def handle_app_config(self, app_config, **options):
        fieldnames = ['num', 'name', 'type', 'description']
        with open('%s_models.csv' % app_config.label, 'w') as out:
            writer = csv.DictWriter(out, fieldnames=fieldnames)
            writer.writeheader()
            for model in app_config.get_models(include_auto_created=True):
                writer.writerow({
                    'num': '--',
                    'name': model._meta.db_table,
                    'description': fix(model._meta.verbose_name),
                })
                for i, f in enumerate(p for p in model._meta.get_fields()
                                      if not isinstance(p, (ManyToOneRel,
                                                            ManyToManyField,
                                                            ManyToManyRel))):
                    if isinstance(f, JSONField):
                        t = 'jsonb'
                    else:
                        t = f.db_type(connection) or ('!' + str(type(f)))
                    writer.writerow({
                        'num': i + 1,
                        'name': f.name,
                        'type': t,
                        'description': fix(getattr(f, 'verbose_name', '')),
                    })
                for i, f in enumerate(p for p in model._meta.get_fields()
                                      if isinstance(p, ManyToManyField)):
                    writer.writerow({
                        'name':
                            f.db_table or f.m2m_db_table() or str(f.__dict__),
                        'description': fix(getattr(f, 'verbose_name', '')),
                    })
