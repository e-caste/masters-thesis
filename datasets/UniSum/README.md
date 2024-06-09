## UniSum Dataset
University Summarization

To make the UniSum dataset CSV files from the 2 available subsets, first complete all the steps required for each of them, then run the numbered script and Jupyter Notebooks. They will:
1. aggregate the data into one JSON file
2. perform a first cleaning pass
3. extend the dataset with the classification, for each sentence, of whether the speaker was writing while saying it (using the X-CLIP model for inference), further clean the data, and save 3 versions of the CSV files (standard, extended, and complete with all metadata)