# MetaBioDetect

This folder contains the main GUI python script `MetaBioDetect.py`, and two folders: `scripts` and `resources`. 

`scripts` is mainly for building the docker container that is used within the app for performing metabarcoding analysis. (Refer to its README.md for more details)

`resources` holds the application scripts for its functionalities and features that are apart from the main GUI script as well as the docker image tar file generated following the steps in **src/scripts/README.md**

## App deployment (developer use)
First make sure the docker image is located in **src/resources**, refer to its README.md to set it up.

To depoly the app with new changes, naviagte to the directory where main GUI script `MetaBioDetect.py` resides and run the following:

`pyinstaller  MetaBioDetect.py --onefile --add-data="resources:resources"`

This command will generate two folder `build` and `dist`. The dist folder will have the applicaton excutable file that is ready to run with a double click :)