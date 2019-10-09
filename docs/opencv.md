Getting opencv installed in the virtual environment:

Ubuntu 18.04

run

`sudo apt update`

`sudo apt upgrade`

install the following system packages:
build-essential cmake unzip pkg-config
libjpeg-dev libpng-dev libtiff-dev
libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
libxvidcore-dev libx264-dev
libatlas-base-dev gfortran
python3-dev

download the desired release source:
https://github.com/opencv/opencv/releases
https://github.com/opencv/opencv_contrib/releases

unzip into a folder, rename folders if desired

go to the opencv folder
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE
    -D CMAKE_INSTALL_PREFIX=$VIRTUAL_ENV/local/ 
    -D PYTHON_EXECUTABLE=$VIRTUAL_ENV/bin/python 
    -D PYTHON_PACKAGES_PATH=$VIRTUAL_ENV/lib/python3.6/site-packages 
	-D INSTALL_PYTHON_EXAMPLES=OFF
	-D INSTALL_C_EXAMPLES=OFF
	-D BUILD_EXAMPLES=OFF
	-D OPENCV_ENABLE_NONFREE=OFF
	-D OPENCV_EXTRA_MODULES_PATH=../opencv_contrib/modules ..

(check that the paths work and are correct. relative paths were tested, so double dot syntax may not work)

make -j<N> (where <N> is number of processors, try `nproc`)
make install (may require `sudo`)
ldconfig (may require `sudo`)

References:
https://www.pyimagesearch.com/2018/05/28/ubuntu-18-04-how-to-install-opencv/
http://manuganji.github.io/deployment/install-opencv-numpy-scipy-virtualenv-ubuntu-server/