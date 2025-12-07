from django.shortcuts import render
from .forms import ResumeForm, JobDescriptionForm
from .models import Resume, ATSAnalysis
from .utils import calculate_ats_score

def score_resume(request):
    if request.method == 'POST' and request.FILES.get('uploaded_resume'):
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save()
            ats_score = calculate_ats_score(resume.uploaded_resume)
            resume.ats_score = ats_score
            resume.save()
            ATSAnalysis.objects.create(
                resume=resume, score=ats_score, analysis_text="Overall ATS analysis."
            )
            return render(request, 'resume/result.html', {'score': ats_score, 'resume': resume})
    else:
        form = ResumeForm()
    return render(request, 'resume/upload.html', {'form': form})

def job_based_ats(request):
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = form.cleaned_data['uploaded_resume']
            job_description = form.cleaned_data['job_description']
            ats_score = calculate_ats_score(resume_file, job_description)
            return render(request, 'resume/job_description_result.html', {
                'score': ats_score,
                'job_description': job_description,
            })
    else:
        form = JobDescriptionForm()
    return render(request, 'resume/job_based_ats.html', {'form': form})
