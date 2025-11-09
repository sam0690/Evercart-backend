from rest_framework import serializers
from .models import Category, Product, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "image", "alt_text")

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ("id", "title", "slug", "description", "price", "inventory", "category", "images")


class ProductAdminWriteImageSerializer(serializers.Serializer):
    image = serializers.CharField(max_length=500)
    alt_text = serializers.CharField(max_length=255, required=False, allow_blank=True)
    is_primary = serializers.BooleanField(required=False)


class ProductAdminSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    images = ProductAdminWriteImageSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ("id", "title", "slug", "description", "price", "inventory", "category", "images")

    def _ensure_slug(self, validated_data):
        from django.utils.text import slugify
        title = validated_data.get("title")
        slug = validated_data.get("slug")
        if not slug and title:
            validated_data["slug"] = slugify(title)
        return validated_data

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        validated_data = self._ensure_slug(validated_data)
        product = Product.objects.create(**validated_data)
        for img in images_data:
            ProductImage.objects.create(
                product=product,
                image=img.get("image"),
                alt_text=img.get("alt_text", ""),
                is_primary=img.get("is_primary", False),
            )
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", None)
        validated_data = self._ensure_slug(validated_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if images_data is not None:
            # Replace existing images with provided set
            instance.images.all().delete()
            for img in images_data:
                ProductImage.objects.create(
                    product=instance,
                    image=img.get("image"),
                    alt_text=img.get("alt_text", ""),
                    is_primary=img.get("is_primary", False),
                )
        return instance

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")
