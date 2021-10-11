**Mars à avr. 2021 – C++, Python, DataStudio : optimisation de livraison de colis**
- Responsable technique et chef d’équipe d’un groupe international de 6 personnes.
- 4 cas d’usages (Travelling Salesman Problem, Vehicle Routing Problem, Package Delivery Routing Problem, Multiple Package Delivery Routing Problem), souplesse d’exécution (21+4n paramètres avec n le nombre d'algorithmes d'optimisations).
- Application multicouche : moteurs de génération et d'optimisation C++, wrapper Python et dashboard Data Studio.

<br><hr><br>

# M1_S2project_deliverySystemOptimization


## Prerequisites
The prerequisites for this project are:
- A Python interpreter between 3.7 and 3.9,
- A C ++ 11 or higher compiler,
- A Windows or Linux based OS which use apt dependency manager.


## Credentials
The user needs to follow listed steps to obtain Google Drive credentials: developers.google.com/workspace/guides/create-credentials.

Credentials needed:
- Google Sheets API v4
- Google Drive API v3


## Auto setup script
User can start a script automating about 90% of the project specific setup work in four steps:
1.	We start by installing the python dependencies listed in the requirements.txt file, via the pip package manager. Then, we download python libraries out of pip before installing them too.
There are then two scenarios:

    a.	For Linux users, we install a C ++ library via the apt package manager.

    b.	For Windows users, we download a port of this library, which we decompress. It will remain to add folder’s path to the Path environment variables list & restart the system.

2.	We then check the number of credentials files in the directory for access to the drive.

3.	After that, we compare the list of drawing countries files present on a site with that of the local directory and we download the zip archives of the missing countries. Once everything has been downloaded, we extract the required files and delete the archive.

4.	Finally, the script compiles the C++ files to ensure the user has working executables.

To avoid redoing a step, we create a witness file at the end of each step, except compilation. To allow dependency evolution, the dependency witness file is numbered. If you want re execute a step, delete the flag file in the setup folder.

The command to execute from the root folder is: python setup/init.py


## Launch execution
User need to prepare the execution in two steps, either in local (root folder) or in drive (with credentials access):
1. Fill the .data file with input data's,
2. Configure the incoming execution by copying and filling the .json file.

Then, the command to execute from the root folder is: python launcher/main.py < configName > < optionnal: true(default) | false >
The optional parameter specifies if the execution is online or not.


## Results
Results can be analyzed as shown here: https://datastudio.google.com/u/2/reporting/719e36c2-23e3-4697-8a94-30e2cb147167/

## Notes
- Multiprocessing for graph generation seems slower than multithreading (see process_for_graph branch)
- Img uploads are in parallel for better performances
- Optimizations are in parallel and not sequentials : one good update would be to create pipelines of optimizations
