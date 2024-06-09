import json

from common import *


def main():
    mitocw_courses = json.load(open(mitocw_dataset_file, "r"))
    yale_courses = json.load(open(yale_dataset_file, "r"))

    courses = []
    for c in mitocw_courses:
        lectures = c['lectures']
        del c['lectures']  # put 'from_subset' at the top
        c['from_subset'] = "mitocw"
        c['lectures'] = lectures
        courses.append(c)
    for c in yale_courses:
        lectures = c['lectures']
        del c['lectures']  # put 'from_subset' at the top
        c['from_subset'] = "yale"
        c['lectures'] = lectures
        courses.append(c)

    with open(aggregated_dataset_file, "w") as f:
        json.dump(courses, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting...")
        exit()
