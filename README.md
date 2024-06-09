# Automatic Video Lecture Summarization with Injection of Multimodal Information: Two Novel Datasets and a New Approach
**Enrico Castelli's Master's Thesis**  
  
![](https://img.shields.io/badge/Python-3.10.6-brightgreen) ![](https://img.shields.io/badge/License-GPLv3-orange) [![](https://img.shields.io/badge/PDF-Here-cyan)](http://webthesis.biblio.polito.it/id/eprint/26717)

### Abstract

With the growing diffusion of online courses with video lectures, both from universities such as PoliTo and from MOOC platforms, the ability to distill key information is becoming more and more quintessential to the life of a student. Video lectures provide their contents in a multimodal way, not only with the voice of the speaker, which can be transcribed, but also with visual information such as writings on a blackboard or projected slides. The aim of this work is to offer a new tool to learners and teachers that will allow them to supply one of the proposed models with the transcript of a video lecture and obtain its short summary in return in a fully automatic way. To train our Transformer-based models, we build two datasets from scratch: OpenULTD, a university lecture and public talk transcripts dataset, and UniSum, a transcript-summary dataset of university lectures from sixtyseven courses offered at MIT and Yale, which we also extend leveraging the lectures’ visual information.

### Thesis

Find the PDF on PoliTo's website: http://webthesis.biblio.polito.it/id/eprint/26717.

### Repository Description

This repository stores all the code needed to reproduce the work of this master's thesis. It is structured in the following way:
- the `datasets` directory contains the `OpenULTD` and `UniSum` directories, which are the two proposed datasets, and...
  - the `subsets` directory includes the 4 subsets used to obtain the datasets mentioned above (MIT OpenCourseWare, OpenHPI, VT-SSum, Yale)
- the `experiments` directory contains one directory per type of experiment:
  - `denoining-language-modeling` includes 2 Jupyter notebooks to continue BART's pretraining with its original pretraining objective with the data of OpenULTD
  - `summarization` includes a Jupyter notebook to finetune different variants of BART (i.e. original, with Longformer attention, with LSG attention) on UniSum standard and extended, and a notebook to test the resulting models on different UniSum splits

### Dependencies

We use Python 3.10.6 in a virtual environment with the dependencies available in `requirements.txt`. This includes a PyTorch version with CUDA, so make sure you have at least a couple of GBs of available disk space just for the Python libraries.  
To install:
1. `python3.10.6 -m venv venv`
2. `source venv/bin/activate`
3. `pip install -U pip`
4. `pip install -r requirements.txt`