import random, zipfile
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

domains = ["software_engineering", "marketing", "finance"]
levels = {"entry":7, "mid":7, "senior":6}
skills_pool = {
    "software_engineering": ["Python","Java","C++","SQL","Git","Docker","AWS","React"],
    "marketing": ["SEO","Content Marketing","Google Ads","Social Media","CRM"],
    "finance": ["Excel","Power BI","Accounting","Forecasting","Auditing"]
}

def make_pdf(text, path):
    c = canvas.Canvas(str(path), pagesize=letter)
    t = c.beginText(40, 750)
    t.setFont("Helvetica", 10)
    for line in text.split("\n"):
        t.textLine(line)
    c.drawText(t)
    c.save()

def make_resume(domain, level):
    name = random.choice(["Alex","Jordan","Taylor","Sam"]) + " " + random.choice(["Smith","Patel","Lee","Garcia"])
    summary = f"{level.capitalize()} professional in {domain.replace('_',' ')}."
    skills = ", ".join(random.sample(skills_pool[domain], min(5, len(skills_pool[domain]))))
    return f"{name}\n\nSUMMARY\n{summary}\n\nSKILLS\n{skills}\n\nEDUCATION\nBachelors Degree\n\nEXPERIENCE\nDetails here."

out = Path("resumes_dataset"); out.mkdir(exist_ok=True)
created = []
for d in domains:
    for l, n in levels.items():
        folder = out / d / f"{l}_level"
        folder.mkdir(parents=True, exist_ok=True)
        for i in range(1, n+1):
            pdf_path = folder / f"{d.replace('_','')}_{l}_{i:02d}.pdf"
            make_pdf(make_resume(d, l), pdf_path)
            created.append(pdf_path)

with zipfile.ZipFile("resumes_dataset.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for f in created: z.write(f, arcname=str(f.relative_to(out)))
print("✅ Created resumes_dataset.zip with", len(created), "PDFs.")