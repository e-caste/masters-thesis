from common import *

import json
from sys import stderr

n_tildes = 80

try:
    with open(course_download_urls_file, "r") as f:
        courses_download_urls = json.load(f)
except FileNotFoundError:
    print("Please run 1_openhpi_video_slides_and_transcript_urls_scraper.py first.", file=stderr)
    exit(-1)

n_courses = len(courses_download_urls)
total_lectures = sum([len(courses_download_urls[c]) for c in courses_download_urls])
avg_lectures_per_course = total_lectures / n_courses

courses_in_lectures = sorted([(c, len(courses_download_urls[c]))
                              for c in courses_download_urls],
                             key=lambda x: x[1],
                             reverse=True)

total_lectures_with_transcript = sum([1
                                      for course in courses_download_urls
                                      for lecture in courses_download_urls[course]
                                      if courses_download_urls[course][lecture]['transcript'] is not None])
full_courses_with_transcript = [c for c in courses_download_urls
                                if all(courses_download_urls[c][l]['transcript'] is not None
                                       for l in courses_download_urls[c])]

total_lectures_with_slides = sum([1
                                  for course in courses_download_urls
                                  for lecture in courses_download_urls[course]
                                  if any(mat_url.endswith(".pdf") # or mat_url.endswith(".ppt") or mat_url.endswith(".pptx")
                                         for mat_url in courses_download_urls[course][lecture]['material'])])
full_courses_with_slides = [c for c in courses_download_urls
                            if all([any(mat_url.endswith(".pdf") or mat_url.endswith(".ppt") or mat_url.endswith(".pptx")
                                        for mat_url in courses_download_urls[c][l]['material'])
                                    for l in courses_download_urls[c]])]

total_lectures_with_transcript_and_slides = sum([1
                                                 for course in courses_download_urls
                                                 for lecture in courses_download_urls[course]
                                                 if courses_download_urls[course][lecture]['transcript'] is not None
                                                 and any(mat_url.endswith(".pdf") # or mat_url.endswith(".ppt") or mat_url.endswith(".pptx")
                                                         for mat_url in courses_download_urls[course][lecture]['material'])])
full_courses_with_transcript_and_slides = [c for c in full_courses_with_transcript if c in full_courses_with_slides]

print(f"Number of courses with downloadable material: {n_courses}")
print(f"for a total of {total_lectures} lectures")
print(f"with an average of {avg_lectures_per_course:.2f} lectures per course.")
print("~" * n_tildes)
print(f"Longest course: {courses_in_lectures[0][0]} with {courses_in_lectures[0][1]} lectures.")
print(f"Shortest course: {courses_in_lectures[-1][0]} with {courses_in_lectures[-1][1]} lectures.")
print("~" * n_tildes)
print(f"Number of lectures with a transcript: {total_lectures_with_transcript} "
      f"({total_lectures_with_transcript / total_lectures * 100:.2f}%)")
print(f"Number of full courses with a transcript: {len(full_courses_with_transcript)} "
      f"({len(full_courses_with_transcript) / n_courses * 100:.2f}%) -- {', '.join(full_courses_with_transcript)}")
print("~" * n_tildes)
print(f"Number of lectures with downloadable slides: {total_lectures_with_slides} "
      f"({total_lectures_with_slides / total_lectures * 100:.2f}%)")
print(f"Number of full courses with slides: {len(full_courses_with_slides)} "
      f"({len(full_courses_with_slides) / n_courses * 100:.2f}%) -- {', '.join(full_courses_with_slides)}")
print("~" * n_tildes)
print(f"Number of lectures with a transcript and downloadable slides: {total_lectures_with_transcript_and_slides} "
      f"({total_lectures_with_slides / total_lectures * 100:.2f}%)")
print(f"Number of full courses with a transcript and slides: {len(full_courses_with_transcript_and_slides)} "
      f"({len(full_courses_with_transcript_and_slides) / n_courses * 100:.2f}%) -- {', '.join(full_courses_with_transcript_and_slides)}")

"""as of 11/12/2022
Number of courses with downloadable material: 45
for a total of 1571 lectures
with an average of 34.91 lectures per course.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Longest course: hpi-learningatscale2021-emoocs2021 with 94 lectures.
Shortest course: startup-talks with 9 lectures.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Number of lectures with a transcript: 1076 (68.49%)
Number of full courses with a transcript: 18 (40.00%) -- malware2022, identities2022, confidentialcommunication2022, processmining2021, digital_entrepreneurship2021, cleanit2021, blockchain2021, malware2021, identities2021, confidentialcommunication2021, knowledgegraphs2020, prototype2019, bpm2019, designthinking2019, ibmpower2019, ideas2018, qc-qiskit2022, edgeai2022
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Number of lectures with downloadable slides: 1132 (72.06%)
Number of full courses with slides: 14 (31.11%) -- malware2022, identities2022, confidentialcommunication2022, processmining2021, blockchain2021, knowledgegraphs2020, learningtheory2020, semanticweb2017, intsec2018, ws-privacy2017, ws-privacy2016, semanticweb2015, softwareanalytics2015, edgeai2022
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Number of lectures with a transcript and downloadable slides: 773 (72.06%)
Number of full courses with a transcript and slides: 7 (15.56%) -- malware2022, identities2022, confidentialcommunication2022, processmining2021, blockchain2021, knowledgegraphs2020, edgeai2022
"""