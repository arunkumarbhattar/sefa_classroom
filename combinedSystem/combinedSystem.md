# **Combined Grading System (Github/Brightspace interactions)**
_This article is incomplete. You can help by expanding it._
## _Abstract_
This section describes the system that governs the interactions between the _Github Classroom_ and the server. This includes pulling, running the grading script, tagging, committing, pushing, deleting the repos afterward, and other pertinent functions such as obtaining the information necessary to run these. These functions are all done by Python scripts that make use of OS and Unix commands/functions.

PAS has decided to make use of _Github Classroom_ to facilitate the user grading process (see **Github Classroom** section). This process involves the student supplying their homework submissions to a repository on _Github Classroom_, which is then pulled into the main server. The homework submissions are then processed by this system, graded individually by the actual grading system, and repositories are deleted off of the main server after the changes have applied to the Github and relevant areas of the server. 
## _Detailed Description of System as a Whole_

## _Description of Specific Functionality_

## _Github Classroom_
_Github Classroom_ is a free online service for educators created by Github to provide storage services that can be used for assignment submission. 

## _What are "Tags"?_
Tags are a specific marker used by Github on repositories that serve useful properties relevant to this part of the system. For instance, tags can provide the system with the time of a submission, and can be used to indicate that the repository has been graded. Of course, these tags can be customized to fit the user's purposes. 

One can read more on the specifics of tags on the official github documentation:
https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/managing-commits/managing-tags

or specific notes taken by Leila Yanni: https://github.com/PurdueCAM2Project/pas_githubclassroom/blob/combined/Notes%20on%20Tags.md
## _Github Commands Used and Their Descriptions_
## _Linux Commands Used and Their Descriptions_
## _Current Status of Functionality and What Needs to be Done_
The combined grading system has not been fully implemented. The Github interactions are mostly complete; however, they need to be tested to interact with the actual grading system itself. Interactions with Brightspace are not complete and fully implemented either.