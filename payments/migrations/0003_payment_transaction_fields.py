from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0002_alter_payment_method"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="transaction_uuid",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="payment",
            name="product_code",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
