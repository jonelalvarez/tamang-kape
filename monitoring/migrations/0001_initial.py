# Generated by Django 4.2.19 on 2025-05-05 15:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CaffeineProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drinkName', models.CharField(max_length=255)),
                ('volumeML', models.IntegerField()),
                ('calorie', models.IntegerField()),
                ('caffeine', models.DecimalField(decimal_places=2, max_digits=5)),
                ('category', models.CharField(max_length=100)),
                ('type', models.IntegerField()),
                ('status', models.BooleanField(default=True)),
                ('flOz', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('mgPerFlOz', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('mgPer100ml', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='HealthTip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('detail', models.TextField()),
                ('link', models.CharField(blank=True, max_length=500, null=True)),
                ('category', models.CharField(max_length=100)),
                ('tip', models.TextField()),
                ('icon_name', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField(blank=True, null=True)),
                ('bDate', models.DateField(blank=True, null=True)),
                ('health_condition', models.CharField(choices=[('none', 'None'), ('pregnant', 'Pregnant'), ('lactating', 'Lactating'), ('heart', 'Heart Condition'), ('hypertension', 'Hypertension'), ('diabetes', 'Diabetes')], default='none', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CreatedDrink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drinkName', models.CharField(max_length=255)),
                ('volumeML', models.IntegerField(blank=True, null=True)),
                ('caffeine', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('mgPer100ml', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('category', models.CharField(max_length=100)),
                ('measurementMethod', models.CharField(blank=True, max_length=50, null=True)),
                ('status', models.BooleanField(default=True)),
                ('is_created', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CaffeineIntake',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drink_name', models.CharField(max_length=255)),
                ('caffeine_amount', models.FloatField()),
                ('serving_size', models.FloatField(blank=True, null=True)),
                ('timestamp', models.DateTimeField()),
                ('drink_id', models.IntegerField(blank=True, null=True)),
                ('categoryType', models.CharField(blank=True, max_length=100, null=True)),
                ('is_created', models.BooleanField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
