# Machine Learning Engineer Nanodegree
## Capstone Proposal
Rob Fitch 
April 1st, 2017

## Proposal
_(approx. 2-3 pages)_

### Domain Background
_(approx. 1-2 paragraphs)_

Micromouse competitions date back to the 1972, requiring the robots to explore a novel maze and plot a best path through it. These competitions narrow this problem field down to allow competitive focus on application of autonomous action planning. The robot must be able to evaluate its surroundings and plan a course of action that meets the current situations framework of restrictions.

These competitions encourage the development of methods for autonomous robots to handle novel situations encountered in the world. They also require the robot to compensate for flaws in hardware and the imperfect nature of real world applications. Solving these challenges allows robots to be deployed in a wider variety of situations, with less direct oversight. This has value in many aspects of society and industry.  


### Problem Statement
_(approx. 1 paragraph)_

This simulation will attempt to create an micromouse robot under ideal conditions. The robot will be required to explore a square maze of width 12 to 14. The robot will be assumed to be facing a cardinal direction and to occupy the center of the current cell. At each time step, it will be allowed to rotate 90 degree in either direction or continue straight. After each opportunity to turn, the robot may choose to move 1 to 3 cells forward. The robot will be permitted to explore and map the maze prior to a best path attempt. A penalty of 1/30th of the exploration time will be applied to the time for the best path attempt, encouraging efficient exploration.  


### Datasets and Inputs
_(approx. 2-3 paragraphs)_

At each time step of the simulation, the virtual robot will receive 3 numerical inputs approximating range sensors. The inputs indicate the distance to the nearest wall from the front, left and right sensors. To determine the correct inputs for each cell, encoded maze files will be used. The mazes are provided by Udacity and include 3 layouts, measuring 12, 14 and 16 cells respectively. These mazes are designed to challenge the pathfinding ability of the robot.  


### Solution Statement
_(approx. 1 paragraph)_

The robot will use a waterfall algorithm. It will track its location and inputs at each point in the maze, preventing a stuck condition if the maze contains an open loop. Once the robot reaches the goal, it will conduct a turn left first, depth-first search for the starting cell. I believe that these two searches, in concert with loop tracking will allow the robot to find a suitable path in a reasonable timeframe.  


### Benchmark Model
_(approximately 1-2 paragraphs)_

Dead reckoning with dead end learning will be used as the null hypothesis algorithm for this project. Dead reckoning models travel straight until reaching a fork or dead end, at which point the algorithm randomly selects an open path and continues. Dead end learning requires tracking every space in the maze and virtually closing off dead ends as they are discovered. The dead reckoning algorithm has minimal memory and processing requirements and will eventually reach the goal. With dead ends closed off as they are discovered, the speed run should be faster than the exploratory run. This algorithm will be simulated 100 times per maze to create a statistical benchmark.

### Evaluation Metrics
_(approx. 1-2 paragraphs)_

Each model will be simulated 100 times, for up to 1000 time steps per phase, on each available maze. The simulations will be scored by adding 1/30th of the time steps required for the first phase to the total time steps required for the second phase. First phase, second phase and final score statistics will be evaluated for statistical significance. This scoring system favors reliable and efficient algorithms over exhaustive and random algorithms.  

By tracking and reporting on the first phase, evaluation will be possible on exploration efficiency. Finding the center quickly will contribute significantly to the final result. The same statistics will report on exploration efficacy. Mapping the best route to the center will also contribute significantly to the final result, but may not be decisive if the exploration phase is inefficient. Finally, the scoring data combines these metrics to an overall algorithmic effectiveness metric. With all three metrics, lower values are preferred.  

### Project Design
_(approx. 1 page)_

In this final section, summarize a theoretical workflow for approaching a solution given the problem. Provide thorough discussion for what strategies you may consider employing, what analysis of the data might be required before being used, or which algorithms will be considered for your implementation. The workflow and discussion that you provide should align with the qualities of the previous sections. Additionally, you are encouraged to include small visualizations, pseudocode, or diagrams to aid in describing the project design, but it is not required. The discussion should clearly outline your intended workflow of the capstone project.

Experimental phases:
    Establish baseline performance
    Establish initial solution performance
    Tune solution to optimize performance

-----------

**Before submitting your proposal, ask yourself. . .**

- Does the proposal you have written follow a well-organized structure similar to that of the project template?
- Is each section (particularly **Solution Statement** and **Project Design**) written in a clear, concise and specific fashion? Are there any ambiguous terms or phrases that need clarification?
- Would the intended audience of your project be able to understand your proposal?
- Have you properly proofread your proposal to assure there are minimal grammatical and spelling mistakes?
- Are all the resources used for this project correctly cited and referenced?

                  12x12      14x14     16x16
Random_choice    313.333   Exceeded  Exceeded
Wall_follower    100.633    272.733   137.933
Basic_waterfall   53.433     63.567    79.933
Double_waterfall  37.067     58.333    59.433