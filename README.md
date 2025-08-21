# 🧩 Solving Persian Crosswords with NLP

This repository contains the core solver engine for the research project “Solving Persian Crosswords with Natural Language Processing Techniques” published in the 9th International Conference on Web Research (May 2023).

## Abstract

Crossword solving is divided into two subtasks:  

1. **Answer retrieval** – generating possible answers for each clue using a hybrid of NLP methods:
   - Semantic similarity search on previously solved crosswords  
   - Dictionary & Wikipedia lookup  
   - Masked language modeling  
   - FarsNet & Farsiyar related words  

2. **Constraint satisfaction** – selecting the correct answer from candidates by applying crossword grid constraints.

Evaluation achieved **82% recall** in candidate generation and an overall **80.22% precision / 68.86% recall** in full crossword solving.


## Features
- Hybrid NLP-based clue answering  
- Constraint-satisfaction puzzle filling  
- Interfaces for dictionary/Wikipedia/FarsNet/Farsiyar  
- Evaluation scripts with reported metrics  

## Results

- **82% recall** in candidate generation

- **80.22% precision** and **68.86% recall** in full solving

## Citation

If you use this project in your research, please cite:

```
Pakzadian, M., Shamsfard, M., Solving Persian Crosswords with Natural Language Processing Techniques,  Proceedings of the 9th International Conference on Web Research, 2023
```

## Publication

The project is based on the paper:

[Solving Persian Crosswords with Natural Language Processing Techniques](https://www.sid.ir/paper/1047251/fa), The 9th International Conference on Web Research · May 2023
