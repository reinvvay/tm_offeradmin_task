import csv
import os

from django import forms
from django.contrib import admin, messages
from django.contrib.admin import action
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.html import format_html

from offersAdmin.settings.base import MEDIA_ROOT

from .models import (Offer, OfferChoices, OfferWall, OfferWallOffer,
                     OfferWallPopupOffer)


def authenticated_only(view):
    def wrapper(_, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponse("You are not authenticated", status=401)
        return view(_, request, *args, **kwargs)

    return wrapper


class OfferWallOfferInline(admin.TabularInline):
    model = OfferWallOffer
    extra = 0
    ordering = ["order"]
    template = "admin/offerwalloffer_inline.html"


class OfferWallPopupOfferInline(admin.TabularInline):
    model = OfferWallPopupOffer
    extra = 0
    ordering = ["order"]
    template = "admin/offerwalloffer_inline.html"


@admin.register(OfferWall)
class OfferWallAdmin(admin.ModelAdmin):
    list_display = ("name", "token", "url_link", "description_preview")
    search_fields = ("token", "url", "description")
    ordering = ("name",)
    readonly_fields = ("token",)
    inlines = [OfferWallOfferInline, OfferWallPopupOfferInline]

    def url_link(self, obj):
        if obj.url:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.url, obj.url)
        return "—"

    url_link.short_description = "URL"
    url_link.admin_order_field = "url"

    def description_preview(self, obj):
        if len(obj.description) > 50:
            return f"{obj.description[:50]}..."
        return obj.description

    description_preview.short_description = "Description"
    description_preview.admin_order_field = "description"


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
    input_formats = {"accept": ".png"}


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class AddImagesForm(forms.Form):
    images = MultipleFileField(
        label="Select files",
        required=True,
    )


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("name", "offer_image", "url_link", "is_active")
    list_filter = ("name", "is_active")
    search_fields = ("uuid", "name", "url")
    readonly_fields = ("uuid",)
    list_editable = ("is_active",)

    # Add the import_csv to change_list template
    change_list_template = "admin/offer_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("import-csv/", self.import_csv, name="offer_import_csv"),
            path("add-images/", self.add_images, name="offer_add_images"),
        ]
        return custom_urls + urls

    @authenticated_only
    def import_csv(self, request):
        if request.method == "POST":
            form = CSVImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES["csv_file"]

                # Check if file is CSV
                if not csv_file.name.endswith(".csv"):
                    messages.error(request, "Please upload a CSV file.")
                    return HttpResponseRedirect(request.path_info)

                # Read and decode the CSV file
                try:
                    decoded_file = csv_file.read().decode("utf-8").splitlines()
                    reader = csv.DictReader(decoded_file)

                    # Validate required fields
                    required_fields = {
                        "id",
                        "name",
                        "sum_to",
                        "term_to",
                        "percent_rate",
                        "status",
                        "url",
                    }
                    if not all(field in reader.fieldnames for field in required_fields):
                        missing_fields = required_fields - set(reader.fieldnames)
                        messages.error(
                            request,
                            f"CSV is missing required fields.\nMissing fields: {missing_fields}",
                        )
                        return HttpResponseRedirect(request.path_info)
                    # Process each row
                    choices = [choice[1] for choice in OfferChoices.choices]
                    for row in reader:
                        try:
                            # Convert status to boolean
                            status = row["status"].lower() == "true"
                            if row["name"] not in choices:
                                messages.warning(
                                    request,
                                    f'Invalid offer name in row {row["id"]}: {row["name"]}',
                                )
                                continue

                            # Create or update Offer object
                            # Note: Assuming your Offer model has these fields
                            offer, created = self.model.objects.update_or_create(
                                name=row["name"],
                                defaults={
                                    "id": int(row["id"]),
                                    "sum_to": row["sum_to"],
                                    "term_to": int(row["term_to"]),
                                    "percent_rate": int(row["percent_rate"]),
                                    "is_active": status,
                                    # Add url if it exists in CSV, otherwise set as empty
                                    "url": row.get("url", ""),
                                },
                            )
                        except (ValueError, KeyError) as e:
                            messages.warning(
                                request, f'Error in row {row["id"]}: {str(e)}'
                            )
                            continue

                    messages.success(
                        request, "CSV file has been imported successfully!"
                    )
                    return redirect("..")

                except Exception as e:
                    messages.error(request, f"Error processing file: {str(e)}")
                    return HttpResponseRedirect(request.path_info)

        # If GET request or form invalid, show the form
        form = CSVImportForm()
        return render(
            request,
            "admin/core/offer/csv_import.html",
            {"form": form, "title": "Import CSV"},
        )

    def url_link(self, obj):
        if obj.url:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.url, obj.url)
        return "—"

    url_link.short_description = "Redirect URL"

    def offer_image(self, obj):
        return format_html(
            '<img src="{}" alt="Offer Image" style="max-width: 100px; max-height: 100px;">',
            "/media/offers/" + obj.name + ".png",
        )

    offer_image.short_description = "Offer Image"

    @authenticated_only
    def add_images(self, request):
        if request.method == "POST":
            form = AddImagesForm(request.POST, request.FILES)
            if form.is_valid():
                images = request.FILES.getlist("images")
                clean_images = []
                try:
                    for image in images:
                        image: TemporaryUploadedFile
                        if image.name.endswith(".png"):
                            clean_images.append(image)
                        else:
                            messages.error(
                                request,
                                f"Invalid image file: {image.name}. Only PNG files are allowed.",
                            )
                    for clean_image in clean_images:
                        img_path = os.path.join(MEDIA_ROOT, "offers", clean_image.name)
                        if os.path.exists(img_path):
                            os.remove(img_path)
                        FileSystemStorage(location="media/offers").save(
                            clean_image.name,
                            clean_image,
                        )
                    messages.success(request, "Images have been added successfully!")
                    return redirect("..")

                except Exception as e:
                    messages.error(request, f"Error processing file: {str(e)}")
                    return HttpResponseRedirect(request.path_info)
            errors = list(
                str(error)
                .replace('<ul class="errorlist"><li>', "")
                .replace("</li></ul>", "")
                for error in dict(form.errors).values()
            )
            messages.error(request, format_html("\n".join(error for error in errors)))
        # If GET request or form invalid, show the form
        form = AddImagesForm()
        return render(
            request,
            "admin/core/offer/add_images.html",
            {"form": form, "title": "Add offer images"},
        )

    # Actions
    @action(description="Remove from all offerwalls")
    def remove_from_all_offerwalls(self, request, queryset):
        offer_wall_offers = OfferWallOffer.objects.filter(offer__in=queryset)
        count = offer_wall_offers.count()
        offer_wall_offers.delete()
        self.message_user(
            request,
            f"Removed {count} offers from all offerwalls.",
        )

    @action(description="Activate selected offers")
    def activate(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(
            request,
            f"Activated {count} offers.",
        )

    @action(description="Deactivate selected offers")
    def deactivate(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(
            request,
            f"Deactivated {count} offers.",
        )

    actions = ["activate", "deactivate", "remove_from_all_offerwalls"]
