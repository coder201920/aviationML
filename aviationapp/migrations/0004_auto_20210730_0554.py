# Generated by Django 3.2.5 on 2021-07-30 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aviationapp', '0003_auto_20210730_0552'),
    ]

    operations = [
        migrations.AddField(
            model_name='airports',
            name='ids',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='airports',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
