# Generated by Django 2.1.11 on 2019-11-19 06:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lmn', '0003_note_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='rating',
            field=models.IntegerField(blank=True, choices=[(None, 'N/A'), (0, '☆☆☆☆☆'), (1, '☆☆☆☆★'), (2, '☆☆☆★★'), (3, '☆☆★★★'), (4, '☆★★★★'), (5, '★★★★★')], default=None, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)]),
        ),
    ]