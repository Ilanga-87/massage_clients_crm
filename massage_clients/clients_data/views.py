from django.shortcuts import render

from django.shortcuts import render, redirect
from .forms import ClientForm


def create_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')  # Replace 'success' with the URL name for your success page
    else:
        form = ClientForm()

    return render(request, 'your_template.html', {'form': form})

