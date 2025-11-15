from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_order_is_paid_order_shipping_address_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="shipping_phone",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
