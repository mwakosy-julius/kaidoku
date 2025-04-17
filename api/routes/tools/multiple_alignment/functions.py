import requests
import time

def align_view(request):
    if request.method == "POST":
        sequences = request.POST.get("sequences")
        seq_type = request.POST.get("seq_type")
        url = "https://www.ebi.ac.uk/Tools/services/rest/clustalo/run"
        data = {"email": "your.email@example.com", "sequence": sequences, "stype": seq_type}
        job_id = requests.post(url, data=data).text
        status_url = f"https://www.ebi.ac.uk/Tools/services/rest/clustalo/status/{job_id}"
        while requests.get(status_url).text == "RUNNING":
            time.sleep(5)
        result_url = f"https://www.ebi.ac.uk/Tools/services/rest/clustalo/result/{job_id}/aln-clustal_num"
        alignment = requests.get(result_url).text
        return render(request, "align/result.html", {"alignment": alignment})
    return render(request, "align/form.html")