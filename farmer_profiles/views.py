from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import UserRole
from .models import FarmerProfile
from .forms import FarmerProfileForm, FarmerCropFormSet

@login_required
def dashboard(request):
    # Enforce role
    if request.user.role != UserRole.FARMER:
        return redirect("admin:index")

    try:
        profile = request.user.profile
    except FarmerProfile.DoesNotExist:
        # If no profile exists, send them to complete it
        return redirect("profile_edit")

    # If profile exists but onboarding isn't finished
    if not profile.is_completed:
        messages.info(request, "Please complete your profile to see personalized recommendations.")
        return redirect("profile_edit")

    context = {
        "profile": profile,
        "crops": profile.crops.all(),
    }
    return render(request, "farmer_profiles/dashboard.html", context)

@login_required
def profile_edit(request):
    if request.user.role != UserRole.FARMER:
        return redirect("admin:index")

    # Get or create a profile for this user
    profile, created = FarmerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = FarmerProfileForm(request.POST, instance=profile)
        formset = FarmerCropFormSet(request.POST, instance=profile)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            
            # Mark profile as completed if essential fields are filled
            if profile.state and profile.district and profile.landholding_acres is not None:
                profile.is_completed = True
                profile.save()
                messages.success(request, "Profile updated successfully!")
                return redirect("dashboard")
            else:
                messages.warning(request, "Profile saved, but please fill state, district, and landholding to complete onboarding.")
    else:
        form = FarmerProfileForm(instance=profile)
        formset = FarmerCropFormSet(instance=profile)

    return render(request, "farmer_profiles/profile_form.html", {
        "form": form,
        "formset": formset,
    })