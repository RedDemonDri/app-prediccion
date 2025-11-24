from django.db import migrations


def forwards_replace_default(apps, schema_editor):
    Metric = apps.get_model('dashboard', 'Metric')
    MetricCategory = apps.get_model('dashboard', 'MetricCategory')

    # Aseguramos que exista una categoría llamada 'default'
    cat, created = MetricCategory.objects.get_or_create(name='default', defaults={'description': 'Creada por migración para reemplazar valor "default" en category_id'})

    # Reemplazamos valores literales 'default' en category_id por el id entero de la categoría creada
    table = Metric._meta.db_table
    with schema_editor.connection.cursor() as cursor:
        # SQLite y otros permiten comparar texto; usamos parámetros seguros
        cursor.execute(f"UPDATE {table} SET category_id = %s WHERE category_id = %s", [cat.pk, 'default'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_metriccategory_alter_metric_options_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards_replace_default, reverse_code=noop_reverse),
    ]
