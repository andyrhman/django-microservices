from django.core.management.base import BaseCommand
from django.db import transaction

from core.old_models      import OldCategory, OldProduct
from core.category_models import Category
from core.models          import Product, ProductImages, ProductVariation

class Command(BaseCommand):
    help = "Seed Product-MS from old monolith, remapping via Category-MS DB"

    def handle(self, *args, **opts):
        self.stdout.write("⏳ Fetching categories from Category-MS…")
        cat_map = {}
        for cat in Category.objects.all():
            cat_map[cat.name] = cat.id
            self.stdout.write(f"  • {cat.name} → {cat.id}")

        old_qs = OldProduct.objects.using('old_data').all()
        old_product_images = ProductImages.objects.using('old_data').all()       
        old_product_variants = ProductVariation.objects.using('old_data').all()
         
        total  = old_qs.count()
        self.stdout.write(f"⏳ Importing {total} products…")

        with transaction.atomic():
            for old in old_qs:
                old_cat = OldCategory.objects.using('old_data').get(id=old.category_id)
                new_cat_id = cat_map.get(old_cat.name)
                if not new_cat_id:
                    self.stderr.write(f"⚠️  No new Category for “{old_cat.name}”: skipping {old.title}")
                    continue

                product = Product.objects.create(
                    title       = old.title,
                    slug        = old.slug,
                    description = old.description,
                    image       = old.image,
                    price       = old.price,
                    category    = new_cat_id,
                )

                for img in old_product_images.filter(product_id=old.id):
                    ProductImages.objects.create(
                        product=product,
                        name=img.name
                    )

                for var in old_product_variants.filter(product_id=old.id):
                    ProductVariation.objects.create(
                        product=product,
                        name=var.name
                    )

                self.stdout.write(f"  ✓ {old.title}")

        self.stdout.write(self.style.SUCCESS(f"✅ Imported {total} products!"))
