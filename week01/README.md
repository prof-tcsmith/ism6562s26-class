# Week 1 — Big Data for Business Applications

**ISM 6562 - Big Data for Business Applications**

## Topics

- The 5 V's of big data (Volume, Velocity, Variety, Veracity, Value)
- Business use cases for big data and data-driven decision making
- Introduction to the big data ecosystem
- Python concurrency and parallel processing as a first taste of distributed work

## What's in this folder

```
week01/
├── README.md                                 # this file
├── assignment/
│   └── ism6562-week01-assignment.html        # graded assignment
└── lab/
    ├── ism6562-week01-lab.ipynb              # Lab 1: Python Concurrency and Parallel Processing
    └── ism6562-week01-lab2.ipynb             # Lab 2: The Complexity of Parallelizing Tasks
```

## Lab notebooks

Both lab notebooks are standalone Python — no Docker container required. Open them in JupyterLab, VS Code, or any Jupyter-compatible environment and run the cells in order.

- **Lab 1** introduces Python's `multiprocessing` and `concurrent.futures` APIs to demonstrate the gap between sequential and parallel execution on a single machine.
- **Lab 2** explores the *complexity* of parallelizing real workloads — task granularity, communication overhead, and where the speedups stop coming. Sets up the motivation for distributed systems in the rest of the course.

## Assignment

Open `assignment/ism6562-week01-assignment.html` in your browser. Submit per the instructions on Canvas.

## Getting help

- Lecture slides and recorded discussion are on Canvas.
- For technical questions about the lab notebooks, post in the Week 1 discussion on Canvas or attend the extra-help session on Saturday.
