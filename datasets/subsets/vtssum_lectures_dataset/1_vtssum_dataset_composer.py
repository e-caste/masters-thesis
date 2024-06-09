from common import *

import json
from glob import glob
from tqdm import tqdm


def main(transcripts_only: bool = True):
    lectures = []

    for directory in ("train", "dev", "test"):
        json_files = glob(f"{dataset_path}/{directory}/*.json")

        for json_file in tqdm(json_files, desc=f"Reading and modifying in-memory all files in {directory}"):
            contents = json.load(open(json_file, "r"))

            clips = [clip for k, clip in contents['summarization'].items()]
            contents['summarization'] = clips  # now a list instead of a dict

            # remove data that has been excluded from the summarization due to too few words (< 10) in the reference slide used as weak supervision
            exclude_from_summarization_indices = [i for i, clip in enumerate(clips) if
                                                  clip['is_summarization_sample'] is False]
            contents['summarization'] = [el for i, el in enumerate(contents['summarization']) if
                                         i not in exclude_from_summarization_indices]
            contents['segmentation'] = [el for i, el in enumerate(contents['segmentation']) if
                                        i not in exclude_from_summarization_indices]

            # clean out segmentation data, concatenate all sentences within a segment
            for i, segment in enumerate(contents['segmentation']):
                contents['segmentation'][i] = " ".join(segment)

            # clean out summarization data, concatenate all sentences labeled with 1
            for i, _ in enumerate(contents['summarization']):
                del contents['summarization'][i]['is_summarization_sample']  # we have already used this field
                contents['summarization'][i] = " ".join(
                    [datum['sent']
                     for datum in contents['summarization'][i]['summarization_data']
                     if datum['label'] == 1]
                )

            lecture = {
                'title': contents['title'],
                'url': contents['url'],
                text_column: " ".join(contents['segmentation']),
            }

            if not transcripts_only:
                lecture[summary_column] = " ".join(contents['summarization'])

            lectures.append(lecture)

    print(f"{len(lectures)} lectures.")
    update_dataset(lectures, transcripts_only=transcripts_only)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting...")
        exit()
