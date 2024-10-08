# Generated by Django 5.0.7 on 2024-07-26 09:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="image_filter",
            field=models.CharField(
                choices=[
                    ("_1977", "1977"),
                    ("brannan", "Brannan"),
                    ("earlybird", "Earlybird"),
                    ("hudson", "Hudson"),
                    ("inkwell", "Inkwell"),
                    ("lofi", "Lo-Fi"),
                    ("kelvin", "Kelvin"),
                    ("normal", "Normal"),
                    ("nashville", "Nashville"),
                    ("rise", "Rise"),
                    ("toaster", "Toaster"),
                    ("valencia", "Valencia"),
                    ("walden", "Walden"),
                    ("xpro2", "X-pro II"),
                ],
                default="normal",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="owner",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="image",
            field=models.ImageField(
                blank=True, default="../default_product_cjfapy", upload_to="products/"
            ),
        ),
    ]
