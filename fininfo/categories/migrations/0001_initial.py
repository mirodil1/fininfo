# Generated by Django 4.2.11 on 2025-07-20 15:25

from django.db import migrations, models
import django.db.models.deletion
import parler.fields
import parler.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratildi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name="O'zgartirildi")),
                ('is_menu', models.BooleanField(default=False, verbose_name='Menyu')),
                ('category_order', models.PositiveIntegerField(db_index=True, default=0)),
                ('icon', models.FileField(blank=True, null=True, upload_to='category/icons', verbose_name='Ikonka')),
                ('image', models.ImageField(blank=True, null=True, upload_to='category/images', verbose_name='Rasm')),
            ],
            options={
                'verbose_name': "Bo'lim",
                'verbose_name_plural': "Bo'limlar",
                'ordering': ['category_order'],
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CategoryTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=64, verbose_name='Nomi')),
                ('slug', models.SlugField(max_length=64, verbose_name='Slug')),
                ('description', models.TextField(blank=True, null=True, verbose_name="Ta'rif")),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='categories.category')),
            ],
            options={
                'verbose_name': "Bo'lim Translation",
                'db_table': 'categories_category_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master'), ('slug', 'language_code')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
