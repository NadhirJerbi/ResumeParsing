query = """ ` text into JSON following the specified template. Ensure the output strictly adheres to the structure outlined below. If a section is empty, leave the corresponding fields as empty strings or arrays:

{
  "Name": "",
  "Job_title": "",
  "Email": "",
  "Phone": "",
  "Location": "",
  "Other_contact": [
    {
      "contact_type": "",
      "link": ""
    }
  ],
  "Profile": "",
  "Experience": [
    {
      "job_title": "",
      "company": "",
      "description": "",
      "skills": [],
      "start_date": "",
      "end_date": "",
      "location": ""
    }
  ],
  "Education": [
    {
      "degree": "",
      "major": "",
      "school": "",
      "location": "",
      "graduation_date": ""
    }
  ],
  "Projects": [
    {
      "project_title": "",
      "description": "",
      "skills": []
    }
  ],
  "Skills": [],
  "Certificates": [],
  "Languages": [
    {
      "language": "",
      "level": ""
    }
  ],
  "Interests": [],
  "Achievement": [],
  "References": [],
  "Community": []
}
Provide the response as a JSON text without any additional content.
"""