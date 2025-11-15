from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_order_shipping_phone"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="transaction_uuid",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
