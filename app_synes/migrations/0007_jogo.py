# Generated by Django 5.1.3 on 2025-01-09 11:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_synes', '0006_alter_arena_options_alter_arena_usuario'),
    ]

    operations = [
        migrations.CreateModel(
            name='Jogo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('descricao', models.TextField()),
                ('data', models.DateField()),
                ('horario', models.TimeField()),
                ('max_jogadores', models.IntegerField(verbose_name='Quantidade máxima de jogadores')),
                ('arena', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jogos', to='app_synes.arena')),
            ],
        ),
    ]