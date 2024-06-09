import json

dataset_path = "./VT-SSum"

data_path = "."
dataset_file = f"{data_path}/vtssum_lectures_dataset.json"
transcripts_only_dataset_file = f"{data_path}/vtssum_lectures_dataset_transcripts_only.json"

text_column = "transcript"
summary_column = "description"


def update_dataset(lectures, transcripts_only=False):
    with open(transcripts_only_dataset_file if transcripts_only else dataset_file, mode="w") as f:
        json.dump(lectures, f, indent=4, ensure_ascii=False)
