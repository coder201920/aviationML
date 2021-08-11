# Generated by Django 3.2.5 on 2021-07-30 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aviationapp', '0002_auto_20210730_0531'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='airports',
            name='ids',
        ),
        migrations.AddField(
            model_name='airports',
            name='home_link',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='airports',
            name='keywords',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='airports',
            name='wikipedia_link',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='airports',
            name='id',
            field=models.CharField(max_length=10, primary_key=True, serialize=False),
        ),
    ]
