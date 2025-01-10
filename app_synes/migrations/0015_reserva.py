# Generated by Django 5.1.3 on 2025-01-10 15:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_synes', '0014_alter_jogo_horario'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField()),
                ('horario_inicio', models.TimeField()),
                ('horario_fim', models.TimeField()),
                ('arena', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_synes.arena')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]