# Generated by Django 4.2.11 on 2024-12-07 09:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fire', '0003_incident_incident_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='weatherconditions',
            name='wind_direction',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='incident',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fire.locations'),
        ),
        migrations.AlterField(
            model_name='incident',
            name='status',
            field=models.CharField(choices=[('Active', 'Active'), ('Resolve', 'Resolve')], default='Active', max_length=45),
        ),
    ]