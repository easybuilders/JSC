Before running `eb` to install MATLAB you need to

a) export the file installation key as EB_MATLAB_KEY, like the following example
export EB_MATLAB_KEY='00000-00000-00000-00000-00000-00000-00000-00000-00000-00000-00000-00000-00000-00000-00000-00000-00000-00000-00000-00000-00000-00000'

b) or export the absolute path to the license file as EB_MATLAB_LICFILE, like the following example
export EB_MATLAB_LICFILE=/home/matlab/matlab.lic

c) download the ISO installation file from MATHWORKS

d) unpack it with `7z x <iso-file>` and repack it again with `tar -czf matlab-2022a.tar.gz`

e) copy the packed matlab sources as 'matlab-2020b.tar.gz' to the working directory
