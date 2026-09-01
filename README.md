# LLMike: Exploring Large Language Models' Abilities in Wheel of Fortune Riddles

This repository contains LLMike, the framework introduced in the paper "***LLMike: Exploring Large Language Models' Abilities in Wheel of Fortune Riddles***". It enables large language models to play the textual version of the game *Wheel of Fortune*, inspired by the famous TV show.

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Steps](#steps)
- [Usage](#usage)
- [License](#license)
- [Contact](#contact)
- [Citation](#citation)

## Overview
LLMike allows researchers to evaluate **Large Language Models** (LLMs) in a controlled setting by simulating the textual version of the Wheel of Fortune game. The repository provides all the code needed to connect different LLMs, a simple datasets of riddles, and one experiment configuration example. Users can reproduce the results reported in the paper, analyze model performance under varying conditions, and extend the framework for new tasks or custom experiments.


## Repository Structure
```
.
├── configs/            # Configurations folder
├── data/               # Dataset 
├── source/             # Python code of the experiments
├── execute.sh          # Script that executes all the configurations
├── environment.yml     # Conda environment specification
├── LICENSE             # License file
├── README.md           # This file 
└── stats.ipynb         # Python notebook for visualizing the results
```

## Installation

### Prerequisites
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/ejdisgjinika/LLMike.git
   cd LLMike
   ```

2. **Create the conda environment**
   ```bash
   conda env create -f environment.yml
   ```

3. **Activate the environment**
   ```bash
   conda activate llmike
   ```

4. **(Optional) Install additional packages**
   If you need extra packages, install them using:
   ```bash
   conda install <package_name>
   ```

## Usage

- To run all experiments as configured, use the `execute.sh` script:
  ```bash
  ./execute.sh
  ```

- The results are available in the `reports/` folder.
- The `stats.ipynb` file shows statistics extracted from the reports and a graph that helps visualize the overall performance of the analyzed models.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Citation

If you use **LLMike** or the associated dataset in your research, please cite our paper:

**[LLMike: Exploring Large Language Models' Abilities in Wheel of Fortune Riddles](https://aclanthology.org/2025.clicit-1.47/)**  
*Proceedings of the Eleventh Italian Conference on Computational Linguistics (CLiC-it 2025)*

```bibtex
@inproceedings{gjinika-etal-2025-llmike,
    title     = {{LLM}ike: Exploring Large Language Models'
                 Abilities in Wheel of Fortune Riddles},
    author    = {Gjinika, Ejdis and
                 Arici, Nicola and
                 Loreggia, Andrea and
                 Putelli, Luca and
                 Serina, Ivan and
                 Gerevini, Alfonso Emilio},
    editor    = {Bosco, Cristina and
                 Jezek, Elisabetta and
                 Polignano, Marco and
                 Sanguinetti, Manuela},
    booktitle = {Proceedings of the Eleventh Italian Conference on
                 Computational Linguistics (CLiC-it 2025)},
    year      = {2025},
    month     = sep,
    address   = {Cagliari, Italy},
    publisher = {CEUR Workshop Proceedings},
    pages     = {480--489},
    url       = {https://aclanthology.org/2025.clicit-1.47/},
    isbn      = {979-12-243-0587-3}
}
```

## Contact

For questions, contact [ejdis.gjinika@unibs.it](mailto:ejdis.gjinika@unibs.it).
